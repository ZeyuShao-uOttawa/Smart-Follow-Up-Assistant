import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheet(sheet_id, sheet_name='Log'):
    sa_path = os.getenv('GOOGLE_SA_JSON_PATH')
    if not sa_path:
        raise ValueError("GOOGLE_SA_JSON_PATH environment variable not set.")
    
    creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    worksheet = sh.worksheet(sheet_name)
    return worksheet

def append_followup_row(followup, ws):
    """
    followup: dict with keys task, due_date, type, source_text, created_at
    """
    row = [
        followup.get('status'),
        followup.get('action'),
        followup.get('followup_date'),
        followup.get('type'),
        followup.get('urgency'),
        followup.get('source_text'),
        followup.get('created_at')
    ]
    try:
        ws.insert_row(row, value_input_option='USER_ENTERED', index=2)
    except Exception as e:
        print("Error appending log row:", e)

def append_followup_scheduler_row(action, time, sws):
    """
    followup: dict with keys task, due_date, type, source_text, created_at
    """
    row = [
        action,
        time
    ]
    try:
        sws.insert_row(row, value_input_option='USER_ENTERED', index=2)
    except Exception as e:
        print("Error appending scheduler row:", e)