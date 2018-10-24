import os
import json

import requests


MAILGUN_CREDS = json.load(open(os.path.expanduser('~/.mailgun/mailgun.json')))


def send_mailgun_notifications(subject, text):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_CREDS['MAILGUN_DOMAIN']}/messages",
        auth=("api", MAILGUN_CREDS['MAILGUN_API_KEY']),
        data={"from": f"popcorn alerts <mailgun@{MAILGUN_CREDS['MAILGUN_DOMAIN']}>",
              "to": [MAILGUN_CREDS['MAILGUN_RECIPIENT']],
              "subject": subject,
              "text": text})

