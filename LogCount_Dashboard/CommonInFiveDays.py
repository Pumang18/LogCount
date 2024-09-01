from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import defaultdict, Counter
import time
import configparser
import os

def compare(bytes1, bytes2, threshold):
    count1 = Counter(bytes1)
    count2 = Counter(bytes2)

    intersection_size = sum((count1 & count2).values())
    max_size = max(sum(count1.values()), sum(count2.values()))

    if max_size == 0:
        return False  # Handle division by zero case

    similarity_score = intersection_size / max_size

    return similarity_score > threshold

def find_matching_string(existing_strings, new_string, threshold):
    for string in existing_strings:
        if compare(string, new_string, threshold):
            return string
    return None

def main():
    # Load config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    credentials_path = config["paths"]["CREDENTIALS_PATH"]
    threshold_for_five_days = float(config["constant"]["THRESHOLD_FOR_FIVE_DAYS"])
    days = config["days"]["DAYS"]
    range_of_days = config["days"]["DAY_THRESHOLD"]

    # Define the scope and credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = (os.getcwd()+ credentials_path)
    print(SERVICE_ACCOUNT_FILE)


    # Load credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Sheets API client
    service = build('sheets', 'v4', credentials=credentials)

    # Function to process spreadsheet data
    def process_spreadsheet_data():
        try:
            day_range = int(days) + 2

            # Get all sheet names and sort them by date
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_names = sorted(sheet['properties']['title'] for sheet in spreadsheet['sheets'])[-day_range:-2]



            # Dictionary to store occurrences of strings
            string_occurrences = defaultdict(lambda: defaultdict(int))

            # Iterate over the last 5 sheets
            for sheet_name in sheet_names:
                try:
                    # Define ranges for each type
                    ranges = {
                        'ERROR': f"'{sheet_name}'!B26:B35",
                        'WARN': f"'{sheet_name}'!J26:J35",
                        'Custom Error': f"'{sheet_name}'!Q26:Q35"
                    }

                    for error_type, cell_range in ranges.items():
                        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=cell_range).execute()
                        values = result.get('values', [])

                        # Iterate over each cell and count occurrences of each string
                        for row in values:
                            if row:
                                cell_value = row[0].strip()
                                matching_string = find_matching_string(string_occurrences[error_type].keys(), cell_value, threshold_for_five_days)
                                if matching_string:
                                    string_occurrences[error_type][matching_string] += 1
                                else:
                                    string_occurrences[error_type][cell_value] += 1

                except HttpError as err:
                    print(f"Error processing sheet '{sheet_name}': {err}")

            return string_occurrences

        except HttpError as err:
            print(f"Error retrieving spreadsheet data: {err}")
            return defaultdict(lambda: defaultdict(int))


    # Function to create or update a sheet with occurrences
    def update_or_create_sheet(string_occurrences):
        new_sheet_name = 'RecentDays'

        try:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

            # Check if the sheet already exists
            sheet_exists = any(sheet['properties']['title'] == new_sheet_name for sheet in spreadsheet['sheets'])

            if sheet_exists:
                # Clear the existing sheet
                service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=new_sheet_name).execute()
            else:
                # Create a new sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': new_sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                }]
                body = {'requests': requests}
                service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

            # Write headers for the new sheet
            headers = [['ERROR', f"Incident Count in Recent {days} days", 'WARN', f"Incident Count in Recent {days} days", 'Custom Error', f"Incident Count in Recent {days} days"]]
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{new_sheet_name}!A20:F20",
                valueInputOption="RAW",
                body={"values": headers}
            ).execute()

            # Write the occurrences data to the new sheet
            row_index = 21
            for error_type, occurrences in string_occurrences.items():
                col_index = 1 if error_type == 'ERROR' else (3 if error_type == 'WARN' else 5)
                for string, count in occurrences.items():
                    if count >= int(range_of_days):  # Only write if count meets threshold
                        values = [[string, count]]
                        range_ = f"{new_sheet_name}!{chr(64+col_index)}{row_index}:{chr(64+col_index+1)}{row_index}"
                        service.spreadsheets().values().update(
                            spreadsheetId=spreadsheet_id,
                            range=range_,
                            valueInputOption="RAW",
                            body={"values": values}
                        ).execute()
                        row_index += 1
                        time.sleep(2.5)
                row_index = 21
            print(f"String occurrences saved to '{new_sheet_name}' sheet in spreadsheet ID: {spreadsheet_id}")

        except HttpError as err:
            print(f"Error updating or creating new sheet: {err}")

    # Replace 'your-spreadsheet-id' with your actual spreadsheet ID
    spreadsheet_id = config['sheetId']['SPREADSHEET_ID']

    day_range = int(days) + 2
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = sorted(sheet['properties']['title'] for sheet in spreadsheet['sheets'])[-day_range:-2]

    if(len(sheet_names)<int(days)):
        print("Change Days as these much days not available in sheets")
        return
    # Process spreadsheet data
    string_occurrences = process_spreadsheet_data()

    # Update or create a sheet with occurrences
    update_or_create_sheet(string_occurrences)

if __name__ == "__main__":
    main()
