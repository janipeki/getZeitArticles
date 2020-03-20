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

def downloadall(url):
    print (url + ' downloading')
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return response.status_code
        
