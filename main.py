import streamlit as st
st.set_page_config(page_title="Trainer App v1.0", page_icon="🏋️", layout="wide", initial_sidebar_state="collapsed")
import pandas as pd
import datetime
import base64
import os
import time
import calendar
from dateutil.relativedelta import relativedelta
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Database Handler (Merged for Stability) ---
class DataHandler:
    def __init__(self, secrets_path='secrets.json'):
        self.secrets_path = secrets_path
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.client = None
        self.spreadsheet_name = "TrainerApp_Data"

    def authenticate(self):
        try:
            creds_dict = None
            try:
                creds_dict = st.secrets.get("gcp_service_account")
            except Exception:
                creds_dict = None

            if creds_dict:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else:
                if os.path.exists(self.secrets_path):
                    creds = ServiceAccountCredentials.from_json_keyfile_name(self.secrets_path, self.scope)
                else:
                    return False
            
            self.client = gspread.authorize(creds)
            return True
        except Exception as e:
            return False

    def get_worksheet(self, worksheet_name):
        if not self.client:
            if not self.authenticate(): return None
        try:
            sh = self.client.open(self.spreadsheet_name)
            return sh.worksheet(worksheet_name)
        except Exception: return None

    def fetch_calendar(self):
        ws = self.get_worksheet("Kalendarz")
        if ws: return pd.DataFrame(ws.get_all_records())
        return pd.DataFrame()

    def update_calendar_event(self, date_str, hour, client, training_type, status='active'):
        ws = self.get_worksheet("Kalendarz")
        if ws:
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

    def save_workout_result(self, client, exercise, weight, week):
        ws = self.get_worksheet("Treningi")
        if ws:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.append_row([timestamp, client, exercise, weight, week])
            return True
        return False

    def fetch_clients(self):
        ws = self.get_worksheet("Klienci")
        if ws: return pd.DataFrame(ws.get_all_records())
        return pd.DataFrame()

# Initialize DataHandler
if 'dh' not in st.session_state:
    st.session_state.dh = DataHandler()

