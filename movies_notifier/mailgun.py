import json
import os

import requests

from movies_notifier.common import CURRENT_DATE
from movies_notifier.logger import logger
from movies_notifier.common import MAILGUN_DATA_PATH, SENT_DIR
from movies_notifier.movies_store import Movie


class Notifier:

    def __init__(self, backend='mailgun'):
        self.backend = backend

    @staticmethod
    def mailgun_data():
        try:
            return json.load(open(MAILGUN_DATA_PATH))
        except Exception as e:
            raise ValueError(f"Mailgun data doesn't exist or is "
                             f"not a valid json at: {MAILGUN_DATA_PATH}. "
                             f"Provide a json file with following fields: "
                             f"MAILGUN_DOMAIN, MAILGUN_API_KEY, MAILGUN_RECIPIENTS.")

    def notify(self, movies, resend=False):
        to_send = [Movie(m).minimal_fields() for m in movies
                   if (resend or not self.notified(m))]
        if not resend and len(to_send) < len(movies):
            logger.info(f'{len(to_send)} movies that '
                        f'were not previously in notifications.')
        if to_send:
            subject = f'{CURRENT_DATE}: {len(to_send)} new movies from popcorn'
            text = json.dumps(to_send, indent=4)

            if self.backend == 'mailgun':
                resp = self.send_mailgun_notifications(subject=subject, text=text                )
                if resp.ok:
                    logger.info(f'Notified of {len(to_send)} movies.')
                    self.save_notified(to_send)
                else:
                    logger.error(f'Notifying failed: {resp}')
                return resp

            else:
                logger.info(f'Only "mailgun" email notification backend supported '
                            f'({self.backend} supplied), printing results instead:')
                logger.info(subject)
                logger.info(text)

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

    @classmethod
    def send_mailgun_notifications(cls, subject='', text='', html='', files=()):
        mailgun_config = cls.mailgun_data()
        resp = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_config['MAILGUN_DOMAIN']}/messages",
            auth=("api", mailgun_config['MAILGUN_API_KEY']),
            data={"from": f"popcorn alerts <mailgun@{mailgun_config['MAILGUN_DOMAIN']}>",
                  "to": mailgun_config['MAILGUN_RECIPIENTS'],
                  "subject": subject,
                  "text": text,
                  "html": html
                  },
            files=[('attachment', (os.path.split(f)[1], open(f, 'rb').read())) for f in files]
        )
        if resp.ok:
            logger.info(f"Sent Mailgun notification to {mailgun_config['MAILGUN_RECIPIENTS']}")
        else:
            logger.error(f"Failed sending Mailgun notification: got {resp.text}")
        return resp

