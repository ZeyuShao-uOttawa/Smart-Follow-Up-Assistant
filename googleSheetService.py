import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheet(sheet_id, sheet_name='Sheet1'):
    sa_path = os.getenv['GOOGLE_SA_JSON_PATH']
    creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(sheet_id)
    worksheet = sh.worksheet(sheet_name)
    return worksheet

def append_followup_row(sheet_id, followup):
    """
    followup: dict with keys task, due_date, type, source_text, created_at
    """
    ws = get_sheet(sheet_id)
    row = [
        followup.get('task'),
        followup.get('due_date'),
        followup.get('type'),
        followup.get('trigger'),
        followup.get('source_text'),
        followup.get('created_at')
    ]
    ws.append_row(row, value_input_option='USER_ENTERED')