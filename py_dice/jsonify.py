import json

input_dict = {'message': 'You Busted!', 'roll': [6, 4, 2], 'game-state': {'game-id': '0c41ea4a-f670-4b65-9377-34195947d419', 'players': [{'name': 'noahjohnhay', 'turn-order': 0, 'points': 0, 'turn-seq': 0, 'pending-points': 0, 'ice-broken?': False, 'roll-vec': []}, {'name': 'jonathan.armel.daigle', 'turn-order': 1, 'points': 0, 'turn-seq': 0, 'pending-points': 0, 'ice-broken?': False}], 'friendly-name': 'abusivenesses melodies', 'turn': 1, 'state': 'started', 'pending-points': 0, 'pending-dice': 6, 'turn-player': 'jonathan.armel.daigle'}}


print(json.dumps(input_dict, indent=2))

player = input_dict["game-state"]["turn-player"]

print(player)