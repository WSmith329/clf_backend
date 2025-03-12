import os

import gspread
import pandas as pd
from django.conf import settings


class GoogleSheetsClient:
    def __init__(self):  # pragma: no cover
        self.client = gspread.service_account_from_dict(self._config)
        self.share_email = os.getenv('GOOGLE_SHEET_SHARE_EMAIL')

    @property
    def _config(self):  # pragma: no cover
        return settings.GOOGLE_SHEETS_CONFIG

    def create_spreadsheet(self, sheet_name):  # pragma: no cover
        spreadsheet = self.client.create(sheet_name)
        spreadsheet.share(self.share_email, perm_type='user', role='writer')
        return spreadsheet

    def create_sheet_from_dataframe(self, df: pd.DataFrame, sheet_name):  # pragma: no cover
        spreadsheet = self.create_spreadsheet(sheet_name)
        spreadsheet.get_worksheet(0).update([df.columns.values.tolist()] + df.values.tolist())
