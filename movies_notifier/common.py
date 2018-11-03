import os
import datetime

ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
MOVIES_DIR = os.path.join(ROOT_DIR, 'data/movies')
os.makedirs(MOVIES_DIR, exist_ok=True)
LOG_DIR = os.path.join(ROOT_DIR, 'data/logs')
os.makedirs(LOG_DIR, exist_ok=True)
SENT_DIR = os.path.join(ROOT_DIR, 'data/sent')
os.makedirs(SENT_DIR, exist_ok=True)

CURRENT_TIMESTAMP = datetime.datetime.now().isoformat()
CURRENT_DATE = datetime.datetime.now().date().isoformat()

LOG_FILEPATH = os.path.join(LOG_DIR, f'log_{CURRENT_TIMESTAMP}.txt')

MAILGUN_DATA_PATH = os.path.expanduser('~/.mailgun/mailgun.json')