from flask import request, redirect, abort, Flask, jsonify
from slack import WebClient
import http.client
import os

app = Flask(__name__)
SLACK_API_KEY = os.environ.get('SLACK_API_KEY')
class SlackApi:
    def __init__(self):
        self.client = WebClient(token=SLACK_API_KEY)

    def send_message(self, card, slack_message):
        """Notifies a channel about a new comment via Slack message"""
        self.client.chat_postMessage(channel="#"+card, text=slack_message)
        print(
            "A message was sent "
        )

@app.route('/webhook', methods=['GET', 'POST']) 
def webhook():
    data = request.json
    return jsonify(data)

if __name__ == '__main__':
    app.run()