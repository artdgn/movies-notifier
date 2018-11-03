import json
import os

import requests

from movies_notifier.logger import logger
from movies_notifier.common import MAILGUN_DATA_PATH, SENT_DIR
from movies_notifier.movies_store import Movie

try:
    MAILGUN_DATA = json.load(open(MAILGUN_DATA_PATH))
except Exception as e:
    raise ValueError(f"Mailgun data doesn't exist or is "
                     f"not a valid json at: {MAILGUN_DATA_PATH}. "
                     f"Provide a json file with following fields: "
                     f"MAILGUN_DOMAIN, MAILGUN_API_KEY, MAILGUN_RECIPIENTS.")


class MailgunNotifier:

    @classmethod
    def notify(cls, movies, ignore_sent=False):
        to_send = [Movie(m).minimal_fields() for m in movies
                   if (ignore_sent or not cls.notified(m))]
        if to_send:
            resp = cls.send_mailgun_notifications(
                subject=f'{len(to_send)} new movies from popcorn',
                text=json.dumps(to_send, indent=4)
            )
            if resp.ok:
                cls.save_notified(to_send)
            else:
                logger.error(f'Notifying failed: {resp}')
            return resp

    @classmethod
    def save_notified(cls, movies):
        for m in movies:
            filepath = cls.movie_json_path(m)
            with open(filepath, 'wt') as f:
                json.dump(m, f)

    @staticmethod
    def movie_json_path(m):
        return Movie(m).json_path(SENT_DIR)

    @classmethod
    def notified(cls, m):
        return os.path.exists(cls.movie_json_path(m))

    @staticmethod
    def send_mailgun_notifications(subject='', text='', html='', files=()):
        resp = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DATA['MAILGUN_DOMAIN']}/messages",
            auth=("api", MAILGUN_DATA['MAILGUN_API_KEY']),
            data={"from": f"popcorn alerts <mailgun@{MAILGUN_DATA['MAILGUN_DOMAIN']}>",
                  "to": MAILGUN_DATA['MAILGUN_RECIPIENTS'],
                  "subject": subject,
                  "text": text,
                  "html": html
                  },
            files=[('attachment', (os.path.split(f)[1], open(f, 'rb').read())) for f in files]
        )
        if resp.ok:
            logger.info(f"Sent Mailgun notification to {MAILGUN_DATA['MAILGUN_RECIPIENTS']}")
        else:
            logger.error(f"Failed sending Mailgun notification: got {resp.text}")
        return resp