# --- Consolidated CSS Injection (Premium Dark & v28 Buttons) ---
def local_css():
    st.markdown("""
<style>
    /* Global Styles */
    .stApp { background: #0d1117; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 98% !important; }
    
    /* Hide JS Bridge Input completely but keep it focusable */
    div[data-testid="stTextInput"]:has(input[aria-label="js_data_exchange"]),
    div[data-testid="stTextInput"]:has(input[id*="js_data_input"]) {
        position: absolute !important;
        left: -9999px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* v28 Exercise Button Design (Targeting st.popover) */
    div.element-container:has(.ex-btn-marker) { display: none !important; }

    /* Target the button inside st.popover */
    div.element-container:has(.ex-btn-marker) + div.element-container div[data-testid="stPopover"] > button {
        position: relative !important;
        padding-left: 50px !important;
        justify-content: flex-start !important;
        height: 70px !important;
        min-height: 70px !important;
        border-radius: 14px !important;
        background: #1c1c1e !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    /* Activity Circle Indicator */
    div.element-container:has(.ex-btn-marker) + div.element-container div[data-testid="stPopover"] > button::before {
        content: '';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 18px; 
        height: 18px; 
        border-radius: 50%; 
        border: 2px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    /* Active State (Circle filled) */
    div.element-container:has(.ex-btn-marker.btn-active) + div.element-container div[data-testid="stPopover"] > button::before {
        background: #31d5f2 !important;
        border-color: #31d5f2 !important;
        box-shadow: 0 0 15px rgba(49,213,242,0.5) !important;
    }
    
    div.element-container:has(.ex-btn-marker.btn-active) + div.element-container div[data-testid="stPopover"] > button {
        border-color: #31d5f2 !important;
        background: rgba(49,213,242,0.05) !important;
    }

    /* Layout */
    .main-layout { display: flex; gap: 30px; }
    
    /* Tile Link Styling - Sidebar */
    .tile-link {
        text-decoration: none !important;
        display: block;
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        background: #1c1c1e;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100px;
        cursor: pointer;
    }
    .tile-link:hover { transform: translateX(5px); border-color: #31d5f2; background: #252528; }
    .tile-img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.3; z-index: 1; filter: grayscale(100%); transition: 0.3s; }
    .tile-link:hover .tile-img { opacity: 0.5; filter: grayscale(0%); }
    .tile-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, rgba(13,17,23,0.9) 0%, rgba(13,17,23,0.4) 100%); z-index: 2; }
    .tile-content { position: relative; z-index: 3; padding: 15px 20px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .tile-label { color: #31d5f2; font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
    .tile-title { font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
    .tile-desc { font-size: 11px; color: #8b949e; line-height: 1.2; }

    /* Calendar Premium Grid */
    .calendar-wrapper { 
        background: #1c1c1e; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); 
        padding: 20px; overflow-x: auto;
    }
    .calendar-grid-header { display: grid; gap: 10px; margin-bottom: 15px; }
    .day-header { text-align: center; color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .day-header.today { color: #31d5f2; }
    .calendar-row { display: grid; gap: 10px; min-height: 80px; border-top: 1px solid rgba(255,255,255,0.03); }
    .time-col { color: #444; font-size: 11px; font-weight: 700; padding-top: 10px; text-align: right; padding-right: 15px; }
    .calendar-cell { position: relative; border-radius: 12px; background: rgba(255,255,255,0.01); transition: background 0.2s; border: 1px solid transparent; min-width: 120px; }
    .calendar-cell:hover { background: rgba(255,255,255,0.03); }

    /* Event Card */
    .event-card {
        background: rgba(49, 213, 242, 0.1); border-left: 4px solid #31d5f2; border-radius: 8px;
        padding: 8px 12px; height: calc(100% - 10px); margin: 5px; cursor: pointer;
        transition: all 0.2s; position: relative; user-select: none;
        display: flex; flex-direction: column; justify-content: center;
        width: calc(100% - 10px); box-sizing: border-box;
    }
    .event-card:hover { transform: translateY(-2px); background: rgba(49, 213, 242, 0.2); }
    .event-name { font-weight: 800; font-size: 13px; color: white; margin-bottom: 2px; }
    .event-type { font-size: 10px; color: #8b949e; }

    /* Delete Button */
    .delete-btn {
        position: absolute; top: -5px; right: -5px; width: 22px; height: 22px;
        background: #ff4b4b; color: white; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; font-size: 16px; font-weight: 900;
        cursor: pointer; z-index: 100; transition: transform 0.2s;
        opacity: 0; pointer-events: none;
    }
    .delete-btn:hover { transform: scale(1.2); }

    /* Edit Mode Active */
    .edit-mode-active .event-card { border-style: dashed; border-color: #31d5f2; cursor: move; }
    .edit-mode-active .delete-btn { opacity: 1; pointer-events: auto; }
    .edit-mode-active .event-card a { pointer-events: none; }
    .edit-toggle-btn { background: rgba(49, 213, 242, 0.1); border: 1px solid #31d5f2; color: #31d5f2; padding: 5px 15px; border-radius: 8px; cursor: pointer; font-weight: 700; font-size: 12px; }
    .edit-toggle-btn.active { background: #31d5f2; color: #0d1117; }

    /* Deleted Excel Style */
    .deleted-marker { position: absolute; top: 0; right: 0; width: 0; height: 0; border-style: solid; border-width: 0 12px 12px 0; border-color: transparent #ff4b4b transparent transparent; z-index: 10; }
    .deleted-info { display: none; position: absolute; top: 15px; right: 0; width: 150px; background: #2d2d30; border: 1px solid #ff4b4b; border-radius: 4px; padding: 8px; font-size: 10px; color: #ff4b4b; z-index: 100; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .calendar-cell:hover .deleted-info { display: block; }
    .add-btn { position: absolute; inset: 0; opacity: 0; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.2); font-size: 20px; }
    .calendar-cell:hover .add-btn { opacity: 1; }

    /* Fix global Streamlit primary button red color */
    .stButton > button[kind="primary"] {
        background-color: rgba(49,213,242, 0.8) !important;
        color: #fff !important;
        border: 1px solid #31d5f2 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 50px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #31d5f2 !important;
        color: #000 !important;
        box-shadow: 0 0 20px rgba(49,213,242,0.4);
    }
    
    /* Secondary Buttons Styling */
    .stButton > button[kind="secondary"] {
        background-color: #1c1c1e !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        height: 50px !important;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #31d5f2 !important;
        color: #31d5f2 !important;
        background: #252528 !important;
    }

    /* Selectbox, Date Input, and Text Input Styling */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    input {
        background-color: #1c1c1e !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    div[data-baseweb="select"]:hover, 
    div[data-baseweb="input"]:hover {
        border-color: #31d5f2 !important;
    }

    /* Widget Labels & Headers - Force High Visibility White */
    div[data-testid="stWidgetLabel"] p, 
    label, 
    .stSubheader, 
    .page-title,
    div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    
    div[data-testid="stWidgetLabel"] p {
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Page and Section Titles */
    .page-title {
        font-size: 28px !important;
        font-weight: 900 !important;
        margin-bottom: 20px !important;
    }

    /* Dropdown Menu & Popover Styling (Aggressive Fix) */
    div[data-baseweb="popover"], 
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"],
    [role="listbox"] {
        background-color: #1c1c1e !important;
        background: #1c1c1e !important;
        border: 1px solid rgba(49, 213, 242, 0.3) !important;
        color: white !important;
    }
    
    li[data-baseweb="option"],
    [role="option"] {
        background-color: #1c1c1e !important;
        color: #ffffff !important;
        transition: background 0.2s;
    }
    
    li[data-baseweb="option"]:hover,
    [role="option"]:hover,
    li[aria-selected="true"] {
        background-color: rgba(49, 213, 242, 0.1) !important;
        color: #31d5f2 !important;
    }

    /* Date Picker Calendar Fix (Comprehensive Dark Theme) */
    div[data-baseweb="calendar"],
    div[data-baseweb="calendar"] header,
    div[data-baseweb="calendar"] div[role="grid"],
    div[data-baseweb="calendar"] div[role="presentation"],
    div[data-baseweb="popover"] div[role="dialog"] {
        background-color: #1c1c1e !important;
        background: #1c1c1e !important;
        color: white !important;
        border: 1px solid rgba(49, 213, 242, 0.3) !important;
    }
    
    /* Target the month/year name and weekday labels (Su, Mo, etc.) */
    div[data-baseweb="calendar"] [data-baseweb="select"] div,
    div[data-baseweb="calendar"] header div,
    div[data-baseweb="calendar"] div[role="grid"] div {
        color: white !important;
        background-color: transparent !important;
    }

    /* Fix the white 'day headers' (Su, Mo, Tu...) */
    div[data-baseweb="calendar"] div[role="grid"] > div:first-child > div {
        color: #8b949e !important;
        font-weight: 700 !important;
    }

    /* Selected Day and Hover States */
    div[data-baseweb="calendar"] div[aria-selected="true"] > div,
    div[data-baseweb="calendar"] div[aria-selected="true"] {
        background-color: #31d5f2 !important;
        color: #000000 !important;
        border-radius: 50% !important;
    }

    div[data-baseweb="calendar"] div[role="gridcell"]:hover {
        background-color: rgba(49, 213, 242, 0.1) !important;
        border-radius: 50% !important;
    }

    /* Menu button styles (global) */
    .part-label { font-size: 18px; font-weight: 900; color: #31d5f2; text-transform: uppercase; margin: 30px 0 10px 0; }

    /* v28 Exercise Button Design (Row Style) */
    .exercise-row {
        display: flex;
        align-items: center;
        background: #1c1c1e;
        border-radius: 16px;
        padding: 0 20px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        cursor: pointer;
        transition: all 0.3s ease;
        user-select: none;
        height: 80px;
        box-sizing: border-box;
    }
    .exercise-row:hover { border-color: #31d5f2; background: #252528; }
    .exercise-row.selected { border-color: #31d5f2; background: rgba(49, 213, 242, 0.05); }

    .exercise-indicator {
        width: 22px; height: 22px;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.2);
        margin-right: 15px;
        transition: all 0.3s ease;
        flex-shrink: 0;
    }
    .exercise-row.selected .exercise-indicator {
        background: #31d5f2;
        border-color: #31d5f2;
        box-shadow: 0 0 15px rgba(49,213,242,0.5);
    }

    .exercise-name {
        flex-grow: 1;
        font-size: 15px;
        font-weight: 700;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Weight Pill Design */
    .pill-container {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #0d1117;
        padding: 5px 12px;
        border-radius: 100px;
        border: 1px solid rgba(49, 213, 242, 0.3);
        height: 54px;
        margin-left: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .pill-btn {
        width: 34px; height: 34px;
        border-radius: 50%;
        border: 2px solid #31d5f2;
        display: flex; align-items: center; justify-content: center;
        color: #31d5f2; font-weight: 900; font-size: 22px;
        cursor: pointer; transition: all 0.2s;
        user-select: none;
    }
    .pill-btn:active { transform: scale(0.85); background: rgba(49, 213, 242, 0.1); }
    .pill-display {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-width: 50px;
        height: 50px;
        background: #1c1c1e;
        border: 1px solid rgba(49, 213, 242, 0.2);
        border-radius: 50%;
    }
    .pill-val { font-size: 16px; font-weight: 900; color: white; line-height: 1; }
    .pill-unit { font-size: 8px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

    /* Mobile Responsive */
    @media (max-width: 1000px) {
        .calendar-wrapper { padding: 10px; border-radius: 16px; }
        .calendar-grid-header, .calendar-row { min-width: 800px; }
        .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
        .exercise-row { height: 70px; padding: 0 15px; }
        .pill-container { height: 44px; gap: 8px; }
        .pill-btn { width: 28px; height: 28px; font-size: 18px; }
        .pill-display { width: 40px; height: 40px; }
        .pill-val { font-size: 13px; }
    }
</style>
""", unsafe_allow_html=True)

