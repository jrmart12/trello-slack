# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json


url = "https://api.trello.com/1/webhooks/"

headers = {
   "Accept": "application/json"
}

query = {
   'key': 'ee7b8c0523388294d89c0ba192fa5041',
   'token': '3b6f7d9698ce9552ce5c1ecd9d78617af4388d1581939b967b9a4301adf1d5b5',
   'callbackURL': 'https://trello-slack-codex.herokuapp.com/webhook',
   'idModel': '5ffcc56fdb5424207a7cf9f9'
}

response = requests.request(
   "POST",
   url,
   headers=headers,
   params=query
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
