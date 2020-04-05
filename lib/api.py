# from flask import Flask, session, redirect, url_for, request, jsonify
# from multiprocessing import Process, current_process, Queue

# from tekore import Spotify, Credentials, util, scope
# from tekore.scope import scopes, every
# from tekore.util import prompt_for_user_token, request_client_token, config
# from tekore.sender import PersistentSender
# from dotenv import load_dotenv

# import requests
# import json
# import webbrowser
# import os
# import time
# import signal
# import logging
# import subprocess

# load_dotenv()

# SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
# SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# SPOTIFY_REDIRECT_URL = os.getenv("SPOTIFY_REDIRECT_URL")
# SLACK_APP_ID = os.getenv("SLACK_APP_ID")

# cred = Credentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL)
# app_token = cred.request_client_token()

# spotify = Spotify(token=app_token, sender=PersistentSender())

# queue = Queue()




# # Flask