local_css()

# --- Actions via Hidden Input (CONSOLIDATED) ---
js_data = st.text_input("js_data_exchange", key="js_data_input", label_visibility="collapsed")

# --- JS Bridge Script (Injected Globally) ---
js_bridge = """
<script>
const parentDoc = window.parent.document;

function sendActionToStreamlit(actionStr) {
    let targetInput = null;
    const inputs = parentDoc.querySelectorAll('input');
    inputs.forEach(el => {
        if(el.getAttribute('aria-label') === 'js_data_exchange' || (el.id && el.id.includes('js_data_input'))) {
            targetInput = el;
        }
    });

    if(targetInput) {
        targetInput.focus();
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(targetInput, actionStr + '&ts=' + Date.now());
        targetInput.dispatchEvent(new Event('input', { bubbles: true }));
        targetInput.dispatchEvent(new Event('change', { bubbles: true }));
        targetInput.blur();
    }
}

if (!parentDoc.getElementById('injected-global-script')) {
    const s = parentDoc.createElement('script');
    s.id = 'injected-global-script';
    s.innerHTML = `
        if (!document.head.querySelector('#dd-touch')) {
            const touchScript = document.createElement('script');
            touchScript.id = 'dd-touch';
            touchScript.src = 'https://bernardo-castilho.github.io/DragDropTouch/DragDropTouch.js';
            document.head.appendChild(touchScript);
        }

        if (!document.body.hasAttribute('data-drag-bound')) {
            document.body.setAttribute('data-drag-bound', 'true');
            
            document.body.addEventListener('click', (e) => {
                const actionEl = e.target.closest('[data-action]');
                if (actionEl) {
                    e.preventDefault(); e.stopPropagation();
                    window.sendActionToStreamlit(actionEl.getAttribute('data-action'));
                    return;
                }
                const stopEl = e.target.closest('[data-action-stop]');
                if (stopEl) {
                    e.stopPropagation(); 
                    const action = stopEl.getAttribute('data-action-stop');
                    if (action && action !== "true") {
                        e.preventDefault();
                        window.sendActionToStreamlit(action);
                    }
                    return;
                }
            });
            
            document.body.addEventListener('dragstart', (e) => {
                const el = e.target.closest('[data-drag-id]');
                if (el) {
                    e.dataTransfer.setData('text/plain', el.getAttribute('data-drag-id'));
                    el.style.opacity = '0.4';
                }
            });
            document.body.addEventListener('dragend', (e) => {
                const el = e.target.closest('[data-drag-id]');
                if (el) el.style.opacity = '1';
            });
            document.body.addEventListener('dragover', (e) => {
                const el = e.target.closest('[data-drop-zone]');
                if (el) { e.preventDefault(); el.style.background = 'rgba(49, 213, 242, 0.1)'; }
            });
            document.body.addEventListener('dragleave', (e) => {
                const el = e.target.closest('[data-drop-zone]');
                if (el) el.style.background = '';
            });
            document.body.addEventListener('drop', (e) => {
                const el = e.target.closest('[data-drop-zone]');
                if (el) {
                    e.preventDefault();
                    el.style.background = '';
                    const data = e.dataTransfer.getData('text/plain');
                    if(data) {
                        const parts = data.split(',');
                        if(parts[0] !== '' && parts[1] !== '' && (parts[0] !== el.getAttribute('data-drop-d') || parts[1] !== el.getAttribute('data-drop-h'))) {
                            window.sendActionToStreamlit('action=move&fd=' + parts[0] + '&fh=' + parts[1] + '&td=' + el.getAttribute('data-drop-d') + '&th=' + el.getAttribute('data-drop-h'));
                        }
                    }
                }
            });
        }
    `;
    parentDoc.body.appendChild(s);
}

parentDoc.defaultView.sendActionToStreamlit = sendActionToStreamlit;
</script>
"""
components.html(js_bridge, height=0, width=0)

