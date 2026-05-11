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

# --- Auto-login check (MUST run before check_password) ---
components.html("""
<script>
if (!window._autoLoginSent) {
    window._autoLoginSent = true;
    const authTs = window.parent.localStorage.getItem('trainer_auth_ts');
    if (authTs && (Date.now() - parseInt(authTs)) < 14400000) {
        const parentDoc = window.parent.document;
        const input = parentDoc.querySelector('input[aria-label="js_data_exchange"]');
        if (input) {
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(input, 'action=auto_login&ts=' + Date.now());
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}
</script>
""", height=0)

# --- Hidden JS data input (for auto-login) ---
js_data_early = st.text_input("js_data_exchange", label_visibility="collapsed", key="js_data_exchange")
if js_data_early and 'auto_login' in js_data_early:
    st.session_state.authenticated = True

# --- Authentication ---
def check_password():
    if st.session_state.get('authenticated'):
        return True

    def password_entered():
        try:
            access_code = st.secrets.get("access_code", "170491")
        except:
            access_code = "170491"
        if st.session_state["password"] == access_code:
            st.session_state.authenticated = True
            st.session_state.save_session_now = True
            del st.session_state["password"]
            st.rerun()
        else:
            st.error("❌ Błędny kod dostępu")

    # Save session to localStorage after successful login
    if st.session_state.get('save_session_now'):
        st.session_state.save_session_now = False
        components.html('<script>window.parent.localStorage.setItem("trainer_auth_ts", Date.now().toString());</script>', height=0)

    st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; }
        .stTextInput > div { min-height: 130px !important; }
        .stTextInput > div > div { min-height: 130px !important; border-radius: 16px !important; }
        .stTextInput > div > div > input {
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

    st.markdown('<p style="text-align:center; color:#444; margin-top:40px; font-size:12px;">© 2026 Trainer Pro Dashboard</p>', unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()

# --- Navigation Logic ---
if "page" in st.query_params:
    st.session_state.page = st.query_params["page"]
else:
    st.session_state.page = "home"

# --- CSS Injection (Premium Dark) ---
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

    /* Calendar Premium Grid */
    .calendar-wrapper { background: #1c1c1e; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); padding: 20px; }
    .calendar-grid-header { display: grid; grid-template-columns: 60px repeat(6, 1fr); gap: 10px; margin-bottom: 15px; }
    .day-header { text-align: center; color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .day-header.today { color: #31d5f2; }
    .calendar-row { display: grid; grid-template-columns: 60px repeat(6, 1fr); gap: 10px; min-height: 80px; border-top: 1px solid rgba(255,255,255,0.03); }
    .time-col { color: #444; font-size: 11px; font-weight: 700; padding-top: 10px; text-align: right; padding-right: 15px; }
    .calendar-cell { position: relative; border-radius: 12px; background: rgba(255,255,255,0.01); transition: background 0.2s; border: 1px solid transparent; }
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
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #31d5f2 !important;
        color: #000 !important;
    }
    
    /* Global Secondary Buttons styled like Menu Tiles */
    .stButton > button[kind="secondary"] {
        height: 100px !important;
        min-height: 100px !important;
        max-height: 100px !important;
        border-radius: 16px !important;
        background: #1c1c1e !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #252528 !important;
        border-color: rgba(49,213,242,0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        color: #31d5f2 !important;
    }
    
    /* -------------------------------------- */
    /* Custom Circle inside Exercise Buttons  */
    /* -------------------------------------- */
    div.element-container:has(.ex-btn-marker) { display: none !important; }

    /* Shift text to the right to make room for circle */
    div.element-container:has(.ex-btn-marker) + div.element-container .stButton > button[kind="secondary"] {
        position: relative !important;
        padding-left: 50px !important;
        justify-content: flex-start !important;
    }
    div.element-container:has(.ex-btn-marker) + div.element-container .stButton > button[kind="secondary"] div,
    div.element-container:has(.ex-btn-marker) + div.element-container .stButton > button[kind="secondary"] p {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        margin: 0 !important;
        display: flex !important;
    }
    
    /* Draw the circle using ::before */
    div.element-container:has(.ex-btn-marker) + div.element-container .stButton > button[kind="secondary"]::before {
        content: '';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 22px; 
        height: 22px; 
        border-radius: 50%; 
        border: 2px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    /* Active State styling */
    div.element-container:has(.ex-btn-marker.btn-active) + div.element-container .stButton > button[kind="secondary"]::before {
        background: #31d5f2 !important;
        border-color: #31d5f2 !important;
        box-shadow: 0 0 15px rgba(49,213,242,0.5) !important;
    }
    
    div.element-container:has(.ex-btn-marker.btn-active) + div.element-container .stButton > button[kind="secondary"] {
        border-color: #31d5f2 !important;
        background: rgba(49,213,242,0.05) !important;
    }
    
    /* Menu button styles (global) */
    .part-label { font-size: 18px; font-weight: 900; color: #31d5f2; text-transform: uppercase; margin: 30px 0 10px 0; }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .calendar-wrapper { padding: 10px; border-radius: 16px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .calendar-grid-header, .calendar-row { min-width: 600px; }
        .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    }
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
    active_border = "border-color: #31d5f2; background: #252528;" if st.session_state.page == page_name else ""
    st.markdown(f"""
        <a class="tile-link" style="{active_border}" data-action="action=nav&page={page_name}">
            <img src="data:image/png;base64,{img_b64}" class="tile-img">
            <div class="tile-overlay"></div>
            <div class="tile-content">
                <div class="tile-label">{label}</div>
                <div class="tile-title">{title}</div>
                <div class="tile-desc">{desc}</div>
            </div>
        </a>
    """, unsafe_allow_html=True)

def get_pl_date(d):
    months = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
    days_pl = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
    return f"{days_pl[d.weekday()]}, {d.day} {months[d.month-1]}"

# --- State ---
def get_global_schedule():
    clients_pool = ["Jan Kowalski", "Anna Nowak", "Piotr Zieliński", "Marek Murator", "Ania"]
    exercises = ["Nogi", "Klatka piersiowa", "Plecy", "Barki", "FBW", "Mobilizacja", "Cardio", "Pośladki"]
    data = {}
    for d in range(6):
        for h in [7, 8, 10, 11, 17, 18, 19]:
            c_idx = (d + h) % len(clients_pool)
            e_idx = (h) % len(exercises)
            data[(d, h)] = {'name': clients_pool[c_idx], 'type': exercises[e_idx], 'status': 'active'}
    return data

if 'schedule_data' not in st.session_state:
    st.session_state.schedule_data = get_global_schedule()

if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'selected_date' not in st.session_state: st.session_state.selected_date = datetime.date.today()
if 'mini_cal_date' not in st.session_state: st.session_state.mini_cal_date = datetime.date.today().replace(day=1)
if 'selected_week' not in st.session_state: st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
if 'calendar_view' not in st.session_state: st.session_state.calendar_view = 'tydzień'

if st.query_params.get("edit_mode") == "1":
    st.session_state.edit_mode = True

def toggle_edit():
    st.session_state.edit_mode = not st.session_state.edit_mode

def clear_schedule():
    st.session_state.schedule_data = {}

# --- Actions via Hidden Input ---
js_data = js_data_early  # Use the input from the top of the file
if js_data and js_data != st.session_state.get('last_js_data', ''):
    st.session_state.last_js_data = js_data
    try:
        parts = dict(p.split('=') for p in js_data.split('&'))
        action = parts.get('action')
        if action == "delete":
            d_p, h_p = int(parts.get("d", -1)), int(parts.get("h", -1))
            if (d_p, h_p) in st.session_state.schedule_data: st.session_state.schedule_data[(d_p, h_p)]['status'] = 'deleted'
        elif action == "move":
            f_d, f_h = int(parts.get("fd", -1)), int(parts.get("fh", -1))
            t_d, t_h = int(parts.get("td", -1)), int(parts.get("th", -1))
            if (f_d, f_h) in st.session_state.schedule_data:
                val = st.session_state.schedule_data.pop((f_d, f_h))
                st.session_state.schedule_data[(t_d, t_h)] = val
        elif action == "prev_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date - relativedelta(months=1)
        elif action == "next_month":
            st.session_state.mini_cal_date = st.session_state.mini_cal_date + relativedelta(months=1)
        elif action == "select_date":
            st.session_state.selected_date = datetime.date(int(parts.get("y")), int(parts.get("m")), int(parts.get("d")))
            st.session_state.selected_week = st.session_state.selected_date.isocalendar()[1]
        elif action == "nav":
            page = parts.get('page', 'home')
            st.session_state.page = page
        elif action == "auto_login":
            st.session_state.authenticated = True
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
            all_days = ["PON", "WT", "ŚR", "CZW", "PT", "SOB"]
            
            if st.session_state.calendar_view == "dzień":
                show_days = [sel_date.weekday()] if sel_date.weekday() < 6 else [0]
                cols_css = "grid-template-columns: 60px 1fr;"
            else:
                show_days = list(range(6))
                cols_css = "grid-template-columns: 60px repeat(6, 1fr);"
            
            # Calculate dates for the selected week
            week_start = sel_date - datetime.timedelta(days=sel_date.weekday())
            
            full_html += f'<div class="calendar-grid-header" style="{cols_css}"><div class="day-header"></div>'
            for i in show_days:
                today_cls = "today" if i == sel_date.weekday() else ""
                day_date = week_start + datetime.timedelta(days=i)
                full_html += f'<div class="day-header {today_cls}">{all_days[i]}<br><span style="font-size:10px; color:#555;">{day_date.day}.{day_date.month}</span></div>'
            full_html += '</div>'
            
            for h in range(6, 22):
                full_html += f'<div class="calendar-row" style="{cols_css}"><div class="time-col">{h}:00</div>'
                for d in show_days:
                    key = (d, h)
                    event = st.session_state.schedule_data.get(key)
                    cell_content = ""
                    if event:
                        if event['status'] == 'active':
                            drag_str = "true" if st.session_state.edit_mode else "false"
                            cell_content = f"""
                                <div class="event-card" id="event_{d}_{h}" draggable="{drag_str}" data-drag-id="{d},{h}">
                                    <div class="delete-btn" data-action-stop="action=delete&d={d}&h={h}">−</div>
                                    <a href="/?page=add_data&client={event['name']}&hour={h}&day={d}" target="_self" draggable="false" style="text-decoration:none; color:inherit; display:block; height:100%;">
                                        <div class="event-name" draggable="false">{event['name']}</div>
                                        <div class="event-type" draggable="false">{event['type']}</div>
                                    </a>
                                </div>
                            """
                        else:
                            cell_content = f'<div class="deleted-marker"></div><div class="deleted-info"><strong>USUNIĘTO:</strong><br>{event["name"]}<br>{event["type"]}</div>'
                    else:
                        cell_content = f'<div class="add-btn"><a href="/?page=add_data&hour={h}&day={d}" target="_self" style="color:inherit;text-decoration:none;width:100%;height:100%;display:flex;align-items:center;justify-content:center;">+</a></div>'
                    
                    full_html += f'<div class="calendar-cell" data-drop-zone="true" data-drop-d="{d}" data-drop-h="{h}">{cell_content}</div>'
                full_html += '</div>'
            full_html += '</div>'
            st.markdown(full_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Błąd renderowania kalendarza: {e}")

    elif st.session_state.page == "add_data":
        # --- Exercise Data ---
        EXERCISES_DATA = {
            "KLATKA PIERSIOWA": [
                "Wyciskanie sztangi na ławce poziomej", "Wyciskanie hantli na ławce skośnej dodatniej",
                "Rozpiętki z hantlami lub na maszynie", "Pompki na poręczach (dipsy)", "Krzyżowanie linek wyciągu"
            ],
            "PLECY": [
                "Podciąganie na drążku", "Martwy ciąg (Deadlift)",
                "Wiosłowanie sztangą w opadzie", "Ściąganie drążka wyciągu górnego", "Przyciąganie uchwytu wyciągu dolnego"
            ],
            "NOGI": [
                "Przysiady ze sztangą (Back Squat)", "Wypychanie na suwnicy (Leg Press)", "Wykroki z hantlami",
                "Martwy ciąg na prostych nogach (RDL)", "Uginanie nóg na maszynie leżąc"
            ],
            "BARKI": [
                "Wyciskanie żołnierskie (Overhead Press)", "Wznosy hantli bokiem", "Wyciskanie hantli nad głowę",
                "Wznosy w opadzie (tylni akton)", "Podciąganie sztangi wzdłuż tułowia"
            ],
            "TRICEPS": [
                "Wyciskanie w wąskim chwycie", "Prostowanie ramion z linkami",
                "Francuskie (Skullcrushers)", "Dipsy pionowo", "Prostowanie z hantlem nad głową"
            ],
            "BICEPS": [
                "Uginanie ramion ze sztangą", "Uginanie z rotacją (suplinacją)",
                "Modlitewnik", "Uginanie młotkowe", "Podciąganie podchwytem"
            ],
            "BRZUCH": [
                "Unoszenie nóg w zwisie", "Allahy (skłony z linką)", "Plank (deska)", "Deadbug", "Russian Twist"
            ],
            "CARDIO": [
                "Bieżnia", "Rowerek", "Orbitek", "Schody", "Wioślarz"
            ]
        }
        
        st.markdown('<div class="header-section"><div class="page-title">📝 Rejestracja Treningu</div></div>', unsafe_allow_html=True)
        
        # Get query params or defaults
        q_client = st.query_params.get("client", "Jan Kowalski")
        q_hour = int(st.query_params.get("hour", "12"))
        q_day = int(st.query_params.get("day", "0"))
        
        # Initialization of state for exercises if not exists
        if 'add_data_exercises' not in st.session_state:
            st.session_state.add_data_exercises = {} # Format: {exercise_name: weight}

        # --- Top Navigation / Selection ---
        col_c, col_t = st.columns([2, 1])
        with col_c:
            klient = st.selectbox("Podopieczny", ["Jan Kowalski", "Anna Nowak", "Piotr Zieliński", "Marek Murator", "Ania"], index=0)
        with col_t:
            st.markdown(f'<div style="text-align: right; color: #8b949e; font-size: 12px; margin-top: 10px;">{["Pon", "Wt", "Śr", "Czw", "Pt", "Sob"][q_day]}, {q_hour}:00</div>', unsafe_allow_html=True)

        st.divider()
        c1, c2 = st.columns(2)
        
        # --- Exercise List Function ---
        def render_exercise_section(part_name, exercises_dict):
            if part_name == "NONE" or not part_name: return
            
            exercises = exercises_dict.get(part_name, [])[:5] 
            for i, ex in enumerate(exercises):
                is_sel = ex in st.session_state.add_data_exercises
                
                # Hidden marker to style the adjacent button
                active_class = "btn-active" if is_sel else "btn-inactive"
                st.markdown(f'<div class="ex-btn-marker {active_class}"></div>', unsafe_allow_html=True)
                
                if st.button(ex, key=f"sel_{part_name}_{i}", use_container_width=True):
                    if is_sel: del st.session_state.add_data_exercises[ex]
                    else: st.session_state.add_data_exercises[ex] = 20.0
                    st.rerun()

            
        with c1:
            main_part = st.selectbox("Główna Partia", ["KLATKA PIERSIOWA", "PLECY", "NOGI", "BARKI"], index=0)
            render_exercise_section(main_part, EXERCISES_DATA)
            
        with c2:
            extra_part = st.selectbox("Partia Uzupełniająca", ["TRICEPS", "BICEPS", "BRZUCH", "CARDIO", "NONE"], index=0)
            render_exercise_section(extra_part, EXERCISES_DATA)
        
        st.divider()

        # --- Footer Actions ---
        f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
        with f_col1:
            if st.button("⬅️ POWRÓT", use_container_width=True):
                st.session_state.add_data_exercises = {}
                st.query_params.clear(); st.session_state.page = "home"; st.rerun()
        with f_col2:
            if st.button("🗑️ WYCZYŚĆ", use_container_width=True):
                st.session_state.add_data_exercises = {}
                st.rerun()
        with f_col3:
            if st.button("✅ ZAPISZ TRENING", type="primary", use_container_width=True):
                if st.session_state.add_data_exercises:
                    # Save summary to schedule
                    ex_summary = ", ".join([f"{k} ({v}kg)" for k, v in st.session_state.add_data_exercises.items()])
                    st.session_state.schedule_data[(q_day, q_hour)] = {
                        'name': klient, 
                        'type': main_part.capitalize(), 
                        'info': ex_summary,
                        'status': 'active'
                    }
                    st.success("Zapisano trening!")
                    time.sleep(1)
                    st.session_state.add_data_exercises = {}
                    st.query_params.clear(); st.session_state.page = "home"; st.rerun()
                else:
                    st.error("Wybierz przynajmniej jedno ćwiczenie!")

    elif st.session_state.page == "settings":
        st.markdown('<div class="header-section"><div class="page-title">⚙️ Konfiguracja</div></div>', unsafe_allow_html=True)
        st.markdown('---')
        st.subheader("🗑️ Zarządzanie danymi")
        st.warning("Uwaga: ta operacja usunie wszystkie wpisy z kalendarza.")
        if st.button("🗑️ WYCZYŚĆ CAŁY GRAFIK", use_container_width=True):
            clear_schedule()
            st.success("Grafik wyczyszczony!")
            time.sleep(1)
            st.rerun()
        st.markdown('---')
        if st.button("⬅️ POWRÓT"): st.session_state.page = "home"; st.rerun()
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
        nativeInputValueSetter.call(input, actionStr + '&ts=' + Date.now());
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();
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
