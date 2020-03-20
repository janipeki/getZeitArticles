import threading
import checkURL
import boto3

class GetArticleThread (threading.Thread):
   def __init__(self, tablename, storage, runtime, url, target):
      threading.Thread.__init__(self)
      self.url = url
      self.tablename = tablename
      self.storage = storage
      self.runtime = runtime
   def run(self):
      download_article(self.tablename, self.storage, self.runtime, self.url)

def download_article(tablename, storage, runtime, url):
        dynamoDBRes = boto3.resource('dynamodb')
        contents = url.split("/")[-1]
        output = storage + runtime + "_" + contents
        print (url + ' to be downloaded to ' + output)
        komplettansicht = url + "/komplettansicht"
        ret = checkURL.checkURL(komplettansicht)
        if ret == 200:
            print (url + "/komplettansicht" + ' found and will be downloaded')
            htmlfile = checkURL.downloadall(url + "/komplettansicht")
            response = dynamoDBRes.Table(tablename).put_item( Item={ 'article': url, 'data': htmlfile })
        else:
            print (url + ' found and will be downloaded')
            htmlfile = checkURL.downloadall(url)
            response = dynamoDBRes.Table(tablename).put_item( Item={ 'article': url, 'data': htmlfile })

