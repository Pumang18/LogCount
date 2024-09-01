# Utility for Generating Reports

## Overview
This utility generates reports for Error, Warning, and Customer error based on log files from the previous day.

## Requirements
### Libraries Required:
- pandas
- google-auth
- google-api-python-client
- google-auth-httplib2

### Log File:
- LogFile should be created one day before the current date.

## Setup Instructions

### Create Spreadsheet From Google Sheets
To enable and link the Google Sheets API for creating a dashboard:

#### Step 1: Enable the Google Sheets API
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Create or select a project.
- Enable the "Google Sheets API" from the API Library.

#### Step 2: Create Credentials
- Set up OAuth consent screen under APIs & Services > OAuth consent screen.
- Create credentials by selecting "Service account" under APIs & Services > Credentials.
- Generate a JSON key for the service account.

#### Step 3: Find the Service Account Email
- Locate the `client_email` in the downloaded JSON file. This email will be used to share the Google Sheet.

#### Step 4: Share Google Sheet with Service Account
- Open your Google Sheet.
- Share it with the service account email (`client_email`) with Editor permissions.

#### Additional Tips
- Ensure proper permissions and security for the service account and JSON credentials.

### Adding AppScripts in Google Sheet Extension
To automate tasks in Google Sheets:

#### Step 1: Copy AppScripts
- Copy necessary files from the "AppScripts" folder.

#### Step 2: Open Google Sheet
- Open your Google Sheet.
- Go to Extensions > Apps Script.

#### Step 3: Create AppScript
- Name the AppScript and create 3 scripts as mentioned in the AppScripts directory.
- Save all files.

#### Step 4: Set Triggers
- Go to Triggers in the left panel.
- Add a new trigger with time-driven settings (e.g., every 2 hours).

### Create credentials.json
Rename the downloaded JSON file from Step 2 of creating credentials to `credentials.json` and move it to the appropriate directory.

### Update config.ini
Modify the `config.ini` file in the LogCount directory to customize recent days analysis and other settings:

- Set `DAYS=N` for analyzing the top occurrences in recent N days.
- Adjust thresholds as necessary.

### Changes
- Ensure to update `SPREADSHEET_ID` with the ID of your spreadsheet.
- Configure `LOG_FILE_PATH`, `OUTPUT_FILE_PATH`, `CSV_ERROR_WARN`, and `CSV_CUST` paths as needed.

## Running the Script
To execute the script:

```bash
chmod +x LogCount.sh
./LogCount.sh
