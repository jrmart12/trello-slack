import requests
import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from slack import WebClient
from trello import Board, Card, TrelloClient
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

CHECK_INTERVAL_SECONDS = 5
TRELLO_API_KEY = os.environ.get('TRELLO_API_KEY')
TRELLO_API_SECRET = os.environ.get('TRELLO_API_SECRET')
SLACK_API_KEY = os.environ.get('SLACK_API_KEY')
last_comment = ""
HOOKS = [
    {
        "trello_boards": "ALL_STARRED",
        "list_name": "ANY",
        "triggers": "commentCard",
        "slack_message": {
            "type": "direct",
            "recipient": "CARD_ASSIGNMENT",
            "message": " %content%",
        },
    },
]

class TrelloApi:
    def __init__(self):
        self.client = TrelloClient(
        api_key=TRELLO_API_KEY, api_secret=TRELLO_API_SECRET
    )          

    def get_boards(self):
        return self.client.list_boards()

    def fetch_cards(self, triggers, board, target_list, since):
        result = set()
        cards = board.fetch_actions(triggers, since=since)
        for card_data in cards:
            list_name = (
                card_data["data"]["listAfter"]["name"]
                if "listAfter" in card_data["data"]
                else card_data["data"]["list"]["name"]
            )
            card = Card(board, card_data["data"]["card"]["id"])
            card.fetch(eager=False)
            if card_data["type"] == "commentCard":
                card.card_action = "commented"
                card.comment = card_data["data"]["text"]
            result.add(card) 
        return result

class SlackApi:
    def __init__(self):
        self.client = WebClient(token=SLACK_API_KEY)

    def send_message(self, card, slack_message):
        """Notifies a channel about a new comment via Slack message"""
        message_text = slack_message["message"]
        message_text = message_text.replace("%content%", card.comment)
        self.client.chat_postMessage(channel="#"+card.name, text=message_text)
        print(
            "A message was sent "
        )

class Hook:
    def __init__(self, hook):
        self.last_check = datetime.utcnow().replace(microsecond=0).isoformat()
        self.trello_boards = hook["trello_boards"]
        self.list_name = hook["list_name"]
        self.triggers = [x.strip() for x in hook["triggers"].split(",")]
        self.slack_message = hook["slack_message"]
        self.executor = ThreadPoolExecutor()

    def execute(self, trello_api, slack_api, boards):
        try:
            if self.trello_boards == "ALL_STARRED":
                boards = boards
            else:
                boards = [
                    Board(client=trello_api.client, board_id=x.strip())
                    for x in self.trello_boards.split(",")
                ]
            futures = []
            for board in boards:
                futures.append(
                    self.executor.submit(
                        trello_api.fetch_cards,
                        self.triggers,
                        board,
                        self.list_name,
                        f"{self.last_check}Z",
                    )
                )
            for future in as_completed(futures):
                cards = future.result()
                for card in cards:
                    slack_api.send_message(card, self.slack_message)
            self.last_check = datetime.utcnow().replace(microsecond=0).isoformat()
        except Exception:
            traceback.print_exc()



def main():

    trello_api = TrelloApi()
    slack_api = SlackApi()

    hooks = [Hook(x) for x in HOOKS]
    any_starred = any(x.trello_boards == "ALL_STARRED" for x in hooks)
    executor = ThreadPoolExecutor()
    while True:
        try:
            boards = None
            if any_starred:
                boards = trello_api.get_boards()
            futures = []
            for hook in hooks:
                futures.append(
                    executor.submit(hook.execute, trello_api, slack_api, boards)
                )
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            os._exit(0)
        except Exception:
            traceback.print_exc()
        finally:
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()