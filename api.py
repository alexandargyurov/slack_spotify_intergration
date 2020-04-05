from flask import Flask, session, redirect, url_for, request, jsonify
from multiprocessing import Process, current_process

from tekore import Spotify, Credentials, util, scope
from tekore.scope import scopes, every
from tekore.util import prompt_for_user_token, request_client_token, config
from tekore.sender import PersistentSender
from dotenv import load_dotenv

import requests
import json
import webbrowser
import os
import time
import signal
import logging
import subprocess

import slack_app_views as SlackAppView

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URL = os.getenv("SPOTIFY_REDIRECT_URL")
SLACK_APP_ID = os.getenv("SLACK_APP_ID")

cred = Credentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL)
app_token = cred.request_client_token()

spotify = Spotify(token=app_token, sender=PersistentSender())

processes = []

# Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run()
    
@app.route('/', methods=['GET'])
def home():
  return jsonify({"msg": "ok"}), 200

@app.route('/commands/home', methods=['POST'])
def commands_home():  
  slack_payload = json.loads(request.form.to_dict()['payload'])
  button_values = slack_payload['actions'][0]['value'].split(",")
  user_id = str(slack_payload['user']['id'])

  if button_values[0] == 'initialise':
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'disconnect_me':
    for process in processes:
      if str(process.name) == user_id:
        subprocess.call("kill -9 " + process.pid)

    print(processes)

    payload = {
      "profile": {
          "status_text": "",
          "status_emoji": "",
          "status_expiration": int(time.time())
      }
    }
    SlackAppView.update_slack_status(payload)

    SlackAppView.update("default", slack_payload['user']['id'])
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'enable_listen':
    for process in processes:
      if str(process.name) == user_id:
        logging.error(f"A process is already running with the current user id (#{user_id})")
        return jsonify({"error": "A process is already running with the current user id"}), 500

    process = Process(target=poll_spotify_current_song, args=(button_values[1].strip(), user_id), name=user_id)
    process.start()

    processes.append(process)  

    SlackAppView.update("enable_listen", slack_payload['user']['id'], button_values[1])
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'disable_listen':
    for process in processes:
      if str(process.name) == user_id:
        subprocess.call("kill -9 " + process.pid)
        logging.warn(f"SHOULD HAVE KILLED PROCESS {process.pid}")

    print(processes)

    payload = {
      "profile": {
          "status_text": "",
          "status_emoji": "",
          "status_expiration": int(time.time())
      }
    }
    SlackAppView.update_slack_status(payload)

    SlackAppView.update("disable_listen", slack_payload['user']['id'], button_values[1])
    return jsonify({"msg": "ok"}), 200

  else:
    logging.error(f"Something went wrong in commands_home, user: (#{user_id})")
    return jsonify({"error": "Something went wrong, please tell Alex G!"}), 500


@app.route('/kill', methods=['GET'])
def killall():
    pid = int(request.args.get('pid', ''))

    try:
      subprocess.call("kill -9 " + process.pid)
      return jsonify({"error": "Process successfully stopped"}), 200
    except ProcessLookupError:
      return jsonify({"error": "No Process found with given PID"}), 500


@app.route('/processess', methods=['GET'])
def show_processess():
    for process in processes:
      print(process)

    return jsonify({"msg": "ok"}), 200


@app.route('/subscriptions/events', methods=['POST'])
def slack_events():
  slack_payload = request.json

  print(slack_payload)
  try:
    slack_payload['event']['view']['blocks'][2]['accessory']['value']
    return jsonify({"msg": "ok"})
  except:
    SlackAppView.update("default", slack_payload['event']['user'])
    return jsonify({"msg": "ok"})


@app.route('/spotify/callback', methods=['GET'])
def login_callback():
  code = request.args.get('code', None)
  user_id = request.args.get('state', None)
  
  token = cred.request_user_token(code)

  SlackAppView.update("disable_listen", user_id, token)
  return redirect("https://slack.com/app_redirect?app=" + SLACK_APP_ID, code=302)


def poll_spotify_current_song(spotify_token, user_id):
  while True:
    try:
      spotify_data = (requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": "Bearer " + str(spotify_token)})).json()

      if spotify_data['is_playing'] == False:
        payload = {
          "profile": {
              "status_text": "",
              "status_emoji": "",
              "status_expiration": int(time.time())
          }
        }

        SlackAppView.update_slack_status(payload)
      else:
        name = spotify_data['item']['name']
        artist = spotify_data['item']['artists'][0]['name']

        payload = {
          "profile": {
              "status_text": f""""{name}" by {artist}""",
              "status_emoji": ":musical_note:",
              "status_expiration": 0
          }
        }

        SlackAppView.update_slack_status(payload)

      time.sleep(15)

    except Exception:
      payload = {
        "profile": {
            "status_text": "",
            "status_emoji": "",
            "status_expiration": int(time.time())
        }
      }

      SlackAppView.update_slack_status(payload)

      time.sleep(15)


def remove_process(pid):
  if current_process() in processes: processes.remove(current_process())