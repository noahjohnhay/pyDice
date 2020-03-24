import json
from flask import Flask, request
from slack import producers

# gameId=actions.addPlayer("20db2f89-2746-43e7-b5d5-3b181e7f1498", "jon")
# gameId=actions.startGame("20db2f89-2746-43e7-b5d5-3b181e7f1498")
# print("Something here:", gameId)


'''
{
   "token":"*",
   "team_id":"TC58SJX1P",
   "team_domain":"beefers",
   "channel_id":"C0107KZFHEV",
   "channel_name":"spammyshit",
   "user_id":"ddfd",
   "user_name":"jonathan.armel.daigle",
   "command":"/roll",
   "text":"",
   "response_url":"https://hooks.slack.com/commands/*",
   "trigger_id":""
}
'''

flask_app = Flask(__name__)
flask_app.config["DEBUG"] = True


@flask_app.route('/roll', methods=['GET', 'POST', "PUT"])
def roll_route():
    print(json.dumps(request.form))
    producers.respond_slash_command(request.form, request.form["user_name"])

    return "Logged."


@flask_app.route('/pick', methods=['GET', 'POST', "PUT"])
def pick_route():
    print("")
    payload = json.loads(request.form["payload"])
    pick_list = payload["actions"][0]["selected_options"]
    print("")
    producers.send_picks(pick_list, payload["user"]["username"])
    return "Logged."


@flask_app.route('start', methods=["POST"])
def start_game():


    return


@flask_app.route('/picknose', methods=['GET', 'POST', "PUT"])
def pick_nose():
    conn
    return "nose was picked succesfully."


flask_app.run()
