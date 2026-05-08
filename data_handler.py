import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import streamlit as st

class DataHandler:
    def __init__(self, secrets_path='secrets.json'):
        self.secrets_path = secrets_path
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.client = None
        self.spreadsheet_name = "TrainerApp_Data"

    def authenticate(self):
        try:
            # First try Streamlit Secrets (for Cloud deployment)
            if "gcp_service_account" in st.secrets:
                creds_dict = st.secrets["gcp_service_account"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else:
                # Fallback to local file
                creds = ServiceAccountCredentials.from_json_keyfile_name(self.secrets_path, self.scope)
            
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

    def update_calendar_event(self, day, hour, client, training_type, status='active'):
        ws = self.get_worksheet("Kalendarz")
        if ws:
            # Simple append for now, more complex logic (find and update) could be added later
            ws.append_row([day, hour, client, training_type, status])
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
