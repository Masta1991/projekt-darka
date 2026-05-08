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

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trainer App v1.0",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
.stApp { background: #0d1117 !important; color: #fff; }
[data-testid="stSidebar"], header { display: none !important; }
.block-container { padding: 1.5rem 1rem !important; max-width: 100% !important; }
/* Tile */
.tile-link { display:block; position:relative; border-radius:18px; overflow:hidden;
  background:#1c1c1e; border:1px solid rgba(255,255,255,0.06); margin-bottom:10px;
  height:90px; transition:.25s; }
.tile-link:hover { border-color:#31d5f2; transform:translateX(4px); }
.tile-img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.25; filter:grayscale(1); }
.tile-overlay { position:absolute; inset:0; background:linear-gradient(90deg,rgba(13,17,23,.92) 0%,rgba(13,17,23,.4) 100%); }
.tile-content { position:relative; z-index:3; padding:12px 18px; height:100%; display:flex; flex-direction:column; justify-content:center; }
.tile-label { color:#31d5f2; font-size:9px; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; }
.tile-title { font-size:16px; font-weight:700; color:#fff; margin:2px 0; }
.tile-desc  { font-size:10px; color:#8b949e; }
/* Calendar */
.cal-wrap { background:#1c1c1e; border-radius:22px; border:1px solid rgba(255,255,255,0.05); padding:18px; overflow-x:auto; }
.cal-hdr { display:grid; grid-template-columns:55px repeat(6,1fr); gap:8px; margin-bottom:10px; }
.day-hdr { text-align:center; color:#8b949e; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.5px; }
.day-hdr.today { color:#31d5f2; }
.cal-row { display:grid; grid-template-columns:55px repeat(6,1fr); gap:8px; min-height:70px; border-top:1px solid rgba(255,255,255,0.03); }
.time-col { color:#333; font-size:10px; font-weight:700; padding-top:8px; text-align:right; padding-right:12px; }
.cal-cell { position:relative; border-radius:10px; background:rgba(255,255,255,0.01); }
.ev-card { background:rgba(49,213,242,.12); border-left:3px solid #31d5f2; border-radius:8px;
  padding:6px 10px; height:calc(100% - 8px); margin:4px; cursor:pointer; transition:.2s; }
.ev-card:hover { background:rgba(49,213,242,.22); transform:translateY(-1px); }
.ev-name { font-weight:800; font-size:12px; color:#fff; }
.ev-type { font-size:9px; color:#8b949e; }
.add-btn { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size:22px; color:rgba(255,255,255,.15); opacity:0; transition:.2s; cursor:pointer; text-decoration:none; }
.cal-cell:hover .add-btn { opacity:1; color:rgba(49,213,242,.7); }
/* Header */
.pg-title { font-size:22px; font-weight:800; color:#fff; margin-bottom:18px; }
/* Dowodzenie */
.dow-panel { background:linear-gradient(135deg,#1c1c1e,#0d1117); border:1px solid rgba(49,213,242,.35);
  border-radius:22px; padding:18px; margin-bottom:16px; }
/* Buttons */
.stButton>button { border-radius:12px !important; font-weight:700 !important; }
/* Mobile */
@media(max-width:900px) {
  .cal-hdr,.cal-row { min-width:550px; }
  .cal-wrap { overflow-x:auto; }
}
</style>
""", unsafe_allow_html=True)

# ─── Auth ────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
    .login-wrap { max-width:380px; margin:80px auto; background:#1c1c1e; border:1px solid #31d5f2;
      border-radius:24px; padding:40px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,.6); }
    .login-title { font-size:26px; font-weight:800; color:#fff; margin:12px 0 6px; }
    .login-sub { font-size:11px; color:#8b949e; margin-bottom:24px; }
    </style>
    <div class="login-wrap">
      <div class="tile-label">PROJEKT DARKA</div>
      <div class="login-title">🔐 Dostęp</div>
      <div class="login-sub">Wpisz kod dostępu aby kontynuować</div>
    </div>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Kod dostępu", type="password", label_visibility="collapsed", placeholder="Wpisz kod…")
    if pwd:
        if pwd == st.secrets.get("access_code", "170491"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Błędny kod dostępu")
    st.stop()

# ─── Data & State ────────────────────────────────────────────────────────────
if 'dh' not in st.session_state:
    st.session_state.dh = DataHandler()

if 'schedule' not in st.session_state:
    st.session_state.schedule = {}
    try:
        df = st.session_state.dh.fetch_calendar()
        if not df.empty:
            for _, row in df.iterrows():
                st.session_state.schedule[(str(row['Dzień']), int(row['Godzina']))] = {
                    'name': str(row['Klient']), 'type': str(row['Typ']), 'status': str(row['Status'])
                }
    except: pass

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

# ─── Navigation ─────────────────────────────────────────────────────────────
# Simple query_param based navigation – works 100% reliably
page = st.query_params.get("page", "home")

def go(p, **kwargs):
    st.query_params["page"] = p
    for k, v in kwargs.items():
        st.query_params[k] = str(v)
    st.rerun()

def get_clients():
    try:
        df = st.session_state.dh.fetch_clients()
        if not df.empty:
            return df.iloc[:, 0].tolist()
    except: pass
    return ["Maciej Stawski", "Paweł Frencel", "Pawel", "Ewa", "Ania", "Justyna"]

def get_img(name):
    for p in [f"assets/{name}", name]:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

# ─── Sidebar Tiles (use st.button for reliable navigation) ──────────────────
TILE_CSS = """
<style>
div[data-testid="stButton"] > button { 
  width:100%; text-align:left; background:#1c1c1e; color:#fff;
  border:1px solid rgba(255,255,255,0.06); border-radius:18px;
  padding:16px 18px; height:90px; font-size:16px; font-weight:700;
  transition:.25s; margin-bottom:8px;
}
div[data-testid="stButton"] > button:hover { border-color:#31d5f2; transform:translateX(4px); background:#252528; }
div[data-testid="stButton"] > button p { margin:0; }
</style>
"""
st.markdown(TILE_CSS, unsafe_allow_html=True)

# ─── Layout ─────────────────────────────────────────────────────────────────
c_side, c_main = st.columns([1, 4])

with c_side:
    sd = st.session_state.selected_date
    months_pl = ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec",
                 "Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]
    days_pl   = ["Poniedziałek","Wtorek","Środa","Czwartek","Piątek","Sobota","Niedziela"]
    st.markdown(f"""
    <div class="dow-panel">
      <div class="tile-label">DOWODZENIE</div>
      <div style="font-size:22px;font-weight:800;color:#fff;margin-top:8px;">{days_pl[sd.weekday()]}</div>
      <div style="font-size:14px;color:#8b949e;">{sd.day} {months_pl[sd.month-1]} {sd.year}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋  Dodaj dane\n\nTreningi i pomiary", key="nav_add"):
        go("add_data")
    if st.button("👥  Klienci\n\nBaza podopiecznych", key="nav_cli"):
        go("clients")
    if st.button("📊  Wyniki\n\nWykresy postępów", key="nav_dash"):
        go("dashboard")
    if st.button("⚙️  Ustawienia\n\nKonfiguracja aplikacji", key="nav_set"):
        go("settings")

    st.markdown("---")
    new_date = st.date_input("📅 Zmień datę", value=sd, label_visibility="collapsed")
    if new_date != sd:
        st.session_state.selected_date = new_date
        st.rerun()

# ─── MAIN CONTENT ────────────────────────────────────────────────────────────
with c_main:

    # ── HOME / CALENDAR ──────────────────────────────────────────────────────
    if page == "home":
        start_w = sd - datetime.timedelta(days=sd.weekday())
        week_dates = [start_w + datetime.timedelta(days=i) for i in range(6)]

        col_h1, col_h2 = st.columns([5, 1])
        with col_h1:
            st.markdown(f'<div style="color:#8b949e;font-size:13px;font-weight:600;padding:6px 0;">WIDOK TYGODNIA {sd.isocalendar()[1]}</div>', unsafe_allow_html=True)
        with col_h2:
            if st.button("⚙️ EDYTUJ", key="edit_btn"):
                go("home")  # placeholder

        # Calendar header
        hdr = '<div class="cal-wrap"><div class="cal-hdr"><div class="day-hdr"></div>'
        for d in week_dates:
            today_cls = "today" if d == datetime.date.today() else ""
            hdr += f'<div class="day-hdr {today_cls}">{["PON","WT","ŚR","CZW","PT","SOB"][d.weekday()]}<br><span style="font-size:10px;opacity:.6;">{d.day}.{d.month}</span></div>'
        st.markdown(hdr + '</div>', unsafe_allow_html=True)

        # Calendar rows
        for h in range(6, 22):
            row_html = f'<div class="cal-row"><div class="time-col">{h}:00</div>'
            for d in week_dates:
                ds = d.strftime("%Y-%m-%d")
                ev = st.session_state.schedule.get((ds, h))
                if ev and ev.get('status') == 'active':
                    row_html += f'<div class="cal-cell"><div class="ev-card"><div class="ev-name">{ev["name"]}</div><div class="ev-type">{ev["type"]}</div></div></div>'
                else:
                    row_html += f'<div class="cal-cell"><a href="?page=add_data&date={ds}&hour={h}" class="add-btn">+</a></div>'
            st.markdown(row_html + '</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── ADD DATA ─────────────────────────────────────────────────────────────
    elif page == "add_data":
        st.markdown('<div class="pg-title">📝 Rejestracja Treningu</div>', unsafe_allow_html=True)

        q_date_str = st.query_params.get("date", datetime.date.today().strftime("%Y-%m-%d"))
        q_hour_str = st.query_params.get("hour", "12")
        q_client   = st.query_params.get("client", get_clients()[0] if get_clients() else "")

        try:
            q_date_val = datetime.datetime.strptime(q_date_str, "%Y-%m-%d").date()
        except:
            q_date_val = datetime.date.today()

        top_c1, top_c2, top_c3 = st.columns([2, 1, 1])
        with top_c1:
            clients_list = get_clients()
            default_idx = clients_list.index(q_client) if q_client in clients_list else 0
            klient = st.selectbox("Klient", clients_list, index=default_idx)
        with top_c2:
            selected_date = st.date_input("Data", value=q_date_val)
        with top_c3:
            selected_hour = st.number_input("Godzina", min_value=6, max_value=22, value=int(q_hour_str))

        st.divider()

        EXERCISES = {
            "KLATKA PIERSIOWA": ["Wyciskanie sztangi poziomo","Wyciskanie hantli skos +","Rozpiętki","Dipsy (klatka)","Krzyżowanie linek"],
            "PLECY": ["Podciąganie na drążku","Martwy ciąg","Wiosłowanie sztangą","Ściąganie drążka","Przyciąganie dolne"],
            "NOGI": ["Przysiady","Leg Press","Wykroki","RDL","Uginanie leżąc"],
            "BARKI": ["Overhead Press","Wznosy bokiem","Wyciskanie hantli","Wznosy w opadzie","Podciąganie sztangi"],
            "TRICEPS": ["Wyciskanie wąsko","Prostowanie linki","Skullcrushers","Dipsy pionowo","Francuskie hantlem"],
            "BICEPS": ["Uginanie sztanga","Uginanie z supinacją","Modlitewnik","Uginanie młotkowe","Podciąganie podchwytem"],
            "BRZUCH": ["Unoszenie nóg","Allahy","Plank","Deadbug","Russian Twist"],
            "CARDIO": ["Bieżnia","Rowerek","Orbitek","Schody","Wioślarz"],
        }

        if 'exercises' not in st.session_state:
            st.session_state.exercises = {}

        c1, c2 = st.columns(2)
        with c1:
            main_part = st.selectbox("Główna Partia", list(EXERCISES.keys()), index=0)
            for ex in EXERCISES[main_part]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    checked = st.checkbox(ex, key=f"ex_{ex}")
                with col_b:
                    if checked:
                        w = st.number_input("kg", min_value=0.0, step=2.5, key=f"w_{ex}", label_visibility="collapsed")
                        st.session_state.exercises[ex] = w
                    elif ex in st.session_state.exercises:
                        del st.session_state.exercises[ex]

        with c2:
            extra_part = st.selectbox("Partia Uzupełniająca", ["NONE"] + list(EXERCISES.keys()), index=0)
            if extra_part != "NONE":
                for ex in EXERCISES[extra_part]:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        checked = st.checkbox(ex, key=f"ex2_{ex}")
                    with col_b:
                        if checked:
                            w = st.number_input("kg", min_value=0.0, step=2.5, key=f"w2_{ex}", label_visibility="collapsed")
                            st.session_state.exercises[ex] = w
                        elif ex in st.session_state.exercises:
                            del st.session_state.exercises[ex]

        st.divider()
        btn1, btn2, btn3 = st.columns([1, 1, 2])
        with btn1:
            if st.button("🏠 POWRÓT", use_container_width=True):
                st.session_state.exercises = {}
                go("home")
        with btn2:
            if st.button("🗑️ WYCZYŚĆ", use_container_width=True):
                st.session_state.exercises = {}
                st.rerun()
        with btn3:
            if st.button("✅ ZAPISZ TRENING", type="primary", use_container_width=True):
                ds = selected_date.strftime("%Y-%m-%d")
                try:
                    for ex, weight in st.session_state.exercises.items():
                        st.session_state.dh.save_workout_result(klient, ex, weight, selected_date.isocalendar()[1])
                    st.session_state.dh.update_calendar_event(ds, selected_hour, klient, main_part.capitalize(), 'active')
                    st.session_state.schedule[(ds, selected_hour)] = {'name': klient, 'type': main_part.capitalize(), 'status': 'active'}
                    st.success("✅ Trening zapisany!")
                    time.sleep(1)
                    st.session_state.exercises = {}
                    go("home")
                except Exception as e:
                    st.error(f"Błąd zapisu: {e}")

    # ── CLIENTS ──────────────────────────────────────────────────────────────
    elif page == "clients":
        st.markdown('<div class="pg-title">👥 Baza Podopiecznych</div>', unsafe_allow_html=True)

        clients = get_clients()
        cols = st.columns(3)
        for i, c in enumerate(clients):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:#1c1c1e;border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:20px;margin-bottom:12px;">
                  <div class="tile-label">KLIENT</div>
                  <div style="font-size:18px;font-weight:700;color:#fff;margin-top:6px;">{c}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        with st.expander("➕ Dodaj nowego klienta"):
            new_name = st.text_input("Imię i Nazwisko")
            if st.button("DODAJ", type="primary"):
                if new_name:
                    try:
                        st.session_state.dh.add_client(new_name)
                        st.success(f"Dodano: {new_name}")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd: {e}")

        if st.button("🏠 POWRÓT DO MENU", use_container_width=True, key="cli_back"):
            go("home")

    # ── SETTINGS ─────────────────────────────────────────────────────────────
    elif page == "settings":
        st.markdown('<div class="pg-title">⚙️ Ustawienia</div>', unsafe_allow_html=True)
        st.warning("⚠️ Sekcja administracyjna – używaj ostrożnie!")

        if st.button("🚨 RESTART BAZY DANYCH", type="primary", use_container_width=True):
            with st.spinner("Czyszczenie danych..."):
                try:
                    ws_cal = st.session_state.dh.get_worksheet("Kalendarz")
                    if ws_cal:
                        ws_cal.clear()
                        ws_cal.append_row(["Dzień","Godzina","Klient","Typ","Status"])

                    ws_cli = st.session_state.dh.get_worksheet("Klienci")
                    if ws_cli:
                        ws_cli.clear()
                        ws_cli.append_row(["Imię i Nazwisko","Data dołączenia","Notatki"])
                        for k in ["Maciej Stawski","Paweł Frencel","Pawel","Ewa","Ania","Justyna"]:
                            ws_cli.append_row([k, "2026-05-08", ""])

                    ws_tre = st.session_state.dh.get_worksheet("Treningi")
                    if ws_tre:
                        ws_tre.clear()
                        ws_tre.append_row(["Timestamp","Klient","Ćwiczenie","Obciążenie","Tydzień"])

                    st.session_state.schedule = {}
                    st.success("✅ Baza danych zrestartowana!")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd: {e}")

        if st.button("🏠 POWRÓT DO MENU", use_container_width=True, key="set_back"):
            go("home")

    # ── DASHBOARD ────────────────────────────────────────────────────────────
    elif page == "dashboard":
        st.markdown('<div class="pg-title">📊 Wyniki i Analityka</div>', unsafe_allow_html=True)
        st.info("Sekcja w budowie – wróć wkrótce!")
        if st.button("🏠 POWRÓT DO MENU", use_container_width=True):
            go("home")

    # ── FALLBACK ─────────────────────────────────────────────────────────────
    else:
        st.markdown(f'<div class="pg-title">🏗️ Sekcja w budowie</div>', unsafe_allow_html=True)
        if st.button("🏠 POWRÓT DO MENU", use_container_width=True):
            go("home")
