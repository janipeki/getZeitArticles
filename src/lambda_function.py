#!/usr/bin/python3
# 
# 1. Extrahiere alle interessanten Links nach <url>.links
# 2. Vergleiche diese Liste mit der Liste der bereits heruntergeladenen Links: urls.loaded.
# 3. Wenn neu: Herunterladen und in Datei der Links speichern.

import sys
import checkURL
import os
import glob
from time import gmtime, strftime
import re
import datetime
import json
from pathlib import Path
import boto3, botocore

# Get the latest file of a distinct type in a directory
def get_latest_file(path, *paths):
    """Returns the name of the latest (most recent) file of the joined path(s)"""
    fullpath = os.path.join(path, *paths)
    print ("Checking: " + fullpath)
    list_of_files = glob.glob(fullpath)  # You may use iglob in Python3
    if not list_of_files:                # I prefer using the negation
        print ("No file found")
        return None                      # because it behaves like a shortcut
    latest_file = max(list_of_files, key=os.path.getctime)
    _, filename = os.path.split(latest_file)
    print ("Latest file: " + filename)
    return filename

# Read json file
def python_json_file_to_dict(file_path):
    try:
        # Get json file 
        file_object = open(file_path, 'r')
        # Load JSON file data to a python dict object.
        dict_object = json.load(file_object)

        return dict_object
    except FileNotFoundError:
        print(file_path + " not found. ") 
        return None                     

# Read my own configuration 
def read_config(config_file):
    config = python_json_file_to_dict(config_file)
    url = config.get('url')
    target = config.get('target')
    revalid = config.get('revalid')
    reinvalid = config.get('reinvalid')
    storagetype = config.get('storagetype')
    storage = config.get('storage')
    return config, url, target, revalid, reinvalid, storagetype, storage

def download_webpage(url, targetfile):
    # Check if web page is available
    if not checkURL.checkURL(url) == 200:
        print (url + " is not reachable")
        sys.exit(504)
        return None
    else:
        # Download the web page
        print (url + " is reachable")
        checkURL.downloadall(url, targetfile)
        return targetfile
    
# Save the links of new articles in <news>.downloaded file
def save_differences(links, output_filename, timestamp):
    if links:
        linkfile = open(output_filename, "a")
        for line in links:
            print (line + " saved to " + output_filename)
            linkfile.write(timestamp + ";" + line)
        linkfile.close()
    else:
        print ("No links to save to " + output_filename)
        return None                      


# Get all articles if not already downloaded
def get_articles(all_urls, runtime, storagedir, bucket, target, s3res):
    for url in all_urls:
        if not url in open(storagedir + target + '.downloaded').read():
            download_article(storagedir, runtime, url, bucket, target, s3res)
            downloaded = open(storagedir + target + ".downloaded", "a")
            downloaded.write(runtime + ";" + url + '\n')
            downloaded.close()

# Get a single article with all pages (if more than one page is provided)
def download_article(storagedir, runtime, url, bucket, target, s3res):
    if not url in open(storagedir + target + '.downloaded').read():
        print (url + ' to be downloaded')
        contents = url.split("/")[-1]
        output = storagedir + runtime + "_" + contents
        komplettansicht = url + "/komplettansicht"
        ret = checkURL.checkURL(komplettansicht)
        if ret == 200:
            print (url + "/komplettansicht" + ' found and will be downloaded')
            checkURL.downloadall(url + "/komplettansicht", output + ".komplettansicht.html")
            s3res.meta.client.upload_file(output + ".komplettansicht.html", bucket, target + '/' + contents + '.komplettansicht.html')
        else:
            print (url + ' found and will be downloaded')
            checkURL.downloadall(url, output + ".html")
            s3res.meta.client.upload_file(output + ".html", bucket, target + '/' + contents + '.html')
    else:
        print (url + ' not found')

def create_bucket(bucket_name):
    region = 'eu-central-1'
    try:
        s3_client = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# Only get the list of all previously downloaded articles
def s3_test_and_download_object(bucket, obj, storagedir):
    s3res = boto3.resource('s3')
    s3client = boto3.client('s3')
    print ('Trying to get ' + bucket + ' and object: ' + obj + ' to ' + storagedir + obj)
    try:
        s3res.Object(bucket, obj).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            print (bucket + ' not found')
            return (404)
        else:
            # Something else as gone wrong.
            print('Something else has gone wrong when trying to create object: ' + obj + ' in bucket: ' + bucket)
            return (500)
    else:
        print(obj + ' found, downloading')
        s3client.download_file(bucket, obj, storagedir + obj)
        return (0)
    
# Get the list of interesting news of the main page 
def get_news(completepage, revalid, reinvalid, filename, runtime, storagedir, bucket, target, s3res):

    # 1. Get links of news 
    if completepage is not None:
    
        with open(completepage) as completepage_file:
            alllinksfile = open(filename + ".links", "w")
            for line in completepage_file:
                isUrl =  revalid.match(line)
                if isUrl:
                    isvalidUrl = reinvalid.search(isUrl.group(1))
                    if not isvalidUrl:
                        alllinksfile.write (isUrl.group(1) + ";" )
            alllinksfile.close()
        completepage_file.close()
    
        # 2. Get the articles of the links
        alllinks = open(filename + ".links").read().split(';')
        get_articles(alllinks, runtime, storagedir, bucket, target, s3res)
    
        # 3. Save list of downloaded news to AWS / S3
        s3res.meta.client.upload_file(storagedir + target + ".downloaded", bucket, target + '.downloaded')

#################### M A I N #################### 
def lambda_handler(event, context):
    # 1. Read configuration
    config, url, target, revalid, reinvalid, storagetype, storage = read_config("getnews.json")
    
    # 2. Initialize
    curdate = datetime.date.today().strftime('%Y') + '-' + datetime.date.today().strftime('%m') # Short time stamp as used in URL
    revalid = re.compile(eval(revalid))
    reinvalid = re.compile(eval(reinvalid))
    runtime = strftime("%Y.%m.%d_%H.%M.%S", gmtime())
    filename = storage + runtime
    if not os.path.exists(storage):
        os.makedirs(storage)
    
    # 2.1 Init_s3_test_and_download_object AWS
    accountNo = boto3.client('sts').get_caller_identity().get('Account')
    if [ storagetype == "s3" ]:
        bucket = target + '-' + accountNo
        print ('bucket: ' + bucket)
        s3 = boto3.client('s3')
        s3res = boto3.resource('s3')
    #     if [ not s3.head_bucket( Bucket = bucket ) ]:   Assuming that the bucket exists
    #         create_bucket(target + '-accountNo')
        if [ s3_test_and_download_object(bucket, target + '.downloaded', storage) ]:
            print (target + '.downloaded could be downloaded')
        else:
            print (target + '.downloaded not found')
            sys.exit(1)
    
    # 4. Get news page
    completepage = download_webpage(url, filename + ".actual")
    # 5. Get news
    get_news(completepage, revalid, reinvalid, filename, runtime, storage, bucket, target, s3res)
