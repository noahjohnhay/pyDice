import json
import requests
from functools import reduce
buttonCounter=1
def formatEmojiis(x1, x2): 
	return f'{x1} :die{x2}:'
def makeButtons(x1, x2):
	global buttonCounter
	obj={
		"text": {
		"type": "plain_text",
		"text": f':die{x2}:'
		},
		"value": f'value-{buttonCounter}'
	}
	buttonCounter+=1
	x1.append(obj)
	return x1

def sendDiceRoll(roll):
	params={
		"blocks": [
		{
			"type": "section",
			"block_id": "section678",
			"text": {
				"type": "mrkdwn",
				"text": "You Rolled: :die1: :die2: :die2: :die2: :die2: :die4:"
			},
			"accessory": {
				"action_id": "text1234",
				"type": "multi_static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Pick to keep"
				},
				"options": [
				]
			}
		}
	]}
	params["blocks"][0]["text"]["text"]=f'You rolled: {reduce(formatEmojiis, roll, "")}'
	params["blocks"][0]["accessory"]["options"]=reduce(makeButtons, roll, [])
	response=requests.post("https://hooks.slack.com/services/*", json=params)
	return response




sendDiceRoll([1,2,3,4,4,6])