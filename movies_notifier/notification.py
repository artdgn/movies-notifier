import json
import os

from movies_notifier.common import CURRENT_DATE, SENT_DIR
from movies_notifier.gdocs import Gdocs
from movies_notifier.logger import logger
from movies_notifier.mailgun import Mailgun
from movies_notifier.movies_store import Movie, MoviesStore


class Notifier:

    def __init__(self, send_mailgun_email=True, gdocs_share_email=True):
        self.send_mailgun_email = send_mailgun_email
        self.gdocs_share_email = gdocs_share_email

    def notify(self, movies, resend=False):
        to_send = [Movie(m).minimal_fields() for m in movies
                   if (resend or not self.notified(m))]

        if not resend and len(to_send) < len(movies):
            logger.info(f'{len(to_send)} movies that '
                        f'were not previously in notifications.')

        if not to_send:
            return to_send

        subject = f'{CURRENT_DATE}: {len(to_send)} new movies from popcorn'
        text = json.dumps(to_send, indent=4)

        success = False

        if self.send_mailgun_email:
            sent = Mailgun.send_email(subject=subject, text=text)
            success = success or sent

        if self.gdocs_share_email:
            df = MoviesStore().movie_list_to_export_df(to_send)
            df = df.set_index(df.columns[0]).T
            uploaded = Gdocs().upload_and_share(df=df,
                                               email=self.gdocs_share_email,
                                               sheet_name=CURRENT_DATE)
            success = success or uploaded

        if success:
            self.save_notified(to_send)
        else:
            self.log_notifications(subject=subject, text=text)

        return to_send

    @staticmethod
    def log_notifications(subject, text):
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
