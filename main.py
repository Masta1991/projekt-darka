import streamlit as st
import pandas as pd
from data_handler import DataHandler
import datetime
import base64
import os
import time
import calendar
from dateutil.relativedelta import relativedelta
import streamlit.components.v1 as components

# --- Page Config ---
st.set_page_config(page_title="Trainer App v1.0", page_icon="🏋️", layout="wide", initial_sidebar_state="collapsed")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- JS Data Exchange Bridge (Must be rendered early for persistent login) ---
js_data = st.text_input("js_data_exchange", key="js_data_exchange", label_visibility="hidden")
if js_data and js_data != st.session_state.get('last_js_data', ''):
    st.session_state.last_js_data = js_data
    try:
        parts = dict(p.split('=') for p in js_data.split('&'))
        if 'w' in parts:
            st.session_state.screen_width = int(parts['w'])
            st.session_state.is_mobile = st.session_state.screen_width < 768
        if parts.get('action') == 'auto_login':
            st.session_state.authenticated = True
            st.rerun()
    except: pass

def check_password():
    def password_entered():
        try:
            access_code = st.secrets.get("access_code", "170491")
        except:
            access_code = "170491"
        if st.session_state["password"] == access_code:
            st.session_state.authenticated = True
            # Signal JS to save this session
            st.session_state.save_session = True
            del st.session_state["password"]
        else:
            st.error("❌ Błędny kod dostępu")

    # Form rendering only if not authenticated
    if not st.session_state.authenticated:
        st.markdown("""
        <style>
            .block-container { padding-top: 3rem !important; }
            /* === LARGE PASSWORD INPUT === */
            .stTextInput { margin-bottom: 16px !important; }
            .stTextInput > div { min-height: 130px !important; }
            .stTextInput > div > div {
                min-height: 130px !important;
                border-radius: 16px !important;
                overflow: visible !important;
            }
            .stTextInput > div > div > input {
                background-color: #0d1117 !important;
                color: white !important;
                border: 3px solid #31d5f2 !important;
                border-radius: 16px !important;
                text-align: center !important;
                font-size: 48px !important;
                letter-spacing: 18px !important;
                min-height: 130px !important;
                padding: 40px 16px !important;
                caret-color: #31d5f2 !important;
            }
            .stTextInput > div > div > input:focus {
                box-shadow: 0 0 25px rgba(49,213,242,0.35) !important;
                outline: none !important;
            }
            /* Eye icon button positioning */
            .stTextInput > div > div > div[data-testid="InputInstructions"] { display: none; }
            /* === ZALOGUJ BUTTON === */
            div[data-testid="stButton"] > button {
                background: linear-gradient(135deg, #31d5f2, #0099bb) !important;
                color: #000 !important;
                font-size: 20px !important;
                font-weight: 800 !important;
                padding: 20px 24px !important;
                border-radius: 14px !important;
                border: none !important;
                letter-spacing: 3px !important;
            }
        </style>
        """, unsafe_allow_html=True)

        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("""
            <div style="background:#1c1c1e; border:1px solid #31d5f2; border-radius:20px;
                        padding:20px 28px; text-align:center;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom:20px;">
                <div style="color:#31d5f2; font-size:10px; font-weight:800; letter-spacing:2px; text-transform:uppercase;">TRAINER PRO</div>
                <div style="color:white; font-size:20px; font-weight:800; margin:6px 0 4px;">🔐 Kod Dostępu</div>
                <div style="color:#8b949e; font-size:12px;">Wpisz kod i naciśnij ZALOGUJ</div>
            </div>
            """, unsafe_allow_html=True)

            pwd = st.text_input("Kod", type="password", key="password",
                                label_visibility="collapsed", placeholder="• • • • • •")
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            if st.button("🔓  ZALOGUJ", use_container_width=True):
                password_entered()
                if st.session_state.authenticated:
                    st.rerun()
            st.markdown('<p style="color:#444; font-size:11px; text-align:center; margin-top:16px;">Dostęp tylko dla uprawnionych osób</p>', unsafe_allow_html=True)
        
        # Hidden component to handle session saving
        if st.session_state.get('save_session'):
            components.html(f"""
                <script>
                const now = Date.now();
                window.parent.localStorage.setItem('trainer_auth_ts', now);
                window.parent.location.reload();
                </script>
            """, height=0)
            st.session_state.save_session = False
        st.stop()

