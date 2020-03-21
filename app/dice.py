
from actions import actions

# gameId=actions.addPlayer("20db2f89-2746-43e7-b5d5-3b181e7f1498", "jon")
# gameId=actions.startGame("20db2f89-2746-43e7-b5d5-3b181e7f1498")
# print("Something here:", gameId)


import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', methods=['GET'])
def home():
    return actions.createGame()

app.run()