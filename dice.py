import requests


import sys

def startGame(): # return factorial
    result = 1
    response=requests.get("http://api.open-notify.org/this-api-doesnt-exist")
    print("response is", response.status_code)
    return result
startGame()