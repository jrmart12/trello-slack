from flask import request, redirect, abort, Flask, jsonify
from slack import WebClient
import http.client
import os
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
SLACK_API_KEY = os.environ.get('SLACK_API_KEY')
slack_web_client = WebClient(token=os.environ['SLACK_API_KEY'])
class SlackApi:
    def __init__(self):
        self.client = WebClient(token=SLACK_API_KEY)

    def message(self, cardName, comment):
        slack_channel_messages = slack_web_client.conversations_history(channel=cardName)
        for channel_message in slack_channel_messages['messages']:
            if(channel_message['text'] != comment):
                self.client.chat_postMessage(channel="#"+cardName, text=comment)
                print(
                    "A message was sent "
                )                

@app.route('/webhook', methods=['GET', 'POST']) 
def webhook():
    data = request.json
    if data["action"]["type"] == "commentCard":
        slack_api = SlackApi()
        cardName = data["action"]["data"]["card"]["name"]
        comment = data["action"]["data"]["text"]
        slack_api.message(cardName,comment)
        
    return jsonify(data)

if __name__ == '__main__':
    app.run()