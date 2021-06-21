import os
import datetime

import pandas as pd

ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..')
MOVIES_DIR = os.path.join(ROOT_DIR, 'data/movies')
os.makedirs(MOVIES_DIR, exist_ok=True)
LOG_DIR = os.path.join(ROOT_DIR, 'data/logs')
os.makedirs(LOG_DIR, exist_ok=True)
SENT_DIR = os.path.join(ROOT_DIR, 'data/sent')
os.makedirs(SENT_DIR, exist_ok=True)
HTML_DIR = os.path.join(ROOT_DIR, 'data/html')
os.makedirs(HTML_DIR, exist_ok=True)

CURRENT_TIMESTAMP = datetime.datetime.now().isoformat()
CURRENT_DATE = datetime.datetime.now().date().isoformat()

LOG_FILEPATH = os.path.join(LOG_DIR, f'log_{CURRENT_TIMESTAMP}.txt')

MAILGUN_DATA_PATH = os.path.join(ROOT_DIR, 'data/mailgun/mailgun.json')


def console_settings():
    pd.set_option('display.max_colwidth', 300)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

console_settings()