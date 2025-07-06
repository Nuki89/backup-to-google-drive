from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import datetime
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s: %(levelname)s %(filename)s:%(lineno)s - %(funcName)s(): %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("backup.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

BACKUP_SOURCE_PATH = os.getenv("BACKUP_SOURCE_PATH")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
DATE = datetime.datetime.now().strftime("%Y-%m-%d")
FILENAME = f"backup_{DATE}_" + os.path.basename(BACKUP_SOURCE_PATH)
BACKUP_COPY = f"/tmp/{FILENAME}"

required_env_vars = [BACKUP_SOURCE_PATH, DRIVE_FOLDER_ID, SERVICE_ACCOUNT_FILE]
if not all(required_env_vars):
    log.error("Missing one or more required environment variables.")
    exit(1)

def backup_file():
    shutil.copy2(BACKUP_SOURCE_PATH, BACKUP_COPY)
    log.info(f"Backup created at: {BACKUP_COPY}")

def cleanup_old_backups(service, max_files=4):
    """Keep only the latest N backups in the Google Drive folder."""
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType != 'application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, createdTime)',
        orderBy='createdTime desc'
    ).execute()
    
    files = results.get('files', [])

    if len(files) > max_files:
        for file in files[max_files:]:
            try:
                service.files().delete(fileId=file['id']).execute()
                log.info(f"Deleted old backup: {file['name']}")
            except Exception as e:
                log.error(f"Error deleting {file['name']}: {e}")

def upload_to_drive(file_path):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [DRIVE_FOLDER_ID] if DRIVE_FOLDER_ID else []
    }
    mime_type, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mime_type or "application/octet-stream")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    log.info(f"Uploaded to Google Drive with ID: {file.get('id')}")

    cleanup_old_backups(service, max_files=4)

if __name__ == "__main__":
    backup_file()
    upload_to_drive(BACKUP_COPY)
