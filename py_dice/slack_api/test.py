import os
import slack

slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)

response = client.chat_postEphemeral(
    channel='C0107KZFHEV',
    text="Hello world!",
    user="UC5LD8QTA",
    thread_ts="1585417571.003200"

)

