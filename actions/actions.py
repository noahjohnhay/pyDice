import json
import requests

def createGame():
    response=requests.post("http://dice.calinfraser.com/games")
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body

def fetchGame(gameId):
    response=requests.get("http://dice.calinfraser.com/games/"+gameId)
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body

def startGame(gameId):
    response=requests.put("http://dice.calinfraser.com/games/"+gameId+"/start")
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body

def addPlayer(gameId, name):
    response=requests.post("http://dice.calinfraser.com/games/"+gameId+"/players", json={'name': name})
    body=json.loads(response.content)
    print("response is:", response.status_code, ":",  body)
    return body["player-id"]

