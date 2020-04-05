from flask import Blueprint, request, redirect, jsonify
from lib import queue, processes 
from dotenv import load_dotenv
from tekore import Credentials

import os
import signal

bot = Blueprint('bot', __name__)

@bot.route('/', methods=['GET'])
def home():
  print(processes)
  return jsonify({"msg": "ok"}), 200


# @bot.route('/kill', methods=['GET'])
# def killall():
#     pid = int(request.args.get('pid', ''))

#     try:
#       os.kill(pid, signal.SIGKILL)
#       remove_process(pid)
#       return jsonify({"error": "Process successfully stopped"}), 200
#     except ProcessLookupError:
#       return jsonify({"error": "No Process found with given PID"}), 500


@bot.route('/stop_processes', methods=['GET'])
def stop_processes():
    queue.put_nowait(False)
    return jsonify({"msg": "All processes have stopped"}), 200

@bot.route('/start_processes', methods=['GET'])
def start_processes():
    queue.put_nowait(True)
    return jsonify({"msg": "All processes have started"}), 200
