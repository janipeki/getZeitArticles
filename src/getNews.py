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
import pymongo
import requests

import checkURL
import config
import getArticleThread

def download_webpage(url, targetfile):
    print ('download_webpage: ' + targetfile)
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
    
def already_downloaded(newsCollection, url ):
    urlquery = { "article": url }
    articleCount = newsCollection.count_documents(urlquery)

    if articleCount == 0:
        urlquery = { "article": url + "/komplettansicht" }
        articleCount = newsCollection.count_documents(urlquery)

    print("Count of downloads: " + str(articleCount) + " for url: " + url)
    return articleCount

# Get all articles if not already downloaded
def get_articles(all_urls, runtime, storage, target, newscol):
    urlList = []
    tablename = 'news'
    for url in all_urls:
        if url != '':
            if not already_downloaded(newscol, url):
                print ("Get article for:  " + url)
                article_contents = getArticleThread.download_article(storage, runtime, url, target)

                # Store the article in MongoDB:
                inserted = newscol.insert_one(article_contents)
                urlList.append(url)
    return urlList

# Get the list of interesting news of the main page 
def get_news(completepage, revalid, reinvalid, filename, runtime, storage, target, newscol):

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
        urlList = get_articles(alllinks, runtime, storage, target, newscol)
    
    return urlList

#################### M A I N #################### 
def main():
    # 1. Read configuration
    local_config = config.Config('./getnews.json')
    
    # 2. Initialize
    curdate = datetime.date.today().strftime('%Y') + '-' + datetime.date.today().strftime('%m') # Short time stamp as used in URL
    print (str(curdate))
    revalid = re.compile(eval(local_config.revalid))
    reinvalid = re.compile(eval(local_config.reinvalid))
    runtime = strftime("%Y.%m.%d_%H.%M.%S", gmtime())
    filename = local_config.storage + runtime
    if not os.path.exists(filename):
            os.makedirs(filename)
    mongoclient = pymongo.MongoClient("mongodb://192.168.178.48:27017/")
    mongodb = mongoclient["news"]
    newscol = mongodb["zeit"]
    dblist = mongoclient.list_database_names()
    if "news" in dblist:
          print("The database exists.")
    else:
          print("The database not exists.")

    
    # 4. Get news page ...
    completepage = download_webpage(local_config.url, filename + ".actual")

    # 5. ... and news
    urlList = get_news(completepage, revalid, reinvalid, filename, runtime, local_config.storage, local_config.target, newscol)

    return urlList

main()
