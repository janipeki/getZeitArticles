import threading

class GetArticleThread (threading.Thread):
   def __init__(self, storagedir, runtime, url, bucket, target, s3res):
      threading.Thread.__init__(self)
      self.name = url
      self.storagedir = storagedir
      self.runtime = runtime
      self.bucket = bucket
      self.target = target
      self.s3res = s3res
   def run(self):
      print ("Starting download for " + self.name)
      download_article(self.storagedir, self.runtime, self.url, self.bucket, self.target, self.s3res)
      print ("Exiting download for " + self.name)

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

