from flask import Blueprint, request, redirect, jsonify
from multiprocessing import Process, current_process, Queue
from lib import queue, processes 

import time
import json
import os
import signal
import logging
import requests

import lib.slack.slack_api as SlackAPI

slack = Blueprint('slack', __name__)

@slack.route('/commands/home', methods=['POST'])
def commands_home():
  slack_payload = json.loads(request.form.to_dict()['payload'])
  button_values = slack_payload['actions'][0]['value'].split(",")
  user_id = str(slack_payload['user']['id'])

  if button_values[0] == 'initialise':
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'disconnect_me':
    for process in processes:
      if str(process.name) == user_id:
        os.kill(process.pid, signal.SIGKILL)
        remove_process(process.pid)

    payload = {
      "profile": {
          "status_text": "",
          "status_emoji": "",
          "status_expiration": int(time.time())
      }
    }
    SlackAPI.update_slack_status(payload)

    SlackAPI.update("default", slack_payload['user']['id'])
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'enable_listen':
    for process in processes:
      if str(process.name) == user_id:
        logging.error(f"A process is already running with the current user id (#{user_id})")
        return jsonify({"error": "A process is already running with the current user id"}), 500

    process = Process(target=poll_spotify_current_song, args=(button_values[1].strip(), user_id, queue), name=user_id)
    process.start()

    processes.append(process)

    SlackAPI.update("enable_listen", slack_payload['user']['id'], button_values[1])
    return jsonify({"msg": "ok"}), 200

  elif button_values[0] == 'disable_listen':
    for process in processes:
      if str(process.name) == user_id:
        os.kill(process.pid, signal.SIGKILL)
        remove_process(process.pid)

    payload = {
      "profile": {
          "status_text": "",
          "status_emoji": "",
          "status_expiration": int(time.time())
      }
    }
    SlackAPI.update_slack_status(payload)

    SlackAPI.update("disable_listen", slack_payload['user']['id'], button_values[1])
    return jsonify({"msg": "ok"}), 200

  else:
    logging.error(f"Something went wrong in commands_home, user: (#{user_id})")
    return jsonify({"error": "Something went wrong, please tell Alex G!"}), 500

@slack.route('/subscriptions/events', methods=['POST'])
def slack_events():
  slack_payload = request.json

  print(slack_payload)
  try:
    slack_payload['event']['view']['blocks'][2]['accessory']['value']
    return jsonify({"msg": "ok"})
  except:
    SlackAPI.update("default", slack_payload['event']['user'])
    return jsonify({"msg": "ok"})

def poll_spotify_current_song(spotify_token, user_id, queue):
  should_poll = queue.get_nowait()

  while True:
      if should_poll:
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

            SlackAPI.update_slack_status(payload)
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

            SlackAPI.update_slack_status(payload)

          try:
            should_poll = queue.get_nowait()
            payload = {
             "profile": {
              "status_text": "",
              "status_emoji": "",
              "status_expiration": int(time.time())
              }
            }

            SlackAPI.update_slack_status(payload)
          except:
            pass

          time.sleep(15)

        except Exception:
          payload = {
            "profile": {
                "status_text": "",
                "status_emoji": "",
                "status_expiration": int(time.time())
            }
          }

          SlackAPI.update_slack_status(payload)

          try:
            should_poll = queue.get_nowait()
            payload = {
             "profile": {
              "status_text": "",
              "status_emoji": "",
              "status_expiration": int(time.time())
              }
            }

            SlackAPI.update_slack_status(payload)
          except:
            pass

          time.sleep(15)
      else:
        logging.info("Process is now sleeping, listening for queue.")
        should_poll = queue.get()

def remove_process(pid):
    for process in processes[:]:
        if process.pid == pid:
            processes.remove(process)    