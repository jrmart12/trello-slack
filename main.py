from flask import request, redirect, abort, Flask, jsonify
from slack import WebClient
import http.client
import os
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_web_client = WebClient(token=os.environ['SLACK_API_KEY'])

def get_channel_name(channel_name):
        slack_channels = slack_web_client.conversations_list(types="private_channel, public_channel")
        channel_id = ""
        for channel in slack_channels['channels']:
            if(channel['name']==channel_name):
                channel_id = channel['id']   
        return channel_id

def message(cardName, comment):
    slack_channel_messages = slack_web_client.conversations_history(channel=get_channel_name(cardName),limit=1)
    x = comment.split("(")
    x_x =  x[0].strip()
    for channel_message in slack_channel_messages['messages']:
        if channel_message['text'] == x_x:
            slack_channel_replies = slack_web_client.conversations_replies(channel=get_channel_name(cardName),ts=channel_message["ts"])
            for channel_reply in slack_channel_replies['messages']:
                if channel_reply['text'] == x_x:
                    print("entro")
                    return None
    slack_web_client.chat_postMessage(channel="#"+cardName, text=comment)
    print(
        "A message was sent "
    )            

@app.route('/webhook', methods=['GET', 'POST']) 
def webhook():
    data = request.json
    if data["action"]["type"] == "commentCard":
        cardName = data["action"]["data"]["card"]["name"]
        comment = data["action"]["data"]["text"]
        message(cardName,comment)
        
    return jsonify(data)

if __name__ == '__main__':
    app.run()