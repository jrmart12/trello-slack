# Trello-Slack

This tool will check the trello api once every ten seconds for new comments and send a message with the content into the channel which has the same name as the card. This also checks every boards and card in your trello.

## Requirements
- Python 3
- `py-trello`
- `slackclient`
- `flask`

## Usage
- `python main.py`.