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
import time
import json
from pathlib import Path

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

def read_config(config_file):
    config = python_json_file_to_dict(config_file)
    workdir = config.get('workdir')
    url = config.get('url')
    target = config.get('target')
    revalid = config.get('revalid')
    reinvalid = config.get('reinvalid')
    storage = config.get('storage')
    return config, workdir, url, target, revalid, reinvalid, storage

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


def download_article(workdir, runtime, url):
    if not url in open(workdir + target + '.downloaded').read():
        print (url + ' to be downloaded')
        output = workdir + runtime + "_" + url.split("/")[-1]
        komplettansicht = url + "/komplettansicht"
        ret = checkURL.checkURL(komplettansicht)
        if ret == 200:
            print (url + "/komplettansicht" + ' found and will be downloaded')
            checkURL.downloadall(url + "/komplettansicht", output + ".komplettansicht.html")
        else:
            print (url + ' found and will be downloaded')
            checkURL.downloadall(url, output + ".html")
    else:
        print (url + ' not found')

def get_articles(all_urls, runtime, workdir, target):
    for url in all_urls:
        if not url in open(workdir + target + '.downloaded').read():
            download_article(workdir, runtime, url)
            downloaded = open(workdir + target + ".downloaded", "a")
            downloaded.write(runtime + ";" + url + '\n')
            downloaded.close()

#################### M A I N #################### 

# 0. Get web site indicator
if len(sys.argv) == 2:
    website = sys.argv[1]
else:
    print ("Give web site indicator as only argument")
    sys.exit(1)

# 1. Read configuration
config, workdir, url, target, revalid, reinvalid, storage = read_config(website + ".json")

# 2. Initialize
curdate = datetime.date.today().strftime('%Y') + '-' + datetime.date.today().strftime('%m') # Short time stamp as used in URL
revalid = re.compile(eval(revalid))
reinvalid = re.compile(eval(reinvalid))
runtime = strftime("%Y.%m.%d_%H.%M.%S", gmtime())
filename = workdir + runtime

# 4. Get the page
completepage = download_webpage(url, filename + ".actual")
if completepage is not None:

    # 5. Get all interesting links from web page
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

    # 7. Get the articles
    alllinks = open(filename + ".links").read().split(';')
    get_articles(alllinks, runtime, workdir, target)

