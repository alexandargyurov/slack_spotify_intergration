import requests
import json

def update(content, user_id, code='none'):
    payload = {
        "default": default(user_id),
        "connected": connected_only(user_id, code),
        "enable_listen": connected_and_listening(user_id, code),
        "disable_listen": connected_only(user_id, code)
    }

    url = 'https://slack.com/api/views.publish'
    headers = {'Authorization': 'Bearer xoxb-29202147252-1035321106263-8eWkq5Z8liJt7wK1RdyJlTFN', 'Content-Type': 'application/json'}
    requests.post(url, data=json.dumps(payload[content]), headers=headers)

def default(user_id):
  return {
    "user_id": user_id,
    "view": { 
        "type":"home",
        "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hi there, welcome to the *Slack Spotify Bot*! I update your Slack status with the current song you're listening to so friends and colleagues can jam along."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Connect your Spotify account below to get started!"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Connect Spotify Account :musical_note:",
                                "emoji": True
                            },
                            "value": "initialise,none"
                        }
                    ]
                }
            ]
        }
    }

def connected_and_listening(user_id, code):
  return {
    "user_id": user_id,
    "view": { 
        "type":"home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi there, welcome to the *Slack Spotify Bot*! I update your Slack status with the current song you're listening to so friends and colleagues can jam along."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Spotify Connected*  :white_check_mark:"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Disconnect",
                        "emoji": True
                    },
                    "value": "disconnect_me"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " "
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Stop Auto-Status Update :x: ",
                        "emoji": True
                    },
                    "value": f"disable_listen,{code}"
                }
            }
          ]
        }
    }

def connected_only(user_id, code):
  return {
  "user_id": user_id,
  "view": { 
      "type":"home",
      "blocks": [
          {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": "Hi there, welcome to the *Slack Spotify Bot*! I update your Slack status with the current song you're listening to so friends and colleagues can jam along."
              }
          },
          {
              "type": "divider"
          },
          {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": "*Spotify Connected*  :white_check_mark:"
              },
              "accessory": {
                  "type": "button",
                  "text": {
                      "type": "plain_text",
                      "text": "Disconnect",
                      "emoji": True
                  },
                  "value": "disconnect_me"
              }
          },
          {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": " "
              },
              "accessory": {
                  "type": "button",
                  "text": {
                      "type": "plain_text",
                      "text": "Enable Auto-Status Update :musical_note: ",
                      "emoji": True
                  },
                  "value": f"enable_listen, {code}"
              }
          }
        ]
      }
  }