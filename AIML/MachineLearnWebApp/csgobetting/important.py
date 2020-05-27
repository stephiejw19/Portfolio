import json
import sys
import urllib.request
from html import unescape

def get_joke():
    url = 'http://api.icndb.com/jokes/random/'

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())

    return(unescape(result['value']['joke']))