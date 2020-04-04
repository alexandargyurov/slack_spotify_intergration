from flask import Flask, session, redirect, url_for, request, jsonify
from multiprocessing import Process, current_process

from tekore import Spotify, Credentials, util, scope
from tekore.scope import scopes, every
from tekore.util import prompt_for_user_token, request_client_token, config_from_file
from tekore.sender import PersistentSender

import requests
import json
import webbrowser
import requests
import os
import time
import signal
import logging

import slack_app_views as SlackAppView

config = config_from_file("config.ini")
cred = Credentials(*config)
app_token = cred.request_client_token()

spotify = Spotify(token=app_token, sender=PersistentSender())

processes = []

# Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)
    

@app.route('/commands/home', methods=['POST'])
def commands_home():  
  slack_payload = json.loads(request.form.to_dict()['payload'])
  button_values = slack_payload['actions'][0]['value'].split(",")
  user_id = str(slack_payload['user']['id'])

  if button_values[0] == 'initialise':
    webbrowser.open("https://accounts.spotify.com/authorize?client_id=36cec683cc8d48cdbd51d0210d37bbf5&response_type=code&redirect_uri=http%3A%2F%2F77.98.167.224:4000%2Fspotify%2Fcallback&scope=user-read-playback-state&state=" + user_id)
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'disconnect_me':
    for process in processes:
      if str(process.name) == user_id:
        os.kill(process.pid, signal.SIGTERM)

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
        os.kill(process.pid, signal.SIGTERM)

    SlackAppView.update("disable_listen", slack_payload['user']['id'], button_values[1])
    return jsonify({"msg": "ok"}), 200

  else:
    logging.error(f"Something went wrong in commands_home, user: (#{user_id})")
    return jsonify({"error": "Something went wrong, please tell Alex G!"}), 500


@app.route('/kill', methods=['GET'])
def killall():
    pid = int(request.args.get('pid', ''))

    try:
      os.kill(pid, signal.SIGTERM)
      return jsonify({"error": "Process successfully stopped"}), 200
    except ProcessLookupError:
      return jsonify({"error": "No Process found with given PID"}), 500


@app.route('/subscriptions/events', methods=['POST'])
def main():
  slack_payload = request.json

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
  return redirect("https://slack.com/app_redirect?app=A010LFE0WKC", code=302)


def poll_spotify_current_song(spotify_token, user_id):
  while True:
    try:
      spotify_data = (requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": "Bearer " + str(spotify_token)})).json()

      name = spotify_data['item']['name']
      artist = spotify_data['item']['artists'][0]['name']

      payload = {
        "profile": {
            "status_text": f""""{name}" by {artist}""",
            "status_emoji": ":musical_note:",
            "status_expiration": 0
        }
      }

      slack_status(payload)
      time.sleep(15)

    except Exception:
      payload = {
        "profile": {
            "status_text": "",
            "status_emoji": ":musical_note:",
            "status_expiration": 1
        }
      }
      slack_status(payload)

      time.sleep(15)


def slack_status(payload):
  url = 'https://slack.com/api/users.profile.set'
  headers = {'Authorization': 'Bearer xoxp-29202147252-604304230050-1033309457056-76513a98207f487f8bbfab48422b7119', 'Content-Type': 'application/json'}
  requests.post(url, data=json.dumps(payload), headers=headers)


def remove_process(pid):
  if current_process() in processes: processes.remove(current_process())