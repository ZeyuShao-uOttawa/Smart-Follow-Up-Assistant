import os
import json
import streamlit as st
import traceback
import pandas as pd
from agent import parse_message
from googleSheetService import append_followup_row, get_sheet, append_followup_scheduler_row
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Smart Follow-Up Assistant", layout="wide")

st.title("Smart Follow-Up Assistant — Demo")

with st.sidebar:
    st.header("Settings")
    save_to_sheets = st.checkbox("Save detected follow-ups to Google Sheets", value=False)
    sheet_id = st.text_input("Google Sheet ID", os.getenv("SHEET_ID", ""))

st.markdown("Paste messages (one per line) or upload a JSON array of strings.")

input_mode = st.radio("Input mode", ["Paste messages", "Upload JSON"])

messages = []
if input_mode == "Paste messages":
    txt = st.text_area("Messages", height=200)
    if txt.strip():
        messages = [l.strip() for l in txt.splitlines() if l.strip()]
else:
    uploaded = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded is not None:
        messages = json.load(uploaded)
        if not isinstance(messages, list):
            st.error("JSON must be an array of message strings.")
            messages = []

if st.button("Analyze"):
    if not messages:
        st.warning("No messages found.")
    else:
        results = []
        workSheet = get_sheet(sheet_id, "Log")
        schedulerWorkSheet = get_sheet(sheet_id, "Scheduler")
        for message in messages:
            try:
                obj = parse_message(message)
            except Exception as e:
                st.error(f"Error parsing message: {e}")
                continue
            results.append(obj)
            if save_to_sheets and sheet_id:
                try:
                    append_followup_row(obj, workSheet)
                    append_followup_scheduler_row(obj.get('action'), obj.get('followup_date'), schedulerWorkSheet)
                except Exception as e:
                    st.error(f"Error saving to sheet: {traceback.format_exc()}")

        df = pd.DataFrame(results)
        st.subheader("Detected follow-ups")
        st.dataframe(df)

        # Show summary
        follow_ups = [r for r in results if r.get("status", "follow-up needed")]
        st.success(f"{len(follow_ups)} follow-up(s) detected.")