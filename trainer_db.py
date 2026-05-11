import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import streamlit as st
import os

class DataHandler:
    def __init__(self, secrets_path='secrets.json'):
        self.secrets_path = secrets_path
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.client = None
        self.spreadsheet_name = "TrainerApp_Data"

    def authenticate(self):
        try:
            # Try Streamlit Secrets (for Cloud deployment)
            creds_dict = None
            try:
                # Avoid using 'in st.secrets' as it can cause KeyError in some environments
                creds_dict = st.secrets.get("gcp_service_account")
            except Exception:
                creds_dict = None

            if creds_dict:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else:
                # Fallback to local file
                if os.path.exists(self.secrets_path):
                    creds = ServiceAccountCredentials.from_json_keyfile_name(self.secrets_path, self.scope)
                else:
                    return False
            
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_worksheet(self, worksheet_name):
        if not self.client:
            if not self.authenticate():
                return None
        try:
            sh = self.client.open(self.spreadsheet_name)
            return sh.worksheet(worksheet_name)
        except Exception as e:
            print(f"Worksheet access error ({worksheet_name}): {e}")
            return None

    # --- Kalendarz Methods ---
    def fetch_calendar(self):
        ws = self.get_worksheet("Kalendarz")
        if ws:
            return pd.DataFrame(ws.get_all_records())
        return pd.DataFrame()

    def update_calendar_event(self, date_str, hour, client, training_type, status='active'):
        ws = self.get_worksheet("Kalendarz")
        if ws:
            # Check if event already exists for this date and hour to update instead of append
            data = ws.get_all_records()
            for i, row in enumerate(data):
                if str(row.get('Dzień')) == str(date_str) and int(row.get('Godzina')) == int(hour):
                    ws.update_cell(i + 2, 3, client)
                    ws.update_cell(i + 2, 4, training_type)
                    ws.update_cell(i + 2, 5, status)
                    return True
            
            ws.append_row([str(date_str), hour, client, training_type, status])
            return True
        return False

    # --- Treningi Methods ---
    def save_workout_result(self, client, exercise, weight, week):
        ws = self.get_worksheet("Treningi")
        if ws:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.append_row([timestamp, client, exercise, weight, week])
            return True
        return False

    def fetch_workouts(self):
        ws = self.get_worksheet("Treningi")
        if ws:
            return pd.DataFrame(ws.get_all_records())
        return pd.DataFrame()

    # --- Klienci Methods ---
    def fetch_clients(self):
        ws = self.get_worksheet("Klienci")
        if ws:
            return pd.DataFrame(ws.get_all_records())
        return pd.DataFrame()

    def add_client(self, name, notes=""):
        ws = self.get_worksheet("Klienci")
        if ws:
            join_date = datetime.datetime.now().strftime("%Y-%m-%d")
            ws.append_row([name, join_date, notes])
            return True
        return False
