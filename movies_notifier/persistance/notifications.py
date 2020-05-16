import json
import os

from movies_notifier.config.common import CURRENT_DATE, SENT_DIR
from movies_notifier.data_outputs.gdocs import Gdocs
from movies_notifier.data_outputs.mailgun import Mailgun
from movies_notifier.persistance.movies import Movie, MoviesStore
from movies_notifier.util.logger import logger


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
            uploaded = self.upload_to_gdocs(to_send)
            success = success or uploaded

        if success:
            self.save_notified(to_send)
        else:
            self.log_notifications(subject=subject, text=text)

        return to_send

    def upload_to_gdocs(self, movies):
        df = MoviesStore().movie_list_to_export_df(movies)
        df.set_index(df.columns[0])
        df['label'] = ''  # add label col for relevance labeling
        df = df[df.columns[[-1]].append(df.columns[0:-1])]
        upload_df = df.T
        return Gdocs().upload_and_share(df=upload_df,
                                        email=self.gdocs_share_email,
                                        sheet_name=CURRENT_DATE)

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
