#!/usr/bin/python3

import urllib.request
import requests
from urllib.error import HTTPError

def checkURL(URL):
    try:
        ret = urllib.request.urlopen(URL).getcode()
    except HTTPError as err:
        ret = err.code
    return ret

def downloadall(url, outputfile):
    print (url + ' downloading to ' + outputfile)
    response = requests.get(url)
    if response.status_code == 200:
        output = open(outputfile, 'wb')
        output.write(response.content)
        output.close()
        return response.content
    else:
        return response.status_code
        
