import csv
import io
import os.path
import pickle
import re
import urllib
from typing import Optional

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class GoogleDriveClient:
    _SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
    ]
    _TOKEN_FILE = 'google_token.pickle'

    def __init__(self, secrets_file: str):
        self._secrets_file = secrets_file
        self._cached_creds: Optional[Credentials] = None

    def create_png(self, source: str, target_name: str, target_folder_id: str) -> str:
        creds = self._get_creds()
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(source, mimetype='image/png')
        metadata = {
            'name': target_name,
            'parents': [target_folder_id]
        }
        file = service.files().create(
            body=metadata,
            media_body=media).execute()
        return file.get('id')

    def update_png(self, source: str, target_id: str):
        creds = self._get_creds()
        service = build('drive', 'v3', credentials=creds)
        media = MediaFileUpload(source, mimetype='image/png')
        service.files().update(
            fileId=target_id,
            body={},
            media_body=media).execute()

    def download_png(self, id: str, output_file_name: str, folder_id: Optional[str]):
        creds = self._get_creds()
        service = build('drive', 'v3', credentials=creds)

        if folder_id is not None:
            lookup_ids = self.get_ids(id, folder_id)
            if len(lookup_ids) > 1:
                print('Warning: found ' + str(len(lookup_ids)) +
                      ' files for "' + id + '"')
            lookup_id = lookup_ids[0] if len(lookup_ids) > 0 else id

        request = service.files().get_media(fileId=lookup_id)
        with io.BytesIO() as stream:
            downloader = MediaIoBaseDownload(stream, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
            with open(output_file_name, 'wb') as f:
                f.write(stream.getbuffer())

    def get_ids(self, name: str, folder_id: str) -> list[str]:
        creds = self._get_creds()
        service = build('drive', 'v3', credentials=creds)

        files: list[dict] = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = service.files().list(
                q=F"name='{name}' and '{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id)',
                pageToken=page_token,
            ).execute()

            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return list(map(lambda f: f.get('id'), files))

    def create_csv(self, name: str, target_folder_id: str) -> str:
        creds = self._get_creds()
        service = build('sheets', 'v4', credentials=creds)
        metadata = {
            'properties': {
                'title': name,
            },
        }
        spreadsheet = service.spreadsheets().create(
            body=metadata,
            fields='spreadsheetId').execute()
        id = spreadsheet.get('spreadsheetId')

        driveService = build('drive', 'v3', credentials=creds)
        file = driveService.files().get(
            fileId=id,
            fields='parents').execute()
        oldParents = ",".join(file.get('parents'))
        file = driveService.files().update(
            fileId=id,
            addParents=target_folder_id,
            removeParents=oldParents).execute()
        return id

    def download_csv(self, id: str, folder_id: Optional[str]) -> csv.DictReader:
        creds = self._get_creds()
        service = build('sheets', 'v4', credentials=creds)

        if folder_id is not None:
            lookup_ids = self.get_ids(id, folder_id)
            lookup_id = lookup_ids[0] if len(lookup_ids) > 0 else id

        result = service.spreadsheets().get(
            spreadsheetId=lookup_id,
        ).execute()

        if len(result['sheets']) == 0:
            raise Exception('csv ' + id + ' is empty')

        url = result['spreadsheetUrl']
        exportUrl = re.sub("\/edit$", '/export', url)
        headers = {
            'Authorization': 'Bearer ' + creds.token,
        }

        firstSheet = result['sheets'][0]
        params = {
            'format': 'csv',
            'gid': firstSheet['properties']['sheetId'],
        }
        queryParams = urllib.parse.urlencode(params)
        url = exportUrl + '?' + queryParams

        response = requests.get(url, headers=headers)
        contentString = response.content.decode(encoding=response.encoding)
        rows = contentString.split('\r\n')
        return csv.DictReader(rows, delimiter=',')

    def create_folder(self, folder: str, parent_id: str) -> str:
        creds = self._get_creds()
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {
            'name': folder,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        file = service.files().create(body=file_metadata,
                                      fields='id').execute()
        return file.get('id')

    def _get_creds(self) -> Credentials:
        if self._cached_creds is not None and self._cached_creds.valid:
            return self._cached_creds

        creds: Optional[Credentials] = None
        if os.path.exists(GoogleDriveClient._TOKEN_FILE):
            with open(GoogleDriveClient._TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if creds is None or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._secrets_file, GoogleDriveClient._SCOPES)
                creds = flow.run_local_server(port=8083)

            with open(GoogleDriveClient._TOKEN_FILE, 'wb+') as token:
                pickle.dump(creds, token)

        self._cached_creds = creds
        return self._cached_creds
