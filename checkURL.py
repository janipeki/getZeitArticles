#!/usr/bin/python3

from datetime import datetime
import urllib.request
import requests
from urllib.error import HTTPError

def checkURL(URL):
    try:
        ret = urllib.request.urlopen(URL).getcode()
    except HTTPError as err:
        ret = err.code
    
    return ret

def downloadall():
    response = requests.get('http://www.zeit.de/index')
    if response.status_code == 200:
        now = datetime.now()
        date = now.strftime("%Y.%m.%d_%H.%M.%S")
        file object = open(date + ".actual")
        file.write(response.content)
        file.close()
    else
        print("zeit not found")
