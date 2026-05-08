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

# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("access_code", "170491"):
            st.session_state.authenticated = True
            del st.session_state["password"]
        else:
            st.error("❌ Błędny kod dostępu")

    if not st.session_state.authenticated:
        st.markdown("""
        <style>
            .login-box {
                max-width: 400px; margin: 100px auto; padding: 40px;
                background: #1c1c1e; border-radius: 24px;
                border: 1px solid #31d5f2; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .stTextInput>div>div>input {
                background-color: #0d1117 !important;
                color: white !important;
                border: 1px solid #333 !important;
                text-align: center; font-size: 24px !important;
                letter-spacing: 5px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.markdown('<div class="tile-label">PROJEKT DARKA</div>', unsafe_allow_html=True)
            st.markdown('<h2 style="color:white; margin-bottom:30px;">🔐 Kod dostępu</h2>', unsafe_allow_html=True)
            st.text_input("Wpisz kod", type="password", on_change=password_entered, key="password")
            st.markdown('<p style="color:#8b949e; font-size:12px; margin-top:20px;">Dostęp tylko dla uprawnionych osób</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

check_password()

# --- Navigation State ---
if 'page' not in st.session_state:
    st.session_state.page = st.query_params.get("page", "home")

# --- Data Handlers ---
if 'dh' not in st.session_state:
    st.session_state.dh = DataHandler()

def get_clients():
    df = st.session_state.dh.fetch_clients()
    if not df.empty:
        return df.iloc[:, 0].tolist()
    return ["Maciej Stawski", "Paweł Frencel", "Pawel", "Ewa", "Ania", "Justyna"]

# --- CSS Injection ---
def local_css():
    st.markdown("""
<style>
    .stApp { background: #0d1117; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 98% !important; }
    .main-layout { display: flex; gap: 30px; }
    @media (max-width: 900px) {
        .main-layout { flex-direction: column; gap: 15px; }
        .calendar-wrapper { overflow-x: auto; padding: 10px; }
        .calendar-row, .calendar-grid-header { min-width: 600px; }
    }
    .tile-link {
        text-decoration: none !important; display: block; position: relative;
        border-radius: 20px; overflow: hidden; background: #1c1c1e;
        border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 12px;
        transition: all 0.3s; height: 100px; cursor: pointer;
    }
    .tile-link:hover { transform: translateX(5px); border-color: #31d5f2; background: #252528; }
    .tile-img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.3; z-index: 1; filter: grayscale(100%); }
    .tile-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, rgba(13,17,23,0.9) 0%, rgba(13,17,23,0.4) 100%); z-index: 2; }
    .tile-content { position: relative; z-index: 3; padding: 15px 20px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .tile-label { color: #31d5f2; font-size: 10px; font-weight: 800; text-transform: uppercase; }
    .tile-title { font-size: 18px; font-weight: 700; color: #ffffff; }
    .tile-desc { font-size: 11px; color: #8b949e; }
    .calendar-wrapper { background: #1c1c1e; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); padding: 20px; }
    .calendar-grid-header { display: grid; grid-template-columns: 60px repeat(6, 1fr); gap: 10px; margin-bottom: 15px; }
    .day-header { text-align: center; color: #8b949e; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .day-header.today { color: #31d5f2; }
    .calendar-row { display: grid; grid-template-columns: 60px repeat(6, 1fr); gap: 10px; min-height: 80px; border-top: 1px solid rgba(255,255,255,0.03); }
    .time-col { color: #444; font-size: 11px; font-weight: 700; padding-top: 10px; text-align: right; padding-right: 15px; }
    .calendar-cell { position: relative; border-radius: 12px; background: rgba(255,255,255,0.01); }
    .event-card { background: rgba(49, 213, 242, 0.1); border-left: 4px solid #31d5f2; border-radius: 8px; padding: 8px 12px; height: calc(100% - 10px); margin: 5px; cursor: pointer; transition: 0.2s; position: relative; }
    .event-name { font-weight: 800; font-size: 13px; color: white; }
    .event-type { font-size: 10px; color: #8b949e; }
    .delete-btn { position: absolute; top: -5px; right: -5px; width: 22px; height: 22px; background: #ff4b4b; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; }
    .edit-mode-active .delete-btn { opacity: 1; pointer-events: auto; }
    .add-btn { position: absolute; inset: 0; opacity: 0; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; }
    .calendar-cell:hover .add-btn { opacity: 1; }
    .part-label { font-size: 18px; font-weight: 900; color: #31d5f2; text-transform: uppercase; margin: 30px 0 10px 0; }
</style>
""", unsafe_allow_html=True)

local_css()

# --- Helpers ---
def get_img(name):
    if os.path.exists(name):
        with open(name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def bento_tile(label, title, desc, img, page_name):
    img_b64 = get_img(img)
    st.markdown(f"""
        <div class="tile-link" onclick="window.parent.sendActionToStreamlit('action=nav&page={page_name}')">
            <img src="data:image/png;base64,{img_b64}" class="tile-img">
            <div class="tile-overlay"></div>
            <div class="tile-content">
                <div class="tile-label">{label}</div>
                <div class="tile-title">{title}</div>
                <div class="tile-desc">{desc}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- State & Data ---
if 'schedule_data' not in st.session_state:
    st.session_state.schedule_data = {}
    df = st.session_state.dh.fetch_calendar()
    if not df.empty:
        for _, row in df.iterrows():
            st.session_state.schedule_data[(str(row['Dzień']), int(row['Godzina']))] = {'name': row['Klient'], 'type': row['Typ'], 'status': row['Status']}

if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'selected_date' not in st.session_state: st.session_state.selected_date = datetime.date.today()
if 'mini_cal_date' not in st.session_state: st.session_state.mini_cal_date = datetime.date.today().replace(day=1)

# --- Action Handler ---
js_input = st.text_input("js_data_exchange", label_visibility="collapsed")
if js_input:
    try:
        parts = dict(p.split('=') for p in js_input.split('&'))
        action = parts.get('action')
        if action == "nav":
            st.session_state.page = parts.get("page")
            if "client" in parts: st.query_params["client"] = parts["client"]
            if "h" in parts: st.query_params["hour"] = parts["h"]
            if "date" in parts: st.query_params["date"] = parts["date"]
            st.rerun()
        elif action == "delete":
            d, h = parts.get("d"), int(parts.get("h"))
            if (d, h) in st.session_state.schedule_data:
                st.session_state.schedule_data[(d, h)]['status'] = 'deleted'
                st.session_state.dh.update_calendar_event(d, h, "", "", 'deleted')
                st.rerun()
        elif action == "select_date":
            st.session_state.selected_date = datetime.date(int(parts.get("y")), int(parts.get("m")), int(parts.get("d")))
            st.rerun()
    except: pass

# --- UI Layout ---
st.markdown('<div class="main-layout">', unsafe_allow_html=True)
c_side, c_main = st.columns([1, 4])

with c_side:
    # Dowodzenie Panel
    sd = st.session_state.selected_date
    st.markdown(f"""
    <div style="background:#1c1c1e; padding:20px; border-radius:24px; border:1px solid #31d5f2; margin-bottom:20px;">
        <div class="tile-label">DOWODZENIE</div>
        <div style="font-size:20px; font-weight:800; color:white; margin-top:10px;">{sd.strftime("%d.%m.%Y")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    bento_tile("ADMINISTRACJA", "Dodaj dane", "Treningi i pomiary", "tile_add_data_1778074195381.png", "add_data")
    bento_tile("ZARZĄDZANIE", "Klienci", "Baza podopiecznych", "tile_clients_1778074239507.png", "clients")
    bento_tile("USTAWIENIA", "Konfiguracja", "Reset bazy", "tile_settings_1778074463560.png", "settings")

with c_main:
    if st.session_state.page == "home":
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        start_w = sd - datetime.timedelta(days=sd.weekday())
        week_dates = [start_w + datetime.timedelta(days=i) for i in range(6)]
        
        # Header
        h_html = '<div class="calendar-grid-header"><div class="day-header"></div>'
        for d in week_dates:
            today_c = "today" if d == datetime.date.today() else ""
            h_html += f'<div class="day-header {today_c}">{d.strftime("%a")}<br>{d.day}.{d.month}</div>'
        st.markdown(h_html + '</div>', unsafe_allow_html=True)
        
        # Grid
        for h in range(6, 22):
            r_html = f'<div class="calendar-row"><div class="time-col">{h}:00</div>'
            for d in week_dates:
                ds = d.strftime("%Y-%m-%d")
                ev = st.session_state.schedule_data.get((ds, h))
                if ev and ev['status'] == 'active':
                    r_html += f'<div class="calendar-cell"><div class="event-card" onclick="window.parent.sendActionToStreamlit(\'action=nav&page=add_data&client={ev["name"]}&h={h}&date={ds}\')"><div class="event-name">{ev["name"]}</div><div class="event-type">{ev["type"]}</div></div></div>'
                else:
                    r_html += f'<div class="calendar-cell"><div class="add-btn" onclick="window.parent.sendActionToStreamlit(\'action=nav&page=add_data&h={h}&date={ds}\')">+</div></div>'
            st.markdown(r_html + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == "add_data":
        st.title("📝 Rejestracja Treningu")
        # Simplified for now to ensure it works
        c1, c2, c3 = st.columns([2,1,1])
        with c1: klient = st.selectbox("Klient", get_clients())
        with c2: d_sel = st.date_input("Data", value=datetime.date.today())
        with c3: h_sel = st.number_input("Godzina", 6, 22, 12)
        
        if st.button("✅ ZAPISZ TRENING", type="primary", use_container_width=True):
            st.session_state.dh.update_calendar_event(d_sel.strftime("%Y-%m-%d"), h_sel, klient, "Trening", 'active')
            st.session_state.schedule_data[(d_sel.strftime("%Y-%m-%d"), h_sel)] = {'name': klient, 'type': 'Trening', 'status': 'active'}
            st.success("Zapisano!")
            time.sleep(1)
            st.session_state.page = "home"
            st.rerun()
            
        if st.button("🏠 POWRÓT", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    elif st.session_state.page == "settings":
        st.title("⚙️ Ustawienia")
        if st.button("🚨 RESTART BAZY DANYCH", type="primary"):
            ws_cli = st.session_state.dh.get_worksheet("Klienci")
            if ws_cli:
                ws_cli.clear()
                ws_cli.append_row(["Imię i Nazwisko", "Data", "Notatki"])
                for k in ["Maciej Stawski", "Paweł Frencel", "Pawel", "Ewa", "Ania", "Justyna"]:
                    ws_cli.append_row([k, "2026-05-08", ""])
            st.success("Restart zakończony!")
            st.rerun()
        if st.button("🏠 POWRÓT", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- CRITICAL JS BRIDGE ---
st.markdown("""
<script>
window.parent.sendActionToStreamlit = function(data) {
    const parentDoc = window.parent.document;
    const inputs = Array.from(parentDoc.querySelectorAll('input'));
    const input = inputs.find(el => el.getAttribute('aria-label') === 'js_data_exchange' || el.placeholder === 'js_data_exchange');
    if (input) {
        input.value = data;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    }
}
</script>
""", unsafe_allow_html=True)
