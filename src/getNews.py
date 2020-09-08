#!/usr/bin/python3
# 
# 1. Extrahiere alle interessanten Links nach <url>.links
# 2. Vergleiche diese Liste mit der Liste der bereits heruntergeladenen Links: urls.loaded.
# 3. Wenn neu: Herunterladen und in Datei der Links speichern.
import sys
import os
from time import gmtime, strftime, time
import re
import datetime
from pathlib import Path
import pymongo

import checkURL
import config
import getArticleThread

ticks = int(time())

def download_webpage(url, targetfile):
    print ('download_webpage: ' + targetfile)
    # Check if web page is available
    if not checkURL.checkURL(url) == 200:
        print (url + " is not reachable")
        sys.exit(504)
        return None
    else:
        # Download the web page
#         print (url + " is reachable")
        checkURL.downloadall(url, targetfile, True)
        return targetfile
    
def already_downloaded(newsCollection, url ):
    urlquery = { "article": url }
    articleCount = newsCollection.count_documents(urlquery)
#     print ('articleCount for ', url, ': ', articleCount)

    if articleCount == 0:
        urlquery = { "article": url + "/komplettansicht" }
        articleCount = newsCollection.count_documents(urlquery)
#         print ('articleCount for ', url + "/komplettansicht" , ': ', articleCount)

    if articleCount > 1: print("Count of downloads: " + str(articleCount) + " for url: " + url)
    return articleCount

# Get all articles if not already downloaded
def get_articles(all_urls, runtime, storage, target, newscol):
    urlList = []
    tablename = 'news'
    for url in all_urls:
        if url != '':
            if not already_downloaded(newscol, url):
                print ("Get article for:  " + url)
                article_contents, longFormat = getArticleThread.download_article(storage, runtime, url, target)
                article_contents.update({'foundFirst': ticks})
                article_contents.update({'foundLast': 0})
                article_contents.update({'foundPeriod': 0})
                article_contents.update({'longFormat': longFormat})

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
    
    return urlList, alllinks

def finalizeOldArticles(newscol, urlList):
    # Get the epoch of the last update.
    lastTimeStamp  = newscol.find({"foundFirst":{'$gt':0}},{'foundFirst': 1, '_id': 0})
    lastupdtime = []
    for i in lastTimeStamp:
        lastupdtime.append(i['foundFirst'])
    lastupdtimestamp = max(lastupdtime)

    # Get list of articles that were earlier still found on the webpage and thus not finalized in mongodb:
    unfinalizedArticles = newscol.find({"foundLast":{'$eq':0}},{'article': 1, '_id': 0})
    unfArtlist = []
    for unfinalized in unfinalizedArticles:
        unfArtlist.append(unfinalized['article'])

    # Check if unfinalized articles are still found in the newest version of the webpage:
    for article in unfArtlist:
        # If article is not found then set the finalized time stamp:
        foundFirst = 0
        _id = 0
        content = ''
        foundFirst = 0
        foundLast = 0
        if article.endswith('/komplettansicht'):
                article = article[:-16]
        if not ((article in urlList) or ( article + '/komplettansicht' in urlList)):
#             print('finalizing unfinalizedArticle: finalize', article) 
            articleCursor = newscol.find({"article":{'$eq':article}})
            for fields in articleCursor:
                for key, value in fields.items():
                    if key == '_id':
                        _id = value
                    elif key == 'content':
                        content = value
                    elif key == 'foundFirst':
                        foundFirst = value
            foundPeriod = lastupdtimestamp - foundFirst
            print ('With values:', _id, article, foundFirst, foundPeriod, lastupdtimestamp)
            newscol.replace_one({'_id': _id }, {'foundFirst': foundFirst, 'article':article, 'content': content, 'foundLast': lastupdtimestamp, 'foundPeriod': foundPeriod})


#################### M A I N #################### 
def main():
    # 1. Read configuration
    local_config = config.Config('./getnews.json')
    
    # 2. Initialize
    curdate = datetime.date.today().strftime('%Y') + '-' + datetime.date.today().strftime('%m') # Short time stamp as used in URL
 #   print (str(curdate))
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
    urlList, alllinks = get_news(completepage, revalid, reinvalid, filename, runtime, local_config.storage, local_config.target, newscol)
    finalizeOldArticles(newscol, alllinks)
    return urlList

main()
