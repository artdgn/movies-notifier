import json
import os

import requests

from movies_notifier.config.common import MAILGUN_DATA_PATH
from movies_notifier.util.logger import logger


class Mailgun:

    @staticmethod
    def mailgun_data():
        try:
            return json.load(open(MAILGUN_DATA_PATH))
        except Exception as e:
            logger.error(f"Mailgun data doesn't exist or is "
                         f"not a valid json at: {MAILGUN_DATA_PATH}. "
                         f"Provide a json file with following fields: "
                         f"MAILGUN_DOMAIN, MAILGUN_API_KEY, MAILGUN_RECIPIENTS.")
            return {}

    @classmethod
    def send_email(cls, subject='', text='', html='', files=()):
        mailgun_config = cls.mailgun_data()
        if mailgun_config:
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
                logger.info(f'Mailgun response: {resp.text}')
                return True
            else:
                logger.error(f"Failed sending Mailgun notification: got {resp} {resp.text}")