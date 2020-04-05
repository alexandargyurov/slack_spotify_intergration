from flask import Flask
from flask_apscheduler import APScheduler
from multiprocessing import Process, current_process, Queue

import os

scheduler = APScheduler()

queue = Queue()
processes = []

@scheduler.task('cron', id='start_all_processes', day='*', hour='8')
def start_all_processes():
    queue.put_nowait(True)
    print('========== CRON JOB ==========')
    print('WAKING ALL PROCESSES ')
    print('========== CRON JOB ==========')

@scheduler.task('cron', id='stop_all_processes', day='*', hour='18')
def stop_all_processes():
    queue.put_nowait(False)
    print('========== CRON JOB ==========')
    print('SLEEPING ALL PROCESSES ')
    print('========== CRON JOB ==========')

class Config(object):
    SCHEDULER_API_ENABLED = True

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    scheduler.init_app(app)
    scheduler.start()

    from lib.spotify.routes import spotify
    from lib.slack.routes import slack
    from lib.bot.routes import bot

    app.register_blueprint(spotify)
    app.register_blueprint(slack)
    app.register_blueprint(bot)

    return app