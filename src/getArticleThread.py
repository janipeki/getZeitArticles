import threading
import checkURL

class GetArticleThread (threading.Thread):
    def __init__(self, storagedir, runtime, url, target, client):
        threading.Thread.__init__(self)
        self.url = url
        self.storagedir = storagedir
        self.runtime = runtime
        self.target = target
        self.client = client

    def run(self):
        print ("Starting download for " + self.url)
        article = download_article(self.storagedir, self.runtime, self.url, self.target)
        print ("Exiting download for " + self.url)
        return article

def download_article(storagedir, runtime, url, target):
#    if not url in open(storagedir + target + '.downloaded').read():
        print (url + ' to be downloaded at ' + str(runtime) )

        contents = url.split("/")[-1]
        output = storagedir + runtime + "_" + contents
        komplettansicht = url + "/komplettansicht"
        ret = checkURL.checkURL(komplettansicht)
        if ret == 200:
            print (url + "/komplettansicht" + ' found and will be downloaded')
            content = checkURL.downloadall(url + "/komplettansicht", output + ".komplettansicht.html")
            article_dict = {"article": url + "/komplettansicht", "content": content}
            return article_dict

        else:
            print (url + ' found and will be downloaded')
            content = checkURL.downloadall(url, output + ".html")
            article_dict = {"article": url + "/komplettansicht", "content": content}
            return article_dict
#    else:
#        print (url + ' not found')

