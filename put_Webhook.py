# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
import os

url = "https://api.trello.com/1/webhooks/"

headers = {
   "Accept": "application/json"
}

query = {
   'key': os.environ.get('TRELLO_API_KEY'),
   'token': os.environ.get('TRELLO_API_SECRET'),
   'callbackURL': 'https://trello-slack-codex.herokuapp.com/webhook',
   'idModel': os.environ.get('TRELLO_BOARD__id')
}

response = requests.request(
   "POST",
   url,
   headers=headers,
   params=query
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
