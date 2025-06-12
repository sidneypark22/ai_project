# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START sheets_quickstart]
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2.service_account import Credentials
from typing import Optional

import string
from openpyxl.utils import get_column_letter, column_index_from_string

class GoogleSheetsAPI:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self._credentials = None
        self._service = None
        self._sheet = None
    
    def authenticate_using_credentials_file(self, credentials_filename: str):
        self._credentials = Credentials.from_service_account_file(filename=credentials_filename)
    
    def initiate_sheets_service(self):
        self._service = build("sheets", "v4", credentials=self._credentials)
        self._sheet = self._service.spreadsheets()
        
    def read_sheet_range(self, sheet_name: str, range_name: Optional[str] = None, return_original_output: Optional[bool] = False):
        try:
            if range_name is None:
                sheet_range = f"{sheet_name}"
            else:
                sheet_range = f"{sheet_name}!{range_name}"
            result = (
                self._sheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=sheet_range)
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return
            else:
                if return_original_output:
                    return values
                else:
                    return "\n".join([",".join([col for col in row]) for row in values])
            
        except HttpError as err:
            print(err)
    
    def update_sheet(self, sheet_name: str, values: list, number_of_cols: int, start_col: Optional[str] = "A", row_num: Optional[int] = None):
        if row_num is None:
            row_num = len(self.read_sheet_range(sheet_name=sheet_name, return_original_output=True)) + 1
        
        row_num_idx = row_num - 1
        end_col = get_column_letter(column_index_from_string(start_col) + number_of_cols)
        range_name = f"{start_col}{row_num}:{end_col}{row_num}"
        
        body = {"values": values}

        try:
            result = (
                self._sheet.values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            # print(f"{result.get('updatedCells')} cells updated with values {values[0]}.")
            return "\n".join([f"Cells have been updated with values as below.", ",".join(values[0]), "\n".join([f"{k}: {v}" for k,v in result.items()])])
        
        except HttpError as error:
            # print(f"An error occurred: {error}")
            return error