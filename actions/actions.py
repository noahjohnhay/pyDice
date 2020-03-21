import json
import requests

def startGame(): # return factorial
    response=requests.post("http://dice.calinfraser.com/games")
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body


def fetchGame(): # return factorial
    response=requests.get("http://dice.calinfraser.com/games/20db2f89-2746-43e7-b5d5-3b181e7f1498")
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body