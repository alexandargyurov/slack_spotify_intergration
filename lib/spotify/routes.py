from flask import Blueprint, request, redirect
from dotenv import load_dotenv
from tekore import Credentials

import lib.slack.slack_api as SlackAPI
import os

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URL = os.getenv("SPOTIFY_REDIRECT_URL")
SLACK_APP_ID = os.getenv("SLACK_APP_ID")

cred = Credentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL)
app_token = cred.request_client_token()

spotify = Blueprint('spotify', __name__)

@spotify.route('/spotify/callback', methods=['GET'])
def login_callback():
  code = request.args.get('code', None)
  user_id = request.args.get('state', None)

  token = cred.request_user_token(code)

  SlackAPI.update("disable_listen", user_id, token)
  return redirect("https://slack.com/app_redirect?app=" + SLACK_APP_ID, code=302)