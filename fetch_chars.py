import io
import pickle
from pathlib import Path

from pandas import read_excel
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import SECRETS_DIR
from secrets import ENTRIES_FILE_ID


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def _get_gdrive_service():
    '''
    Returns the user's access service for Google Drive.
    '''
    creds = None
    # Try to access existing credentials
    token_file = SECRETS_DIR / 'token.pickle'
    if token_file.exists():
        with token_file.open('rb') as token:
            creds = pickle.load(token)
    # No valid credentials, logs in the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secrets_file = SECRETS_DIR / 'creds.json'
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file.as_posix(), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with token_file.open('wb') as token:
            pickle.dump(creds, token)
    
    service = build('drive', 'v3', credentials=creds)
    return service


def _download_gdrive(file, download_request):
    '''
    Download a file with a request and a destination file.
    '''
    downloader = MediaIoBaseDownload(file, download_request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print('[INFO] Downloading {}%'.format(status.progress() * 100))


def fetch_from_gdrive():
    '''
    Fetch the list of characters from Google Drive spreadsheet.
    '''
    # Construct download request
    download_request = _get_gdrive_service().files().export_media(
        fileId=ENTRIES_FILE_ID,
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file = io.BytesIO()
    _download_gdrive(file, download_request)

    # Process the downloaded spreadsheet
    radical_df = read_excel(file, 'Radicals')
    character_df = read_excel(file, 'Characters')
    return radical_df, character_df