check_password()

# --- Navigation Logic ---
# session_state is master - only read query_params on first load
if 'page' not in st.session_state:
    st.session_state.page = st.query_params.get("page", "home")

# --- CSS Injection (Premium Dark) ---
# --- Data Handlers ---
if 'dh' not in st.session_state:
    st.session_state.dh = DataHandler()

def get_clients():
    # Try fetching from Google Sheets first
    df = st.session_state.dh.fetch_clients()
    if not df.empty:
        return df.iloc[:, 0].tolist()
    
    # Fallback to local file (relative path)
    file_path = "Dokumenty/Klienci/Klienci.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["Jan Kowalski", "Anna Nowak", "Piotr Zieliński", "Marek Murator", "Ania"]

def add_client(name):
    # Always try cloud first
    st.session_state.dh.add_client(name)
    
    # Also keep local backup (relative path)
    file_path = "Dokumenty/Klienci/Klienci.txt"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n{name}")

def local_css():
    st.markdown("""
<style>
    /* Global Styles */
    .stApp { background: #0d1117; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 98% !important; }

    /* Layout */
    .main-layout { display: flex; gap: 30px; }
    
    @media (max-width: 900px) {
        .main-layout { flex-direction: column; gap: 15px; }
        .stColumn { width: 100% !important; flex: 1 1 auto !important; }
        .tile-link { height: 80px; }
        .tile-title { font-size: 16px; }
    }

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
    }
    .tile-link:hover { transform: translateX(5px); border-color: #31d5f2; background: #252528; }
    .tile-img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.3; z-index: 1; filter: grayscale(100%); transition: 0.3s; }
    .tile-link:hover .tile-img { opacity: 0.5; filter: grayscale(0%); }
    .tile-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, rgba(13,17,23,0.9) 0%, rgba(13,17,23,0.4) 100%); z-index: 2; }
    .tile-content { position: relative; z-index: 3; padding: 15px 20px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .tile-label { color: #31d5f2; font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
    .tile-title { font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
    .tile-desc { font-size: 11px; color: #8b949e; line-height: 1.2; }

    /* Calendar Premium Grid - EXCEL FREEZE PANES */
    .calendar-wrapper { 
        background: #1c1c1e; 
        border-radius: 24px; 
        border: 1px solid rgba(255,255,255,0.05); 
        padding: 20px; 
        overflow: auto; 
        height: 780px;
        max-height: 90vh;
        position: relative;
    }
    .calendar-grid-header { 
        display: grid; 
        grid-template-columns: 60px repeat(6, 1fr); 
        gap: 10px; 
        margin-bottom: 15px;
        position: sticky;
        top: -20px; /* Offset for wrapper padding */
        z-index: 100;
        background: #1c1c1e;
        padding: 10px 0;
    }
    .day-header { 
        text-align: center; 
        color: #8b949e; 
        font-size: 12px; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    .day-header.today { color: #31d5f2; }
    
    /* Freeze top-left corner */
    .day-header:first-child {
        position: sticky;
        left: -20px;
        z-index: 101;
        background: #1c1c1e;
    }

    .calendar-row { 
        display: grid; 
        grid-template-columns: 60px repeat(6, 1fr); 
        gap: 10px; 
        min-height: 80px; 
        border-top: 1px solid rgba(255,255,255,0.03); 
    }
    .time-col { 
        color: #444; 
        font-size: 11px; 
        font-weight: 700; 
        padding-top: 10px; 
        text-align: right; 
        padding-right: 15px;
        position: sticky;
        left: -20px;
        z-index: 90;
        background: #1c1c1e;
    }
    .calendar-cell { 
        position: relative; 
        border-radius: 12px; 
        background: rgba(255,255,255,0.01); 
        transition: background 0.2s; 
        border: 1px solid transparent; 
    }
    .calendar-cell:hover { background: rgba(255,255,255,0.03); }

    /* Event Card */
    .event-card {
        background: rgba(49, 213, 242, 0.1); border-left: 4px solid #31d5f2; border-radius: 8px;
        padding: 8px 12px; height: calc(100% - 10px); margin: 5px; cursor: pointer;
        transition: all 0.2s; position: relative; user-select: none;
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
    
    /* Fix global Streamlit primary button red color */
    .stButton > button[kind="primary"] {
        background-color: rgba(49,213,242, 0.8) !important;
        color: #fff !important;
        border: 1px solid #31d5f2 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #31d5f2 !important;
        color: #000 !important;
    }
    
    /* Menu button styles (global) */
    .part-label { font-size: 18px; font-weight: 900; color: #31d5f2; text-transform: uppercase; margin: 30px 0 10px 0; }

    /* ADD BUTTON (+) - Centered */
    .add-btn { 
        position: absolute; 
        inset: 0; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: rgba(255,255,255,0.1); 
        font-size: 24px; 
        transition: all 0.2s;
        opacity: 0;
    }
    .calendar-cell:hover .add-btn { 
        opacity: 1; 
        color: #31d5f2; 
    }

    /* DELETED EXCEL STYLE - Red triangle marker */
    .deleted-marker { 
        position: absolute; 
        top: 0; 
        right: 0; 
        width: 0; 
        height: 0; 
        border-style: solid; 
        border-width: 0 12px 12px 0; 
        border-color: transparent #ff4b4b transparent transparent; 
        z-index: 10; 
    }
    .deleted-info { 
        display: none; 
        position: absolute; 
        top: 15px; 
        right: 0; 
        width: 150px; 
        background: #2d2d30; 
        border: 1px solid #ff4b4b; 
        border-radius: 4px; 
        padding: 8px; 
        font-size: 10px; 
        color: #ff4b4b; 
        z-index: 100; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
    }
    .calendar-cell:hover .deleted-info { display: block; }
</style>
""", unsafe_allow_html=True)

