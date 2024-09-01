import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import argparse
import configparser
import os

# Load config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
credentials_path=config["paths"]["CREDENTIALS_PATH"]

# Function to load CSV files into a DataFrame
def load_csv(file_path):
    return pd.read_csv(file_path)

# Function to filter and sort incidents
def filter_and_sort_incidents(df):
    errors = df[df['Incident'].str.contains('ERROR')].sort_values(by='Incident_Count', ascending=False)
    warnings = df[df['Incident'].str.contains('WARN')].sort_values(by='Incident_Count', ascending=False)
    return errors, warnings

def calculate_totals(errors, warnings):
    total_errors = errors['Incident_Count'].sum()
    total_warnings = warnings['Incident_Count'].sum()
    return total_errors, total_warnings

# Function to initialize the Google Sheets API
def init_sheets_api(credentials_file):
    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=credentials)
    return service

# Function to create or update Google Sheets
def create_or_update_google_sheets(daily_data, spreadsheet_id, custom_errors_df=None):
    service = init_sheets_api(os.getcwd()+credentials_path)
    try:
        # Read the current spreadsheet
        sheet = service.spreadsheets()

        # Get the existing sheets
        existing_sheets = sheet.get(spreadsheetId=spreadsheet_id).execute().get('sheets', [])
        sheet_ids = {s['properties']['title']: s['properties']['sheetId'] for s in existing_sheets}

        for day, data in daily_data.items():
            errors, warnings = data['errors'], data['warnings']
            total_errors, total_warnings = data['totals']
            total_custom_errors = data.get('total_custom_errors', 0)

            # Check if sheet already exists for the current day
            if day in sheet_ids:
                gid = sheet_ids[day]
            else:
                # Create a new sheet if it doesn't exist
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': day
                        }
                    }
                }]
                body = {'requests': requests}
                sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

                # Refresh sheet IDs
                existing_sheets = sheet.get(spreadsheetId=spreadsheet_id).execute().get('sheets', [])
                sheet_ids = {s['properties']['title']: s['properties']['sheetId'] for s in existing_sheets}

                gid = sheet_ids[day]

            # Prepare data for the new sheet
            error_data = [['Incident_Count', 'Incident']] + errors.astype(str).values.tolist()
            warning_data = [['Incident_Count', 'Incident']] + warnings.astype(str).values.tolist()
            custom_error_data = [['Incident_Count', 'Incident']] + custom_errors_df.astype(str).values.tolist()

            for data in [error_data, warning_data, custom_error_data]:
                for row in data[1:]:
                    row[0] = int(row[0])

            # Define ranges
            error_range = f"{day}!A25:B{25 + len(errors)}"
            warning_range = f"{day}!I25:J{25 + len(warnings)}"
            custom_error_range = f"{day}!P25:Q{25 + len(custom_errors_df)}"

            # Prepare value ranges for batch update
            data = [
                {'range': error_range, 'values': error_data},
                {'range': warning_range, 'values': warning_data},
                {'range': custom_error_range, 'values': custom_error_data}
            ]

            # Batch update the sheet with the incident data
            body = {'valueInputOption': 'RAW', 'data': data}
            sheet.values().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

            # Summary data handling
            summary_range = 'Summary!A:D'
            summary_values = sheet.values().get(spreadsheetId=spreadsheet_id, range=summary_range).execute().get('values', [])

            day_exists = False
            for i, row in enumerate(summary_values):
                if row[0] == day:
                    day_exists = True
                    # Update the existing row
                    summary_values[i] = [
                        f'=HYPERLINK("https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}", "{day}")',
                        int(total_errors),
                        int(total_warnings),
                        int(total_custom_errors)
                    ]
                    # Update the summary range with modified values
                    body = {
                        'values': [summary_values[i]]
                    }
                    sheet.values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Summary!A{i+1}:D{i+1}',
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    break

            if not day_exists:
                # Prepare data for the new entry
                new_entry = [
                    [f'=HYPERLINK("https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}", "{day}")', int(total_errors), int(total_warnings), int(total_custom_errors)]
                ]
                # Append data to the Summary sheet
                sheet.values().append(
                    spreadsheetId=spreadsheet_id,
                    range=summary_range,
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body={'values': new_entry}
                ).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

# Main script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process CSV files and update Google Sheets.")
    parser.add_argument('csv_file_path_errors_warns', type=str, help='Path to the CSV file containing errors and warnings data.')
    parser.add_argument('csv_file_path_custom_errors', type=str, help='Path to the CSV file containing custom errors data.')

    args = parser.parse_args()

    spreadsheet_id=config['sheetId']['SPREADSHEET_ID']
    # Load CSV files
    df_errors_warns = load_csv(args.csv_file_path_errors_warns)
    df_custom_errors = load_csv(args.csv_file_path_custom_errors)

    # Filter and sort incidents
    errors, warnings = filter_and_sort_incidents(df_errors_warns)

    # Assuming all data belongs to the current day
    current_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # current_day = '2024-07-09'

    # Calculate totals for errors and warnings
    total_errors, total_warnings = calculate_totals(errors, warnings)

    # Calculate totals for custom errors
    total_custom_errors = df_custom_errors['Incident_Count'].sum()

    # Prepare daily data dictionary
    daily_data = {
        current_day: {
            'errors': errors,
            'warnings': warnings,
            'totals': (total_errors, total_warnings),
            'total_custom_errors': total_custom_errors
        }
    }

    # Create or update Google Sheets
    create_or_update_google_sheets(daily_data,spreadsheet_id, custom_errors_df=df_custom_errors)



