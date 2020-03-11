#!/usr/bin/python3

from datetime import datetime
import urllib.request
import requests
import socket
from urllib.error import HTTPError

def checkURL(URL):
    # First try if internet is connected
#     try:
#         socket.create_connection((URL, 80))
#         print (URL + " is reachable")
#         return True
#     except OSError:
#         print (URL + " is not reachable: " + str(OSError))
#         return False

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
    else:
        print(url + " not found")