# --- State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if 'dh' not in st.session_state:
    st.session_state.dh = DataHandler()

# --- Authentication Logic ---
def check_password():
    if st.session_state.get('authenticated'):
        login_ts = st.session_state.get('login_ts', 0)
        if time.time() - login_ts > 14400:
            st.session_state.authenticated = False
            st.rerun()
        return True

    # Check localStorage for valid session via Bridge (Safe for Cloud)
    st.components.v1.html(f"""
    <script>
    const authTs = window.localStorage.getItem('trainer_auth_ts');
    if (authTs && (Date.now() - parseInt(authTs)) < 14400000) {{
        window.parent.defaultView.sendActionToStreamlit('action=auto_login');
    }}
    </script>
    """, height=0)

    def password_entered():
        access_code = st.secrets.get("access_code", "170491")
        pwd = st.session_state.get("password", "")
        if pwd == access_code:
            st.session_state.authenticated = True
            st.session_state.login_ts = time.time()
            st.session_state.save_login = True
            st.session_state.password = "" 
        else:
            if pwd: st.error("❌ Błędny kod dostępu")

    st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; }
        div[data-testid="stTextInput"]:has(input[aria-label="Kod"]) > div { min-height: 130px !important; }
        div[data-testid="stTextInput"]:has(input[aria-label="Kod"]) > div > div { min-height: 130px !important; border-radius: 16px !important; }
        div[data-testid="stTextInput"]:has(input[aria-label="Kod"]) > div > div > input {
            background-color: #0d1117 !important; color: white !important;
            border: 3px solid #31d5f2 !important; border-radius: 16px !important;
            text-align: center !important; font-size: 48px !important;
            letter-spacing: 18px !important; min-height: 130px !important;
            padding: 40px 16px !important; caret-color: #31d5f2 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; margin-top:60px;"><h1 style="font-size:60px; font-weight:900; background: linear-gradient(135deg, #31d5f2, #2196F3); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TRAINER PRO</h1><p style="color: #8b949e; font-size:14px;">Wprowadź kod dostępu</p></div>', unsafe_allow_html=True)
    st.text_input("Kod", type="password", key="password", on_change=password_entered, label_visibility="collapsed")
    st.markdown('<div style="text-align:center; margin-top:20px;">', unsafe_allow_html=True)
    st.button("🔐 ZALOGUJ", on_click=password_entered, use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# Save login to localStorage
if st.session_state.get('save_login'):
    st.session_state.save_login = False
    components.html('<script>window.localStorage.setItem("trainer_auth_ts", Date.now().toString());</script>', height=0)

# --- Navigation & Page Persistence ---
if "page" not in st.session_state:
    st.session_state.page = st.query_params.get("page", "home")

# --- Helpers ---
def get_img(name):
    paths = [f"assets/{name}", name]
    for p in paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

def bento_tile(label, title, desc, img, page_name):
    img_b64 = get_img(img)
    active_border = "border-color: #31d5f2; background: #252528;" if st.session_state.page == page_name else ""
    st.markdown(f"""
        <div class="tile-link" style="{active_border}" data-action="action=nav&page={page_name}">
            <img src="data:image/png;base64,{img_b64}" class="tile-img">
            <div class="tile-overlay"></div>
            <div class="tile-content">
                <div class="tile-label">{label}</div>
                <div class="tile-title">{title}</div>
                <div class="tile-desc">{desc}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_pl_date(d):
    months = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
    days_pl = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
    return f"{days_pl[d.weekday()]}, {d.day} {months[d.month-1]}"

# --- Data Handling ---
def load_data_from_db():
    try:
        df = st.session_state.dh.fetch_calendar()
        new_data = {}
        if not df.empty:
            for _, row in df.iterrows():
                try:
                    d_str = str(row['Dzień'])
                    h = int(row['Godzina'])
                    new_data[d_str, h] = {
                        'name': row['Klient'],
                        'type': row['Typ'],
                        'status': row.get('Status', 'active')
                    }
                except: continue
        return new_data
    except:
        return {}

if 'schedule_data' not in st.session_state:
    st.session_state.schedule_data = load_data_from_db()

if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'selected_date' not in st.session_state: st.session_state.selected_date = datetime.date.today()
if 'mini_cal_date' not in st.session_state: st.session_state.mini_cal_date = datetime.date.today().replace(day=1)
if 'selected_week' not in st.session_state: st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
if 'calendar_view' not in st.session_state: st.session_state.calendar_view = 'tydzień'

def toggle_edit():
    st.session_state.edit_mode = not st.session_state.edit_mode

def clear_schedule():
    st.session_state.schedule_data = {}

# --- Actions via Hidden Input ---
if js_data and js_data != st.session_state.get('last_js_data', ''):
    st.session_state.last_js_data = js_data
    try:
        parts = dict(p.split('=') for p in js_data.split('&'))
        action = parts.get('action')
        if action == "auto_login":
            st.session_state.authenticated = True
            st.session_state.login_ts = time.time()
            st.rerun()
        elif action == "toggle_exercise":
            ex_name = parts.get("ex")
            if ex_name in st.session_state.add_data_exercises:
                del st.session_state.add_data_exercises[ex_name]
            else:
                st.session_state.add_data_exercises[ex_name] = 0.0
            st.rerun()
        elif action == "update_weight":
            ex_name = parts.get("ex")
            delta = float(parts.get("delta", 0))
            if ex_name in st.session_state.add_data_exercises:
                st.session_state.add_data_exercises[ex_name] += delta
                if st.session_state.add_data_exercises[ex_name] < 0:
                    st.session_state.add_data_exercises[ex_name] = 0.0
            st.rerun()
        elif action == "delete":
            d_p, h_p = parts.get("d"), int(parts.get("h", -1))
            if (d_p, h_p) in st.session_state.schedule_data: 
                st.session_state.schedule_data[(d_p, h_p)]['status'] = 'deleted'
                st.session_state.dh.delete_calendar_event(d_p, h_p)
        elif action == "move":
            f_d, f_h = parts.get("fd"), int(parts.get("fh", -1))
            t_d, t_h = parts.get("td"), int(parts.get("th", -1))
            if (f_d, f_h) in st.session_state.schedule_data:
                val = st.session_state.schedule_data.pop((f_d, f_h))
                st.session_state.schedule_data[(t_d, t_h)] = val
                st.session_state.dh.update_calendar_event(t_d, t_h, val['name'], val['type'])
        elif action == "prev_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date - relativedelta(months=1)
        elif action == "next_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date + relativedelta(months=1)
        elif action == "select_date":
            st.session_state.selected_date = datetime.date(int(parts.get("y")), int(parts.get("m")), int(parts.get("d")))
            st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
        elif action == "nav":
            st.session_state.page = parts.get('page', 'home')
        elif action == "open_event":
            st.session_state.page = "add_data"
            st.session_state.event_client = parts.get('client', '')
            st.session_state.event_hour = int(parts.get('hour', 12))
            st.session_state.event_day = parts.get('day', '')
        elif action == "add_event":
            st.session_state.page = "add_data"
            st.session_state.event_client = ''
            st.session_state.event_hour = int(parts.get('hour', 12))
            st.session_state.event_day = parts.get('day', '')
        st.rerun()
    except Exception as e:
        print(f"Action error: {e}")

# --- LAYOUT ---
st.markdown('<div class="main-layout">', unsafe_allow_html=True)
col_side, col_main = st.columns([1, 4])

with col_side:
    sel_date = st.session_state.selected_date
    d_str_today = sel_date.strftime("%Y-%m-%d")
    day_workouts = [v for k, v in st.session_state.schedule_data.items() if k[0] == d_str_today and v['status'] == 'active']
    
    # Square Dowodzenie Panel with Permanent Calendar
    c = calendar.Calendar(firstweekday=0)
    month_cal = c.monthdatescalendar(st.session_state.mini_cal_date.year, st.session_state.mini_cal_date.month)
    months_pl = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
    month_str = f"{st.session_state.mini_cal_date.year} {months_pl[st.session_state.mini_cal_date.month-1]}"
    
    grid_html = ""
    for d_l in ["P", "W", "Ś", "C", "P", "S", "N"]: grid_html += f'<div style="color: #8b949e;">{d_l}</div>'
    
    for week in month_cal:
        for d_o in week:
            is_current_month = d_o.month == st.session_state.mini_cal_date.month
            is_selected = d_o == sel_date
            color = "#444" if not is_current_month else "white"
            style = f"color: {color}; cursor: pointer; border-radius: 50%; width: 20px; height: 20px; line-height: 20px; margin: 0 auto;"
            if is_selected: style += " background: #31d5f2; color: #0d1117; font-weight: 800; box-shadow: 0 0 8px rgba(49,213,242,0.5);"
            grid_html += f'<span data-action="action=select_date&y={d_o.year}&m={d_o.month}&d={d_o.day}" style="display:inline-block; {style}">{d_o.day}</span>'

    dowodzenie_html = f"""<div style="background: linear-gradient(135deg, #1c1c1e 0%, #0d1117 100%); border: 1px solid rgba(49, 213, 242, 0.3); border-radius: 24px; padding: 20px; margin-bottom: 25px; display: flex; flex-direction: column; justify-content: space-between;"><div><div class="tile-label">DOWODZENIE</div><div style="font-size: 20px; font-weight: 800; color: white; margin-top: 10px;">{get_pl_date(sel_date)}</div></div><div style="font-size: 13px; color: #8b949e; margin-top: 5px; margin-bottom: 10px;">Zaplanowano <span class="stat-highlight">{len(day_workouts)}</span> treningów</div><div style="margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;"><div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 10px; color: #8b949e; font-weight: 600;"><span>{month_str}</span><div><span data-action="action=prev_month" style="cursor:pointer;">↑</span> <span data-action="action=next_month" style="margin-left:10px; cursor:pointer;">↓</span></div></div><div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center; font-size: 11px; font-weight: 500;">{grid_html}</div></div></div>"""
    st.markdown(dowodzenie_html, unsafe_allow_html=True)

    bento_tile("ADMINISTRACJA", "Dodaj dane", "Treningi i pomiary", "tile_add_data_1778074195381.png", "add_data")
    bento_tile("ANALITYKA", "Wyniki", "Wykresy postępów", "tile_dashboard_1778074214113.png", "dashboard")
    bento_tile("ZARZĄDZANIE", "Klienci", "Baza podopiecznych", "tile_clients_1778074239507.png", "clients")
    bento_tile("DOKUMENTACJA", "Raporty", "Pliki PDF", "tile_reports_1778074427532.png", "reports")
    bento_tile("NOTATNIK", "Notatki", "Uwagi o klientach", "tile_notes_1778074445132.png", "notes")
    bento_tile("USTAWIENIA", "Konfiguracja", "Ustawienia aplikacji", "tile_settings_1778074463560.png", "settings")

with col_main:
    if st.session_state.page == "home":
        col_hdr1, col_hdr_v, col_hdr2 = st.columns([3, 2, 1])
        with col_hdr1:
            st.markdown(f'<div style="color: #8b949e; font-size: 14px; font-weight: 600; padding: 10px 0;">WIDOK TYGODNIA {st.session_state.selected_week}</div>', unsafe_allow_html=True)
        with col_hdr_v:
            v_col1, v_col2 = st.columns(2)
            if v_col1.button("📱 DZIEŃ", type="primary" if st.session_state.calendar_view == "dzień" else "secondary", use_container_width=True):
                st.session_state.calendar_view = "dzień"; st.rerun()
            if v_col2.button("📅 TYDZIEŃ", type="primary" if st.session_state.calendar_view == "tydzień" else "secondary", use_container_width=True):
                st.session_state.calendar_view = "tydzień"; st.rerun()
        with col_hdr2:
            st.button("✅ KONIEC" if st.session_state.edit_mode else "⚙️ EDYTUJ", on_click=toggle_edit, use_container_width=True)

        try:
            edit_cls = "edit-mode-active" if st.session_state.edit_mode else ""
            all_days = ["PON", "WT", "ŚR", "CZW", "PT", "SOB"]
            
            if st.session_state.calendar_view == "dzień":
                show_days_indices = [sel_date.weekday()] if sel_date.weekday() < 6 else [0]
                cols_css = "grid-template-columns: 60px 1fr;"
            else:
                show_days_indices = list(range(6))
                cols_css = "grid-template-columns: 60px repeat(6, 1fr);"
            
            full_html = f'<div class="calendar-wrapper {edit_cls}">'
            full_html += f'<div class="calendar-grid-header" style="{cols_css}"><div class="day-header"></div>'
            
            # Calculate dates for the selected week
            week_start = sel_date - datetime.timedelta(days=sel_date.weekday())
            current_week_dates = []
            for i in show_days_indices:
                today_cls = "today" if i == sel_date.weekday() else ""
                day_date = week_start + datetime.timedelta(days=i)
                d_str = day_date.strftime("%Y-%m-%d")
                current_week_dates.append(d_str)
                full_html += f'<div class="day-header {today_cls}">{all_days[i]}<br><span style="font-size:10px; color:#555;">{day_date.day}.{day_date.month}</span></div>'
            full_html += '</div>'
            
            for h in range(6, 22):
                full_html += f'<div class="calendar-row" style="{cols_css}"><div class="time-col">{h}:00</div>'
                for idx, d_str in enumerate(current_week_dates):
                    key = (d_str, h)
                    event = st.session_state.schedule_data.get(key)
                    cell_content = ""
                    if event:
                        if event['status'] == 'active':
                            drag_str = "true" if st.session_state.edit_mode else "false"
                            cell_content = f"""
                                <div class="event-card" draggable="{drag_str}" data-drag-id="{d_str},{h}">
                                    <div class="delete-btn" data-action-stop="action=delete&d={d_str}&h={h}">−</div>
                                    <div data-action="action=open_event&client={event['name']}&hour={h}&day={d_str}" style="cursor:pointer; height:100%;">
                                        <div class="event-name" draggable="false">{event['name']}</div>
                                        <div class="event-type" draggable="false">{event['type']}</div>
                                    </div>
                                </div>
                            """
                        else:
                            cell_content = f'<div class="deleted-marker"></div><div class="deleted-info"><strong>USUNIĘTO:</strong><br>{event["name"]}<br>{event["type"]}</div>'
                    else:
                        cell_content = f'<div class="add-btn" data-action="action=add_event&hour={h}&day={d_str}" style="cursor:pointer;width:100%;height:100%;display:flex;align-items:center;justify-content:center;">+</div>'
                    
                    full_html += f'<div class="calendar-cell" data-drop-zone="true" data-drop-d="{d_str}" data-drop-h="{h}">{cell_content}</div>'
                full_html += '</div>'
            full_html += '</div>'
            st.markdown(full_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Błąd renderowania kalendarza: {e}")

    elif st.session_state.page == "add_data":
        EXERCISES_DATA = {
            "KLATKA PIERSIOWA": ["Wyciskanie sztangi na ławce poziomej", "Wyciskanie hantli na ławce skośnej dodatniej", "Rozpiętki z hantlami lub na maszynie", "Pompki na poręczach (dipsy)", "Krzyżowanie linek wyciągu"],
            "PLECY": ["Podciąganie na drążku", "Martwy ciąg (Deadlift)", "Wiosłowanie sztangą w opadzie", "Ściąganie drążka wyciągu górnego", "Przyciąganie uchwytu wyciągu dolnego"],
            "NOGI": ["Przysiady ze sztangą (Back Squat)", "Wypychanie na suwnicy (Leg Press)", "Wykroki z hantlami", "Martwy ciąg na prostych nogach (RDL)", "Uginanie nóg na maszynie leżąc"],
            "BARKI": ["Wyciskanie żołnierskie (Overhead Press)", "Wznosy hantli bokiem", "Wyciskanie hantli nad głowę", "Wznosy w opadzie (tylni akton)", "Podciąganie sztangi wzdłuż tułowia"],
            "TRICEPS": ["Wyciskanie w wąskim chwycie", "Prostowanie ramion z linkami", "Francuskie (Skullcrushers)", "Dipsy pionowo", "Prostowanie z hantlem nad głową"],
            "BICEPS": ["Uginanie ramion ze sztangą", "Uginanie z rotacją (suplinacją)", "Modlitewnik", "Uginanie młotkowe", "Podciąganie podchwytem"],
            "BRZUCH": ["Unoszenie nóg w zwisie", "Allahy (skłony z linką)", "Plank (deska)", "Deadbug", "Russian Twist"],
            "CARDIO": ["Bieżnia", "Rowerek", "Orbitek", "Schody", "Wioślarz"]
        }
        
        st.markdown('<div class="header-section"><div class="page-title">📝 Rejestracja Treningu</div></div>', unsafe_allow_html=True)
        q_client = st.session_state.get("event_client", "Jan Kowalski")
        q_hour = st.session_state.get("event_hour", 12)
        q_day_str = st.session_state.get("event_day", datetime.date.today().strftime("%Y-%m-%d"))
        
        if 'add_data_exercises' not in st.session_state: st.session_state.add_data_exercises = {}

        col_c, col_d, col_h = st.columns([2, 1, 1])
        with col_c:
            # Fetch clients from Google Sheets
            def get_clients_list():
                try:
                    df_c = st.session_state.dh.fetch_clients()
                    if not df_c.empty:
                        # First column is assumed to be the client name
                        return df_c.iloc[:, 0].astype(str).tolist()
                except Exception:
                    pass
                return ["Jan Kowalski", "Anna Nowak", "Piotr Zieliński", "Marek Murator", "Ania"]

            clients = get_clients_list()
            klient = st.selectbox("Podopieczny", clients, index=clients.index(q_client) if q_client in clients else 0)
        with col_d:
            train_date = st.date_input("Data", value=datetime.datetime.strptime(q_day_str, "%Y-%m-%d").date() if q_day_str else st.session_state.selected_date)
        with col_h:
            train_hour = st.selectbox("Godzina", list(range(6, 22)), index=max(0, q_hour - 6))

        st.divider()
        c1, c2 = st.columns(2)
        
        # --- Exercise List Function ---
        def render_exercise_section(part_name, exercises_dict):
            if not part_name: return
            exercises = exercises_dict.get(part_name, [])[:5] 
            for i, ex in enumerate(exercises):
                is_sel = ex in st.session_state.add_data_exercises
                weight = st.session_state.add_data_exercises.get(ex, 20.0)
                
                sel_class = "selected" if is_sel else ""
                
                pill_html = ""
                if is_sel:
                    pill_html = (
                        f'<div class="pill-container" data-action-stop="true">'
                        f'<div class="pill-btn" data-action="action=update_weight&ex={ex}&delta=-1.25">−</div>'
                        f'<div class="pill-display">'
                        f'<div class="pill-val">{weight:.2f}</div>'
                        f'<div class="pill-unit">kg</div>'
                        f'</div>'
                        f'<div class="pill-btn" data-action="action=update_weight&ex={ex}&delta=1.25">+</div>'
                        f'</div>'
                    )
                
                html = (
                    f'<div class="exercise-row {sel_class}" data-action="action=toggle_exercise&ex={ex}">'
                    f'<div class="exercise-indicator"></div>'
                    f'<div class="exercise-name">{ex}</div>'
                    f'{pill_html}'
                    f'</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

        with c1:
            main_p = st.selectbox("Główna Partia", ["KLATKA PIERSIOWA", "PLECY", "NOGI", "BARKI", ""], index=0)
            render_exercise_section(main_p, EXERCISES_DATA)
        with c2:
            extra_p = st.selectbox("Partia Uzupełniająca", ["TRICEPS", "BICEPS", "BRZUCH", "CARDIO", ""], index=0)
            render_exercise_section(extra_p, EXERCISES_DATA)
        
        st.divider()
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
        with f_col1:
            if st.button("POWRÓT", use_container_width=True):
                st.session_state.add_data_exercises = {}; st.session_state.page = "home"; st.rerun()
        with f_col2:
            if st.button("WYCZYŚĆ", use_container_width=True):
                st.session_state.add_data_exercises = {}; st.rerun()
        with f_col3:
            if st.button("ZAPISZ TRENING", type="primary", use_container_width=True):
                d_s = train_date.strftime("%Y-%m-%d")
                # Save the main calendar event (always allow this)
                if st.session_state.dh.update_calendar_event(d_s, train_hour, klient, main_p.capitalize()):
                    # Save individual exercises if any were selected
                    for ex, weight in st.session_state.add_data_exercises.items():
                        st.session_state.dh.save_workout_result(klient, ex, weight, st.session_state.selected_week)
                    
                    # Update local state and show success
                    st.session_state.schedule_data[(d_s, train_hour)] = {'name': klient, 'type': main_p.capitalize(), 'status': 'active'}
                    st.success("Zapisano trening!"); time.sleep(1)
                    st.session_state.add_data_exercises = {}; st.session_state.page = "home"; st.rerun()

    elif st.session_state.page == "settings":
        st.subheader("⚙️ Konfiguracja")
        if st.button("🗑️ WYCZYŚĆ GRAFIK"): clear_schedule(); st.rerun()
        if st.button("⬅️ POWRÓT"): st.session_state.page = "home"; st.rerun()
    else:
        st.write(f"Strona {st.session_state.page} w budowie...")
        if st.button("POWRÓT"): st.session_state.page = "home"; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
