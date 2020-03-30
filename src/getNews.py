#!/usr/bin/python3
# 
# 1. Extrahiere alle interessanten Links nach <url>.links
# 2. Vergleiche diese Liste mit der Liste der bereits heruntergeladenen Links: urls.loaded.
# 3. Wenn neu: Herunterladen und in Datei der Links speichern.

import sys
import os
import glob
from time import gmtime, strftime
import re
import datetime
from pathlib import Path
import boto3, botocore
from boto3.dynamodb.conditions import Key, Attr
import requests

import checkURL
import config
import getArticleThread

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
    
def safe_headline(tablename, runtime, url):
    table = boto3.resource('dynamodb').Table(tablename)
    
    response = table.put_item(
       Item={
            'article': url
        }
    )

def already_downloaded(table, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table)
    results = table.query(KeyConditionExpression = Key('article').eq(url))
    print("Count of downloads: " + str(results["ScannedCount"]) + " for url: " + url)
    return results["ScannedCount"]

# Get all articles if not already downloaded
def get_articles(all_urls, runtime, storage, bucket, target, s3res):
    urlList = []
    tablename = 'news'
    for url in all_urls:
        if url != '':
            if not already_downloaded(tablename, url):
                print ("Get article for:  " + url)
                newArticleThread = getArticleThread.GetArticleThread(storage, runtime, url, bucket, target, s3res)
                newArticleThread.start()
                safe_headline('news', runtime, url)
                urlList.append(url)
    return urlList

# Get the list of interesting news of the main page 
def get_news(completepage, revalid, reinvalid, filename, runtime, storage, bucket, target, s3res):


    # 1. Get links of news 
    if completepage is not None:
    
        alllinks = []
        with open(completepage) as completepage_file:
            for line in completepage_file:
                isUrl =  revalid.match(line)
                if isUrl:
                    isvalidUrl = reinvalid.search(isUrl.group(1))
                    if not isvalidUrl:
                        alllinks.append(isUrl.group(1))
        completepage_file.close()
    
        # 2. Get the articles of the links
        urlList = get_articles(alllinks, runtime, storage, bucket, target, s3res)
    
    return urlList

def sendMessageAboutNewsDownloaded(urlList, target):
    if urlList:
        sns = boto3.resource('sns') 
        topic = sns.Topic('arn:aws:sns:eu-central-1:800251320731:dynamodb')
    
        subject = " ".join(str(news) for news in urlList)
        print ('subject: ' + subject)
        response = topic.publish(
            Message='News: Urls downloaded for: ' + subject,
            Subject= 'New articles are available for ' + target
        )
    else:
        print("List of URLs is empty.")

# Only get the list of all previously downloaded articles
def s3_test_and_download_object(bucket, obj, storagedir, s3res):
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

#################### M A I N #################### 
def lambda_handler(event, context):
    # 1. Read configuration
    local_config = config.Config('./getnews.json')
    
    # 2. Initialize
    curdate = datetime.date.today().strftime('%Y') + '-' + datetime.date.today().strftime('%m') # Short time stamp as used in URL
    revalid = re.compile(eval(local_config.revalid))
    reinvalid = re.compile(eval(local_config.reinvalid))
    runtime = strftime("%Y.%m.%d_%H.%M.%S", gmtime())
    filename = local_config.storage + runtime
    s3res = boto3.resource('s3')

    account_no = boto3.client('sts').get_caller_identity().get('Account')
    bucket = local_config.target + '-' + account_no
    
    # 4. Get news page ...
    completepage = download_webpage(local_config.url, filename + ".actual")

    # 5. ... and news
    urlList = get_news(completepage, revalid, reinvalid, filename, runtime, local_config.storage, bucket, local_config.target, s3res)

    sendMessageAboutNewsDownloaded(urlList, local_config.target)
    
    return urlList
