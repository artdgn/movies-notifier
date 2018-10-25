import json

import requests

from movies_notifier.logger import logger
from movies_notifier.common import MAILGUN_DATA_PATH

try:
    MAILGUN_DATA = json.load(open(MAILGUN_DATA_PATH))
except Exception as e:
    raise ValueError(f"Mailgun data doesn't exist or is "
                     f"not a valid json at: {MAILGUN_DATA_PATH}. "
                     f"Provide a json file with following fields: "
                     f"MAILGUN_DOMAIN, MAILGUN_API_KEY, MAILGUN_RECIPIENTS.")


def send_mailgun_notifications(subject, text):
    resp = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DATA['MAILGUN_DOMAIN']}/messages",
        auth=("api", MAILGUN_DATA['MAILGUN_API_KEY']),
        data={"from": f"popcorn alerts <mailgun@{MAILGUN_DATA['MAILGUN_DOMAIN']}>",
              "to": MAILGUN_DATA['MAILGUN_RECIPIENTS'],
              "subject": subject,
              "text": text})
    if resp.ok:
        logger.info(f"Sent Mailgun notification to {MAILGUN_DATA['MAILGUN_RECIPIENTS']}")
    else:
        logger.error(f"Failed sending Mailgun notification: got {resp.text}")
    return resp

