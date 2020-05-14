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
        article, long = download_article(self.storagedir, self.runtime, self.url, self.target)
        print ("Exiting download for " + self.url)
        return article, long

def download_article(storagedir, runtime, url, target):
#    if not url in open(storagedir + target + '.downloaded').read():
        print (url + ' to be downloaded at ' + str(runtime) )

        contents = url.split("/")[-1]
        output = storagedir + runtime + "_" + contents
        komplettansicht = url + "/komplettansicht"
        ret = checkURL.checkURL(komplettansicht)
        if ret == 200:
            print ('download_article: ' + komplettansicht + ' found and will be downloaded')
            content = checkURL.downloadall(komplettansicht, output + ".komplettansicht.html", False)
            article_dict = {"article": url, "content": content}
            return article_dict, True

        else:
            print ('download_article: ' + url + ' found and will be downloaded')
            content = checkURL.downloadall(url, output + ".html", False)
            article_dict = {"article": url, "content": content}
            return article_dict, False
#    else:
#        print (url + ' not found')