local_css()

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
    # Use data-action - JS bridge handles click without page reload
    st.markdown(f"""
        <div class="tile-link" data-action="action=nav&page={page_name}">
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

# --- State ---
def get_global_schedule():
    df = st.session_state.dh.fetch_calendar()
    data = {}
    if not df.empty:
        for _, row in df.iterrows():
            # Key is now (date_string, hour)
            key = (str(row['Dzień']), int(row['Godzina']))
            data[key] = {
                'name': row['Klient'],
                'type': row['Typ'],
                'status': row['Status']
            }
    return data

if 'schedule_data' not in st.session_state:
    st.session_state.schedule_data = get_global_schedule()

if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'selected_date' not in st.session_state: st.session_state.selected_date = datetime.date.today()
if 'mini_cal_date' not in st.session_state: st.session_state.mini_cal_date = datetime.date.today().replace(day=1)
if 'selected_week' not in st.session_state: st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
if 'calendar_view' not in st.session_state: 
    st.session_state.calendar_view = "tydzień" if not st.session_state.get('is_mobile') else "dzień"

if st.query_params.get("edit_mode") == "1":
    st.session_state.edit_mode = True

def toggle_edit():
    st.session_state.edit_mode = not st.session_state.edit_mode

# --- Actions via Hidden Input (Navigation, Delete, Move) ---
# Note: Screen width and auto-login are already handled by the first js_data_exchange input at the top of the file.
if js_data and js_data != st.session_state.get('last_js_data_action', ''):
    st.session_state.last_js_data_action = js_data
    try:
        parts = dict(p.split('=') for p in js_data.split('&'))
        action = parts.get('action')
        if action == "nav":
            st.session_state.page = parts.get("page", "home")
            if "client" in parts: st.query_params["client"] = parts["client"]
            if "h" in parts: st.query_params["hour"] = parts["h"]
            if "date" in parts: st.query_params["date"] = parts["date"]
            st.rerun()
        elif action == "delete":
            date_str, h_p = parts.get("d"), int(parts.get("h", -1))
            if (date_str, h_p) in st.session_state.schedule_data:
                st.session_state.schedule_data[(date_str, h_p)]['status'] = 'deleted'
                # Update Google Sheets
                event = st.session_state.schedule_data[(date_str, h_p)]
                st.session_state.dh.update_calendar_event(date_str, h_p, event['name'], event['type'], 'deleted')
                st.rerun()
        elif action == "move":
            f_date, f_h = parts.get("fd"), int(parts.get("fh", -1))
            t_date, t_h = parts.get("td"), int(parts.get("th", -1))
            if (f_date, f_h) in st.session_state.schedule_data:
                val = st.session_state.schedule_data.pop((f_date, f_h))
                st.session_state.schedule_data[(t_date, t_h)] = val
                # Update Google Sheets (Delete old, Add new)
                st.session_state.dh.update_calendar_event(f_date, f_h, val['name'], val['type'], 'deleted')
                st.session_state.dh.update_calendar_event(t_date, t_h, val['name'], val['type'], 'active')
                st.rerun()
    except: pass
                st.session_state.dh.update_calendar_event(f_date, f_h, val['name'], val['type'], 'deleted')
                st.session_state.dh.update_calendar_event(t_date, t_h, val['name'], val['type'], 'active')
        elif action == "sync_weight":
            ex = parts.get("ex")
            val = float(parts.get("val", 0))
            st.session_state.add_data_exercises[ex] = val
        elif action == "toggle_ex":
            ex = parts.get("ex")
            status = parts.get("status")
            val = float(parts.get("val", 0))
            if status == "add":
                st.session_state.add_data_exercises[ex] = val
            else:
                st.session_state.add_data_exercises.pop(ex, None)
        elif action == "prev_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date - relativedelta(months=1)
        elif action == "next_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date + relativedelta(months=1)
        elif action == "select_date":
            st.session_state.selected_date = datetime.date(int(parts.get("y")), int(parts.get("m")), int(parts.get("d")))
            st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
    except Exception as e:
        print(f"Action error: {e}")
    st.rerun()

# --- LAYOUT ---
st.markdown('<div class="main-layout">', unsafe_allow_html=True)
col_side, col_main = st.columns([1, 4])

with col_side:
    sel_date = st.session_state.selected_date
    day_workouts = [v for k, v in st.session_state.schedule_data.items() if k[0] == sel_date.weekday() and v['status'] == 'active']
    
    # Square Dowodzenie Panel with Permanent Calendar
    c = calendar.Calendar(firstweekday=0)
    month_cal = c.monthdatescalendar(st.session_state.mini_cal_date.year, st.session_state.mini_cal_date.month)
    months_pl = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
    month_str = f"{st.session_state.mini_cal_date.year} {months_pl[st.session_state.mini_cal_date.month-1]}"
    
    grid_html = ""
    for d in ["P", "W", "Ś", "C", "P", "S", "N"]: grid_html += f'<div style="color: #8b949e;">{d}</div>'
    
    for week in month_cal:
        for d in week:
            is_current_month = d.month == st.session_state.mini_cal_date.month
            is_selected = d == sel_date
            color = "#444" if not is_current_month else "white"
            style = f"color: {color}; cursor: pointer; border-radius: 50%; width: 20px; height: 20px; line-height: 20px; margin: 0 auto;"
            if is_selected: style += " background: #31d5f2; color: #0d1117; font-weight: 800; box-shadow: 0 0 8px rgba(49,213,242,0.5);"
            grid_html += f'<span data-action="action=select_date&y={d.year}&m={d.month}&d={d.day}" style="display:inline-block; {style}">{d.day}</span>'

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
            full_html = f'<div class="calendar-wrapper {edit_cls}">'
            # Calculate dates for the current week (starting Monday)
            start_of_week = sel_date - datetime.timedelta(days=sel_date.weekday())
            all_week_dates = [start_of_week + datetime.timedelta(days=i) for i in range(6)]
            all_days_names = ["PON", "WT", "ŚR", "CZW", "PT", "SOB"]
            
            # Filter based on view
            if st.session_state.calendar_view == "dzień":
                # Find current selected day in the week
                day_idx = sel_date.weekday()
                if day_idx > 5: day_idx = 0 # Handle Sunday as Monday for display
                week_dates = [sel_date]
                days = [all_days_names[day_idx]]
                grid_template = "60px 1fr"
            else:
                week_dates = all_week_dates
                days = all_days_names
                grid_template = "60px repeat(6, 1fr)"
            
            # Inject dynamic grid template for responsiveness
            full_html += f'<style>.calendar-grid-header, .calendar-row {{ grid-template-columns: {grid_template} !important; gap: 10px !important; }} @media (max-width: 768px) {{ .calendar-row {{ min-width: {"900px" if st.session_state.calendar_view == "tydzień" else "100%"}; }} .calendar-grid-header {{ min-width: {"900px" if st.session_state.calendar_view == "tydzień" else "100%"}; }} }} </style>'
            
            full_html += '<div class="calendar-grid-header"><div class="day-header"></div>'
            for i, d_name in enumerate(days): 
                d_obj = week_dates[i]
                today_cls = "today" if d_obj == datetime.date.today() else ""
                full_html += f'<div class="day-header {today_cls}">{d_name}<br><span style="font-size:10px; opacity:0.6;">{d_obj.day}.{d_obj.month}</span></div>'
            full_html += '</div>'
            
            for h in range(6, 22):
                full_html += f'<div class="calendar-row"><div class="time-col">{h}:00</div>'
                for i, d_obj in enumerate(week_dates):
                    date_str = d_obj.strftime("%Y-%m-%d")
                    key = (date_str, h)
                    event = st.session_state.schedule_data.get(key)
                    cell_content = ""
                    if event:
                        if event['status'] == 'active':
                            drag_str = "true" if st.session_state.edit_mode else "false"
                            cell_content = f"""
                                <div class="event-card" id="event_{date_str}_{h}" draggable="{drag_str}" data-drag-id="{date_str},{h}" data-action="action=nav&page=add_data&client={event['name']}&h={h}&date={date_str}">
                                    <div class="delete-btn" data-action-stop="action=delete&d={date_str}&h={h}">−</div>
                                    <div class="event-name" draggable="false">{event['name']}</div>
                                    <div class="event-type" draggable="false">{event['type']}</div>
                                </div>
                            """
                        else:
                            cell_content = f'<div class="deleted-marker"></div><div class="deleted-info"><strong>USUNIĘTO:</strong><br>{event["name"]}<br>{event["type"]}</div>'
                    else:
                        cell_content = f'<div class="add-btn" data-action="action=nav&page=add_data&h={h}&date={date_str}">+</div>'
                    
                    full_html += f'<div class="calendar-cell" data-drop-zone="true" data-drop-d="{date_str}" data-drop-h="{h}">{cell_content}</div>'
                full_html += '</div>'
            full_html += '</div>'
            st.markdown(full_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Błąd renderowania kalendarza: {e}")

    elif st.session_state.page == "add_data":
        # --- Exercise Data ---
        EXERCISES_DATA = {
            "KLATKA PIERSIOWA": [
                "Wyciskanie sztangi poziomo", "Wyciskanie hantli skos +", 
                "Rozpiętki", "Dipsy (klatka)", "Krzyżowanie linek"
            ],
            "PLECY": [
                "Podciąganie na drążku", "Martwy ciąg (Deadlift)", 
                "Wiosłowanie sztangą", "Ściąganie drążka", "Przyciąganie dolne"
            ],
            "NOGI": [
                "Przysiady (Back Squat)", "Leg Press", "Wykroki", 
                "RDL (Martwy ciąg prosty)", "Uginanie leżąc"
            ],
            "BARKI": [
                "Overhead Press", "Wznosy bokiem", "Wyciskanie hantli", 
                "Wznosy w opadzie", "Podciąganie sztangi"
            ],
            "TRICEPS": [
                "Wyciskanie wąsko", "Prostowanie linki", 
                "Skullcrushers", "Dipsy pionowo", "Francuskie hantlem"
            ],
            "BICEPS": [
                "Uginanie sztanga", "Uginanie z suplinacją", 
                "Modlitewnik", "Uginanie młotkowe", "Podciąganie podchwytem"
            ],
            "BRZUCH": [
                "Unoszenie nóg", "Allahy", "Plank", "Deadbug", "Russian Twist"
            ],
            "CARDIO": [
                "Bieżnia", "Rowerek", "Orbitek", "Schody", "Wioślarz"
            ]
        }
        
        st.markdown('<div class="header-section"><div class="page-title">📝 Rejestracja Treningu</div></div>', unsafe_allow_html=True)
        
        # Get query params or defaults
        q_client = st.query_params.get("client", "Maciej Stawski")
        q_hour = int(st.query_params.get("hour", "12"))
        q_date = st.query_params.get("date", datetime.date.today().strftime("%Y-%m-%d"))
        
        # Initialization of state for exercises if not exists
        if 'add_data_exercises' not in st.session_state:
            st.session_state.add_data_exercises = {} # Format: {exercise_name: weight}

        # --- Top Navigation / Selection ---
        col_c, col_d, col_h = st.columns([2, 1, 1])
        with col_c:
            clients_list = get_clients()
            default_idx = clients_list.index(q_client) if q_client in clients_list else 0
            klient = st.selectbox("Podopieczny", clients_list, index=default_idx)
        with col_d:
            try:
                q_date_val = datetime.datetime.strptime(q_date, "%Y-%m-%d").date()
            except:
                q_date_val = datetime.date.today()
            selected_date = st.date_input("Data", value=q_date_val)
            q_date_str = selected_date.strftime("%Y-%m-%d")
        with col_h:
            selected_hour = st.number_input("Godzina", min_value=6, max_value=22, value=q_hour)

        st.divider()
        c1, c2 = st.columns(2)
        
        # --- Exercise List Function ---
        def render_exercise_section(part_name, exercises_dict):
            if part_name == "NONE" or not part_name: return
            
            exercises = exercises_dict.get(part_name, [])[:5] 
            
            html_out = """
            <style>
            :root {
              --bg-card: #1c1c24;
              --bg-active: #232332;
              --accent-cyan: #22d3ee;
              --text-main: #ffffff;
              --border-color: #2d2d3a;
            }
            body { 
                background-color: #0d1117; 
                margin: 0; 
                padding: 0; 
                font-family: 'Inter', sans-serif;
            }
            .exercise-card {
              display: flex;
              justify-content: space-between;
              align-items: center;
              background-color: var(--bg-card);
              border: 1px solid var(--border-color);
              border-radius: 16px;
              padding: 12px 20px;
              margin-bottom: 12px;
              color: var(--text-main);
              cursor: pointer;
              transition: all 0.3s ease;
              user-select: none;
              height: 75px;
              box-sizing: border-box;
            }
            .exercise-card.active {
              background-color: var(--bg-active);
              border-color: var(--accent-cyan);
              box-shadow: 0 0 15px rgba(34, 211, 238, 0.15);
            }
            .exercise-info { display: flex; align-items: center; gap: 15px; }
            .custom-radio { width: 20px; height: 20px; border-radius: 50%; border: 2px solid #555; transition: all 0.3s ease; }
            .exercise-card.active .custom-radio { border-color: var(--accent-cyan); box-shadow: 0 0 10px rgba(34, 211, 238, 0.6); background: radial-gradient(circle, var(--accent-cyan) 40%, transparent 45%); }
            .exercise-name { font-size: 16px; font-weight: 500; }
            .weight-stepper { display: flex; align-items: center; background-color: #15151b; border-radius: 30px; padding: 5px; border: 1px solid var(--border-color); opacity: 0; transform: translateX(10px); pointer-events: none; transition: all 0.3s ease; }
            .exercise-card.active .weight-stepper { opacity: 1; transform: translateX(0); pointer-events: auto; }
            .stepper-btn { background: #1c1c24; color: var(--accent-cyan); border: 1px solid var(--accent-cyan); border-radius: 50%; width: 36px; height: 36px; font-size: 22px; cursor: pointer; display: flex; justify-content: center; align-items: center; transition: all 0.2s ease; }
            .stepper-btn:hover { background: var(--accent-cyan); color: #15151b; }
            .weight-display { display: flex; flex-direction: column; align-items: center; min-width: 65px; }
            .weight-value { font-size: 20px; font-weight: bold; color: white; }
            .weight-unit { font-size: 10px; color: #888; text-transform: uppercase; margin-top: -3px; }
            </style>
            """
            for i, ex in enumerate(exercises):
                cw = st.session_state.add_data_exercises.get(ex, 0.0)
                
                html_out += f"""
                <div class="exercise-card" onclick="toggleSelection(this)">
                  <div class="exercise-info">
                    <div class="custom-radio"></div>
                    <span class="exercise-name">{ex}</span>
                  </div>
                  
                  <div class="weight-stepper" onclick="event.stopPropagation()">
                    <button class="stepper-btn" onclick="changeWeight(this, -2.5)">−</button>
                    <div class="weight-display">
                      <span class="weight-value">{cw}</span>
                      <span class="weight-unit">kg</span>
                    </div>
                    <button class="stepper-btn" onclick="changeWeight(this, 2.5)">+</button>
                  </div>
                </div>
                """
                
            html_out += """
            <script>
            function changeWeight(button, amount) {
              const card = button.closest('.exercise-card');
              const display = card.querySelector('.weight-value');
              let current = parseFloat(display.innerText);
              let newValue = current + amount;
              if (newValue < 0) newValue = 0;
              display.innerText = Number.isInteger(newValue) ? newValue : newValue.toFixed(1);
              
              // Sync weight with Python if active
              if (card.classList.contains('active')) {
                const exName = card.querySelector('.exercise-name').innerText;
                window.parent.sendActionToStreamlit('action=sync_weight&ex=' + encodeURIComponent(exName) + '&val=' + newValue);
              }
            }
            function toggleSelection(card) {
              card.classList.toggle('active');
              const exName = card.querySelector('.exercise-name').innerText;
              const weight = card.querySelector('.weight-value').innerText;
              const status = card.classList.contains('active') ? 'add' : 'remove';
              window.parent.sendActionToStreamlit('action=toggle_ex&ex=' + encodeURIComponent(exName) + '&val=' + weight + '&status=' + status);
            }
            </script>
            """
            
            # Use native iframe to completely bypass Streamlit sanitization
            components.html(html_out, height=460, scrolling=False)

            
        with c1:
            main_part = st.selectbox("Główna Partia", ["KLATKA PIERSIOWA", "PLECY", "NOGI", "BARKI"], index=0)
            render_exercise_section(main_part, EXERCISES_DATA)
            
        with c2:
            extra_part = st.selectbox("Partia Uzupełniająca", ["TRICEPS", "BICEPS", "BRZUCH", "CARDIO", "NONE"], index=0)
            render_exercise_section(extra_part, EXERCISES_DATA)
        
        st.divider()

        # --- Footer Actions ---
        f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
        with f_col1:
            if st.button("🏠 POWRÓT", use_container_width=True):
                st.session_state.add_data_exercises = {}
                st.session_state.page = "home"
                st.query_params.clear()
                st.rerun()
        with f_col2:
            if st.button("🗑️ WYCZYŚĆ", use_container_width=True):
                st.session_state.add_data_exercises = {}
                st.rerun()
        with f_col3:
            if st.button("✅ ZAPISZ TRENING", type="primary", use_container_width=True):
                with st.spinner("Zapisywanie..."):
                    try:
                        # Save exercises if any selected
                        if st.session_state.add_data_exercises:
                            for ex_name, weight in st.session_state.add_data_exercises.items():
                                st.session_state.dh.save_workout_result(klient, ex_name, weight, selected_date.isocalendar()[1])
                        # Always save the calendar slot
                        training_type = main_part.capitalize() if 'main_part' in dir() else "Trening"
                        st.session_state.dh.update_calendar_event(q_date_str, selected_hour, klient, training_type, 'active')
                        st.session_state.schedule_data[(q_date_str, selected_hour)] = {
                            'name': klient, 'type': training_type, 'status': 'active'
                        }
                        st.success("✅ Zapisano!")
                        time.sleep(1.5)
                        st.session_state.add_data_exercises = {}
                        st.session_state.page = "home"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd zapisu: {e}")


    elif st.session_state.page == "clients":
        st.markdown('<div class="header-section"><div class="page-title">👥 Baza Podopiecznych</div></div>', unsafe_allow_html=True)
        
        clients = get_clients()
        
        # Add new client section
        with st.expander("➕ DODAJ NOWEGO PODOPIECZNEGO", expanded=False):
            new_client_name = st.text_input("Imię i Nazwisko")
            if st.button("DODAJ DO BAZY", kind="primary"):
                if new_client_name:
                    add_client(new_client_name)
                    st.success(f"Dodano: {new_client_name}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Wprowadź imię i nazwisko!")

        st.markdown('<div class="part-label">AKTUALNI KLIENCI</div>', unsafe_allow_html=True)
        
        # Display clients in a grid
        cols = st.columns(3)
        for i, client in enumerate(clients):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: #1c1c1e; border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; margin-bottom: 15px; transition: 0.3s; cursor: default;">
                    <div style="color: #31d5f2; font-size: 10px; font-weight: 800; text-transform: uppercase; margin-bottom: 5px;">KLIENT</div>
                    <div style="font-size: 18px; font-weight: 700; color: white;">{client}</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("⬅️ POWRÓT DO MENU", use_container_width=True):
            st.query_params.clear(); st.session_state.page = "home"; st.rerun()
        with f_col2:
            if st.button("🗑️ WYCZYŚĆ", use_container_width=True):
                st.session_state.add_data_exercises = {}
                st.rerun()
        with f_col3:
            if st.button("✅ ZAPISZ TRENING", type="primary", use_container_width=True):
                if st.session_state.add_data_exercises:
                    # 1. Save results to 'Treningi' sheet
                    for ex_name, weight in st.session_state.add_data_exercises.items():
                        st.session_state.dh.save_workout_result(klient, ex_name, weight, st.session_state.selected_week)
                    
                    # 2. Save summary to schedule state & Google Sheet
                    ex_summary = ", ".join([f"{k} ({v}kg)" for k, v in st.session_state.add_data_exercises.items()])
                    st.session_state.schedule_data[(q_date, q_hour)] = {
                        'name': klient, 
                        'type': main_part.capitalize(), 
                        'info': ex_summary,
                        'status': 'active'
                    }
                    st.session_state.dh.update_calendar_event(q_date, q_hour, klient, main_part.capitalize(), 'active')
                    
                    st.success("Trening zapisany w Google Sheets!")
                    time.sleep(1)
                    st.session_state.add_data_exercises = {}
                    st.query_params.clear(); st.session_state.page = "home"; st.rerun()
                else:
                    st.error("Wybierz przynajmniej jedno ćwiczenie!")

    else:
        st.markdown(f"Sekcja {st.session_state.page} w budowie...")
        if st.button("POWRÓT"): st.session_state.page = "home"; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

js_code = """
<script>
const parentDoc = window.parent.document;

function sendActionToStreamlit(actionStr) {
    const input = parentDoc.querySelector('input[aria-label="js_data_exchange"]');
    if(input) {
        input.focus();
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        // Include window width in every action
        const width = window.innerWidth;
        nativeInputValueSetter.call(input, actionStr + '&w=' + width + '&ts=' + Date.now());
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();
    }
}

// Initial width and session report
if (!window.initialReportSent) {
    setTimeout(() => {
        const authTs = localStorage.getItem('trainer_auth_ts');
        const now = Date.now();
        let action = 'action=init';
        
        // If auth is less than 4 hours old (4 * 60 * 60 * 1000 ms)
        if (authTs && (now - parseInt(authTs)) < 14400000) {
            action = 'action=auto_login';
        }
        
        sendActionToStreamlit(action);
        window.initialReportSent = true;
    }, 500);
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
                const stopEl = e.target.closest('[data-action-stop]');
                if (stopEl) {
                    e.stopPropagation(); e.preventDefault();
                    window.sendActionToStreamlit(stopEl.getAttribute('data-action-stop'));
                    return;
                }
                const actionEl = e.target.closest('[data-action]');
                if (actionEl) {
                    e.preventDefault();
                    window.sendActionToStreamlit(actionEl.getAttribute('data-action'));
                }
            });
            
            document.body.addEventListener('dragstart', (e) => {
                if (e.target.closest('[data-action-stop]')) {
                    e.preventDefault();
                    return;
                }
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

// Make sendActionToStreamlit available in parent scope
parentDoc.defaultView.sendActionToStreamlit = sendActionToStreamlit;
</script>
"""
components.html(js_code, height=0, width=0)
