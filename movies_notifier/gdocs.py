import random

import gspread_pandas

from movies_notifier.logger import logger


class Gdocs:

    def __init__(self):
        self.client = self.init_client()

    @staticmethod
    def init_client():
        try:
            return gspread_pandas.Client()
        except Exception as e:
            logger.error(f"Error {e} initialising gspread-pandas client"
                         f"Please see https://github.com/aiguofer/gspread-pandas "
                         f"for set-up instructions")

    def upload_and_share(self,
                         df,
                         email,
                         sheet_name,
                         filename='popcorn-new-movies'):
        if not self.client:
            return

        sh_file = self._get_or_create_file(filename)

        sheet_name = self._get_or_create_sheet(sh_file, sheet_name)

        sh_file.df_to_sheet(df, sheet=sheet_name, replace=True, index=True)
        logger.info(f'wrote DataFrame to "{sheet_name}" tab in {sh_file}')

        self._adjust_style(sh_file,
                           sheet_name=sheet_name,
                           rows=len(df),
                           cols=len(df.columns) + 1)

        sh_file.spread.share(email, perm_type='user', role='writer')
        logger.info(f'shared {sh_file} to {email}')
        return True

    def _get_or_create_file(self, filename) -> gspread_pandas.Spread:
        files = self.client.list_spreadsheet_files(filename)
        if not files:
            file = self.client.create(filename)
            logger.info(f'created spreadsheet: {file}')
        else:
            file = gspread_pandas.Spread(files[0]['id'])
            if len(files) > 1:
                logger.info(f'found multile existing "{filename}" '
                            f'spreadsheets, selecting first one: {file}')
            else:
                logger.info(f'found spreadsheet: {file}')
        return file

    @staticmethod
    def _get_or_create_sheet(file: gspread_pandas.Spread, sheet_name):
        try:
            file.create_sheet(sheet_name)
            logger.info(f'created sheet {sheet_name}')
            return sheet_name
        except Exception as e:
            new_sheet_name = f'{sheet_name}_{random.randint(1, 1e6)}'
            logger.error(f'Sheet creation failed for "{sheet_name}" with "{e}", '
                         f'perhaps already exists, creating "{new_sheet_name}"')
            file.create_sheet(new_sheet_name)
            logger.info(f'created sheet {sheet_name}')
            return new_sheet_name

    @classmethod
    def _adjust_style(cls, file: gspread_pandas.Spread, sheet_name, rows, cols):
        sheet = file.spread.worksheet(sheet_name)
        body = {
            'requests': [
                cls._text_format_request_body(
                    sheetid=sheet.id, rows=rows, cols=cols),
                cls._text_format_request_body(
                    sheetid=sheet.id, rows=rows, cols=1, alignment='LEFT'),
                cls._column_width_request_body(sheetid=sheet.id, cols=cols),
                cls._move_sheet_to_front_request_body(sheetid=sheet.id)
            ]
        }

        file.spread.batch_update(body)
        logger.info(f'moved tab {sheet_name} to front of file')

    @staticmethod
    def _text_format_request_body(sheetid,
                                  rows,
                                  cols,
                                  font_size=12,
                                  bold=True,
                                  wrap='WRAP',
                                  alignment='CENTER'):
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#CellFormat
        return {
            "repeatCell": {
                "range": {
                    "sheetId": sheetid,
                    "startRowIndex": 0,
                    "endRowIndex": rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": cols

                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": alignment,
                        "textFormat": {
                            "fontSize": font_size,
                            "bold": bold
                        },
                        "wrapStrategy": wrap
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment, textFormat, wrapStrategy)"
            }
        }

    @staticmethod
    def _column_width_request_body(sheetid, cols, width=200):
        # https://developers.google.com/sheets/api/samples/rowcolumn
        return {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheetid,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": cols
                },
                "properties": {
                    "pixelSize": width
                },
                "fields": "pixelSize"
            }
        }

    @staticmethod
    def _move_sheet_to_front_request_body(sheetid):
        return {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheetid,
                    'index': 0
                },
                'fields': 'index'
            }
        }
