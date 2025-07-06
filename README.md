# backup-to-google-drive
A Python script for automatically backing up any file (such as a SQLite database, zip archive, config file, etc.) to a specific Google Drive folder.

It supports:
- Google Drive API via service account
- Daily automated backups using cron
- Cleanup of old files (keeps only the latest 4 backups)

## Google Cloud Setup
1. **Create a Google Cloud project** if you haven't already.
2. **Enable the Google Drive API**  
   - Go to: *APIs & Services > Library*
   - Search for **"Google Drive API"**
   - Click **Enable**
3. **Create a service account**  
   - Go to: *IAM & Admin > Service Accounts*
   - Click **Create Service Account**
4. **Generate a key** for the service account  
   - After creating it, go to the **Keys** tab
   - Click **Add Key > Create New Key > JSON**
   - Download the JSON file and **move it into your project folder**, next to the script (e.g., `google_creds.json`)
5. **Share the Google Drive folder** with the service account's email address
   - Open your Google Drive in a web browser
   - Navigate to the folder where you want to store backups
   - Right-click the folder and select **Share**
   - Add the service account's email (found in the JSON file) and give it **Editor** access

> **DO NOT COMMIT this JSON file to GitHub** – it contains sensitive credentials.

## Install Required Python Packages
Install required packages from `requirements.txt` using `pip`:
```bash
pip install -r requirements.txt
```

## .env Configuration
Create a .env file in the root of your project directory (next to backup.py)

```bash
BACKUP_SOURCE_PATH=/absolute/path/to/your/file.ext
DRIVE_FOLDER_ID=your-google-drive-folder-id
SERVICE_ACCOUNT_FILE=google_creds.json
```
> Important: Do not commit your .env file or your google_creds.json to version control (GitHub). Add them to your .gitignore.

### How to find your Google Drive folder ID:
1. Open your Google Drive in a web browser.
2. Navigate to the folder where you want to store backups.
3. Look at the URL in your browser's address bar. It will look something like this
   ```
   https://drive.google.com/drive/folders/1a2B3cD45eF6gH7iJ8kL9mN0oP
   ```
4. The folder ID is the part after `folders/`, in this case, `1a2B3cD45eF6gH7iJ8kL9mN0oP`.  
   Copy this ID and use it in your `.env` file.

> Make sure the service account has edit access to that folder. You can do this by sharing the folder with your service account's email.

## Run the Script Manually
```bash
python backup_to_drive.py
```

Output will be like this:
```yaml
Backup created at: /tmp/...
Uploaded to Google Drive with ID: ...
Deleted old backup: ...
```

## Automate with Cron
Edit your crontab:
```bash
crontab -e
```

Add a cron job to run the backup script daily at 2 AM:
```bash
0 2 * * * /usr/bin/python3 /path/to/your/backup_script/backup_to_drive.py >> /var/log/sqlite_backup.log 2>&1
``` 

## Logging
The script uses Python's `logging` module for debugging and tracking progress.  
Output is written to stdout by default, but you can redirect it to a log file using cron (see below).

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.