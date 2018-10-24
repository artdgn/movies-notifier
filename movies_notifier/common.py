import os
import datetime

CURRENT_TIMESTAMP = datetime.datetime.now().isoformat()
CURRENT_DATE = datetime.datetime.now().date().isoformat()
MOVIES_DIR = './data/movies'
os.makedirs(MOVIES_DIR, exist_ok=True)

LOG_DIR = './data/logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILEPATH = os.path.join(LOG_DIR, f'log_{CURRENT_TIMESTAMP}.txt')

MAILGUN_DATA_PATH = os.path.expanduser('~/.mailgun/mailgun.json')