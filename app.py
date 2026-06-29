import streamlit as st
import sqlite3
from datetime import datetime
import base64
import json
import threading
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

DB_NAME = "cardiology_review.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""CREATE TABLE IF NOT EXISTS patient_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ward_name TEXT, room_no TEXT, patient_name TEXT,
        ip_no TEXT, age TEXT, gender TEXT, doctor_name TEXT,
        triage TEXT, disease_bucket TEXT,
        diagnosis TEXT, past_medical_history TEXT, presentation TEXT,
        ecg TEXT, echo TEXT, ef TEXT,
        trop TEXT, cr TEXT, k TEXT, hb TEXT, bnp TEXT, lac TEXT, others TEXT,
        done_so TEXT, profile TEXT, volume_status TEXT, ivc_status TEXT,
        support TEXT, net_fluid_balance TEXT,
        drugs TEXT, status1 TEXT, status2 TEXT, plan TEXT, questions TEXT,
        entry_date TEXT, entry_time TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        display_name TEXT)""")
    users = [
        ("Dr.V.S RAMCHANDRA",    "12345", "Dr. V.S Ramchandra"),
        ("Dr.SIVA KUMAR REDDY S","12345", "Dr. Siva Kumar Reddy S"),
        ("Dr.Pranavi",           "12345", "Dr. Pranavi"),
        ("Dr. Raviteja",         "12345", "Dr. Raviteja"),
        ("Dr.BARANI VELAN S",    "12345", "Dr. Barani Velan S"),
        ("Janakiram",            "12345", "Janakiram"),
        ("Admin",                "12345", "Admin"),
        ("Mohan Krishna",        "12345", "Mohan Krishna"),
    ]
    for u,p,d in users:
        conn.execute("INSERT OR IGNORE INTO users (username,password,display_name) VALUES (?,?,?)",(u,p,d))
    conn.commit(); conn.close()

def check_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    row = conn.execute("SELECT display_name FROM users WHERE username=? AND password=?",(username,password)).fetchone()
    conn.close()
    return row[0] if row else None

def change_password(username, new_password):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE users SET password=? WHERE username=?",(new_password, username))
    conn.commit(); conn.close()

init_db()

def save_review(d):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""INSERT INTO patient_reviews (
        ward_name,room_no,patient_name,ip_no,age,gender,doctor_name,
        triage,disease_bucket,diagnosis,past_medical_history,presentation,
        ecg,echo,ef,trop,cr,k,hb,bnp,lac,others,done_so,
        profile,volume_status,ivc_status,support,net_fluid_balance,
        drugs,status1,status2,plan,questions,entry_date,entry_time
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        d.get("ward",""),d.get("room_no",""),d.get("patient_name",""),
        d.get("ip_no",""),d.get("age",""),d.get("gender",""),d.get("doctor_name",""),
        d.get("triage",""),d.get("disease_bucket",""),
        d.get("diagnosis",""),d.get("past_medical_history",""),d.get("presentation",""),
        d.get("ecg",""),d.get("echo",""),d.get("ef",""),
        d.get("trop",""),d.get("cr",""),d.get("k",""),d.get("hb",""),
        d.get("bnp",""),d.get("lac",""),d.get("others",""),d.get("done_so",""),
        d.get("profile",""),d.get("volume_status",""),d.get("ivc_status",""),
        d.get("support",""),d.get("net_fluid_balance",""),
        d.get("drugs",""),d.get("status1",""),d.get("status2",""),
        d.get("plan",""),d.get("questions",""),
        datetime.now().strftime("%d-%m-%Y"),datetime.now().strftime("%H:%M:%S")
    ))
    conn.commit(); conn.close()

def get_all():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM patient_reviews ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_record(rid):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM patient_reviews WHERE id=?", (rid,))
    conn.commit(); conn.close()

def get_record(rid):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.execute("SELECT * FROM patient_reviews WHERE id=?", (rid,))
    row = cur.fetchone()
    cols = [d[0] for d in cur.description]
    conn.close()
    return dict(zip(cols, row)) if row else {}

def update_record(rid, d):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""UPDATE patient_reviews SET
        ward_name=?,room_no=?,patient_name=?,ip_no=?,age=?,gender=?,doctor_name=?,
        triage=?,disease_bucket=?,diagnosis=?,past_medical_history=?,presentation=?,
        ecg=?,echo=?,trop=?,cr=?,k=?,hb=?,bnp=?,lac=?,others=?,done_so=?,
        profile=?,volume_status=?,ivc_status=?,support=?,net_fluid_balance=?,
        drugs=?,status1=?,status2=?,plan=?,questions=?
        WHERE id=?""", (
        d.get("ward",""),d.get("room_no",""),d.get("patient_name",""),
        d.get("ip_no",""),d.get("age",""),d.get("gender",""),d.get("doctor_name",""),
        d.get("triage",""),d.get("disease_bucket",""),
        d.get("diagnosis",""),d.get("past_medical_history",""),d.get("presentation",""),
        d.get("ecg",""),d.get("echo",""),
        d.get("trop",""),d.get("cr",""),d.get("k",""),d.get("hb",""),
        d.get("bnp",""),d.get("lac",""),d.get("others",""),d.get("done_so",""),
        d.get("profile",""),d.get("volume_status",""),d.get("ivc_status",""),
        d.get("support",""),d.get("net_fluid_balance",""),
        d.get("drugs",""),d.get("status1",""),d.get("status2",""),
        d.get("plan",""),d.get("questions",""), rid
    ))
    conn.commit(); conn.close()

# ── HTTP Server ──────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            save_review(data)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args): pass

def start_server():
    try:
        server = HTTPServer(('localhost', 8502), Handler)
        server.serve_forever()
    except: pass

if "server_started" not in st.session_state:
    threading.Thread(target=start_server, daemon=True).start()
    st.session_state["server_started"] = True

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Cardiology IP Patient Review System", page_icon="🏥", layout="wide")

try:
    with open("logo.png","rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{b64}" style="width:60px;display:block;margin:0 auto 3px auto;"/>'
except:
    logo_html = '<div style="font-size:36px;text-align:center">🏥</div>'

# ── LOGIN GATE ──────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["display_name"] = ""

if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
    [data-testid="stStatusWidget"],.stDeployButton,#MainMenu,footer{display:none!important}
    .stApp{background:linear-gradient(135deg,#0B3D47 0%,#0B6E75 60%,#0d9199 100%)!important}
    .main .block-container{
        margin-top:-80px!important;padding:0!important;
        max-width:340px!important;margin-left:auto!important;margin-right:auto!important}
    div[data-testid="stVerticalBlock"],div[data-testid="stVerticalBlock"]>div{
        gap:2px!important;padding:0!important;margin:0!important}
    div[data-testid="stSelectbox"] label{
        font-size:15px!important;font-weight:800!important;color:#fff!important;
        text-shadow:0 1px 4px rgba(0,0,0,0.5)!important;margin-bottom:3px!important}
    div[data-testid="stTextInput"] label{
        font-size:15px!important;font-weight:800!important;color:#fff!important;
        text-shadow:0 1px 4px rgba(0,0,0,0.5)!important;margin-bottom:3px!important}
    div[data-testid="stSelectbox"]>div>div{
        border:1.5px solid #b8d0d4!important;border-radius:7px!important;font-size:13px!important;background:#fff!important}
    div[data-testid="stTextInput"]>div>div>input{
        border:1.5px solid #b8d0d4!important;border-radius:7px!important;font-size:13px!important;padding:6px 12px!important;background:#fff!important}
    div[data-testid="stFormSubmitButton"]>button{
        background:linear-gradient(90deg,#0B3D47,#0B6E75)!important;
        color:#fff!important;font-size:14px!important;font-weight:800!important;
        border:none!important;border-radius:8px!important;height:40px!important;
        width:100%!important;letter-spacing:1px!important;margin-top:6px!important}
    div[data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important}
    </style>
    """, unsafe_allow_html=True)

    try:
        with open("logo.png","rb") as f:
            lb64 = base64.b64encode(f.read()).decode()
        limg = f'<img src="data:image/png;base64,{lb64}" style="width:72px;display:block;margin:0 auto 8px auto;"/>'
    except:
        limg = '<div style="font-size:48px;text-align:center">🏥</div>'

    st.markdown(f"""
    <div style="background:#fff;border-radius:14px;padding:20px 24px 16px 24px;
                box-shadow:0 6px 30px rgba(0,0,0,0.25);margin-top:80px;margin-bottom:16px;text-align:center">
    {limg}
    <div style="color:#0B3D47;font-size:1.1rem;font-weight:800;margin:6px 0 2px 0;line-height:1.3">Cardiology IP Patient Review System</div>
    <div style="color:#0B6E75;font-size:10px;font-weight:600;letter-spacing:3px">ﮩ٨ـﮩﮩ٨ـ❤️ﮩ٨ـﮩﮩ٨ـ</div>
    </div>
    """, unsafe_allow_html=True)

    ALL_USERS = ["Dr.V.S RAMCHANDRA","Dr.SIVA KUMAR REDDY S","Dr.Pranavi",
                 "Dr. Raviteja","Dr.BARANI VELAN S","Janakiram","Admin","Mohan Krishna"]

    with st.form("login_form"):
        uname = st.selectbox("👤 Select User", ALL_USERS)
        pwd   = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        login_btn = st.form_submit_button("🔐 LOGIN")

    if login_btn:
        dn = check_login(uname, pwd)
        if dn:
            st.session_state["logged_in"] = True
            st.session_state["username"]  = uname
            st.session_state["display_name"] = dn
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")

    st.markdown('<div style="text-align:center;color:rgba(255,255,255,0.7);font-size:11px;font-weight:600;margin-top:12px">Sri Sri Holistic Hospitals</div>', unsafe_allow_html=True)
    st.stop()

# ── LOGGED IN — show full app ────────────────────────────────
st.markdown("""
<style>
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],.stDeployButton,#MainMenu,footer{display:none!important}
.stApp{margin-top:0!important;padding-top:0!important;overflow-x:hidden!important}
.main{padding-top:0!important}
.main .block-container{padding:0 12px!important;margin-top:-120px!important;max-width:100%!important}
div[data-testid="stVerticalBlock"],div[data-testid="stVerticalBlock"]>div{gap:0!important;padding:0!important;margin:0!important}
div[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:4px!important;margin-bottom:4px!important}
div[data-testid="stTabs"] [data-baseweb="tab"]{
    background:#e8f4f5!important;border-radius:6px 6px 0 0!important;
    font-weight:700!important;color:#0B3D47!important;padding:8px 28px!important;font-size:16px!important}
div[data-testid="stTabs"] [aria-selected="true"]{
    background:linear-gradient(90deg,#0B6E75,#0d9199)!important;color:#fff!important}
div[data-testid="stTabs"] [data-baseweb="tab-panel"]{padding:0!important}

/* search inputs */
div[data-testid="stTextInput"] label{font-size:14px!important;font-weight:700!important;color:#0B3D47!important;margin-bottom:3px!important}
div[data-testid="stTextInput"]>div>div>input{font-size:13px!important;padding:4px 10px!important;border:1px solid #b8d0d4!important;border-radius:5px!important}
div[data-testid="stRadio"] label{font-size:13px!important;font-weight:600!important;color:#0B3D47!important}
div[data-testid="stRadio"]>div{gap:6px!important}

/* table */
.rec-table{width:100%;border-collapse:collapse;font-size:13px;margin-top:4px}
.rec-table th{background:linear-gradient(90deg,#0B3D47,#0B6E75);color:#fff;padding:7px 10px;text-align:left;font-size:13px;font-weight:800;white-space:nowrap;letter-spacing:.3px}
.rec-table td{padding:6px 10px;border-bottom:1px solid #c8e6ea;vertical-align:middle;white-space:nowrap;font-weight:600;color:#1a3a3f;font-size:13px}
.rec-table tr:nth-child(odd) td{background:#e8f6f7}
.rec-table tr:nth-child(even) td{background:#d0eef1}
.rec-table tr:hover td{background:#b2e0e5!important;transition:background .15s}

.sh{background:linear-gradient(90deg,#0B6E75,#0d9199);color:#fff;padding:5px 12px;border-radius:5px;font-weight:800;font-size:13px;letter-spacing:.5px;margin:3px 0 6px 0;display:block}
.ttl{text-align:center;color:#0B3D47;font-size:1.75rem;font-weight:800;margin:3px 0 1px 0}
.hbl{text-align:center;color:#0B6E75;font-size:14px;letter-spacing:4px;margin:0 0 4px 0}
.footer{text-align:center;color:#0B6E75;font-size:11px;font-weight:600;padding:3px 0 2px 0}

div[data-testid="stFormSubmitButton"]>button{
    background:linear-gradient(90deg,#0B6E75,#0d9199)!important;
    color:#fff!important;font-weight:800!important;border:none!important;border-radius:6px!important}
div[data-testid="stForm"]{border:none!important;padding:0!important}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""{logo_html}
<div class="ttl">Cardiology IP Patient Review System</div>
<div class="hbl">ﮩ٨ـﮩﮩ٨ـ❤️ﮩ٨ـﮩﮩ٨ـ</div>""", unsafe_allow_html=True)



# ── Tabs ─────────────────────────────────────────────────────
# User bar — floating right above tabs using markdown
st.markdown(f'''
<style>
.topbar{{display:flex;justify-content:flex-end;align-items:center;gap:6px;margin-bottom:2px}}
.topbar-name{{font-size:12px;font-weight:700;color:#0B3D47}}
div[data-testid="stTabs"]{{width:100%!important}}
</style>
<div class="topbar">
  <span class="topbar-name">👤 {st.session_state["display_name"]}</span>
</div>
''', unsafe_allow_html=True)

_btnc = st.columns([6,0.5,0.5])
if _btnc[1].button("🔑", key="pwdbtn", help="Change Password"):
    st.session_state["show_pwd"] = not st.session_state.get("show_pwd", False)
if _btnc[2].button("🚪", key="lgout", help="Logout"):
    for k in ["logged_in","username","display_name","show_pwd"]:
        st.session_state.pop(k, None)
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📝 New Review", "📋 View Records", "📊 Dashboard"])

# Change password panel
if st.session_state.get("show_pwd"):
    with st.expander("🔑 Change Password", expanded=True):
        with st.form("chpwd"):
            old_p = st.text_input("Current Password", type="password")
            new_p = st.text_input("New Password", type="password")
            con_p = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("✅ Update Password"):
                if check_login(st.session_state["username"], old_p):
                    if new_p == con_p and len(new_p) >= 4:
                        change_password(st.session_state["username"], new_p)
                        st.success("✅ Password changed!")
                        st.session_state["show_pwd"] = False
                        st.rerun()
                    elif new_p != con_p:
                        st.error("❌ Passwords do not match!")
                    else:
                        st.error("❌ Min 4 characters needed!")
                else:
                    st.error("❌ Current password incorrect!")

# ════════════════════════════════════════════════════════════
# TAB 1 — NEW REVIEW FORM
# ════════════════════════════════════════════════════════════
with tab1:
    from streamlit.components.v1 import html as st_html

    form_html = f"""<!DOCTYPE html><html><head><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#fff;padding:3px 4px 4px 4px}}
.sh{{background:linear-gradient(90deg,#0B6E75,#0d9199);color:#fff;padding:5px 12px;border-radius:5px;font-weight:800;font-size:13px;letter-spacing:.5px;margin:3px 0 2px 0;display:block}}
.lbl{{font-size:13px;font-weight:700;color:#0B3D47;display:block;margin-bottom:1px;margin-top:2px}}
input[type=text],select,textarea{{width:100%;font-size:13px;color:#333;background:#fff;border:1px solid #b8d0d4;border-radius:4px;padding:3px 7px;outline:none;font-family:'Segoe UI',Arial,sans-serif}}
input[type=text]{{height:29px}}select{{height:29px;cursor:pointer}}textarea{{resize:none;padding:3px 7px}}
input[type=text]:focus,select:focus,textarea:focus{{border-color:#0B6E75;box-shadow:0 0 0 2px rgba(11,110,117,.12)}}
.row{{display:flex;gap:5px;width:100%}}.col{{flex:1;min-width:0}}
.savebtn{{display:block;width:240px;margin:6px auto 3px auto;background:linear-gradient(90deg,#0B6E75,#0d9199);color:#fff;font-size:13.5px;font-weight:800;letter-spacing:2px;border:none;border-radius:7px;height:38px;cursor:pointer;box-shadow:0 3px 10px rgba(11,110,117,.3)}}
.footer{{text-align:center;color:#0B6E75;font-size:11px;font-weight:600;padding:3px 0 2px 0}}
</style></head><body>
<form id="F">
<div class="sh">👤&nbsp; 1. PATIENT DETAILS</div>
<div class="row">
  <div class="col" style="flex:1.5"><span class="lbl">Ward</span><select name="ward"><option>CTICU</option><option>DIALYSIS</option><option>DAY CARE</option><option>SINGLE</option><option>MICU</option><option>AMCU</option><option>EMERGENCY</option><option>DELUXE</option><option>ICCU</option><option>TWIN SHARING</option><option>GENERAL WARD</option><option>HDU</option><option>PICU</option><option>TRIPLE SHARING</option><option>SICU</option><option>NICU</option></select></div>
  <div class="col"><span class="lbl">Room No</span><input type="text" name="room_no" placeholder="Enter Room No"/></div>
  <div class="col" style="flex:2"><span class="lbl">Patient Name</span><input type="text" name="patient_name" placeholder="Enter Patient Name"/></div>
  <div class="col" style="flex:1.5"><span class="lbl">IP No</span><input type="text" name="ip_no" placeholder="Enter IP No"/></div>
  <div class="col" style="flex:0.7"><span class="lbl">Age</span><input type="text" name="age" placeholder="Age"/></div>
  <div class="col"><span class="lbl">Gender</span><select name="gender"><option value="">Select Gender</option><option>MALE</option><option>FEMALE</option></select></div>
  <div class="col" style="flex:2"><span class="lbl">Dr. Name</span><select name="doctor_name"><option value="">Select Doctor</option><option>Dr.V.S RAMCHANDRA</option><option>Dr.SIVA KUMAR REDDY S</option><option>Dr.Pranavi</option><option>Dr. Raviteja</option><option>Dr.BARANI VELAN S</option></select></div>
</div>
<div class="sh">🗒️&nbsp; 2. CLINICAL DETAILS &amp; Investigations</div>
<div class="row">
  <div class="col"><span class="lbl">Triage</span><select name="triage"><option value="">Select Triage</option><option>Red</option><option>Yellow</option><option>Green</option></select></div>
  <div class="col" style="flex:1.5"><span class="lbl">Disease Bucket</span><select name="disease_bucket"><option value="">Select Disease Bucket</option><option>ACS</option><option>Chronic CAD</option><option>HF</option><option>Rhythm/EP</option><option>Device</option><option>Valve</option><option>Shock</option><option>Pulmonary</option><option>Pericardial / Myocardial</option></select></div>
  <div class="col" style="flex:1.5"><span class="lbl">ECG</span><input type="text" name="ecg" placeholder="Enter ECG Findings"/></div>
  <div class="col" style="flex:1.5"><span class="lbl">ECHO</span><input type="text" name="echo" placeholder="Enter ECHO Findings"/></div>
</div>
<div class="row" style="margin-top:2px">
  <div class="col"><span class="lbl">Diagnosis</span><textarea name="diagnosis" style="height:36px" placeholder="Enter Diagnosis"></textarea></div>
  <div class="col"><span class="lbl">Past Medical History</span><textarea name="past_medical_history" style="height:36px" placeholder="Enter Past Medical History"></textarea></div>
  <div class="col"><span class="lbl">Presentation</span><textarea name="presentation" style="height:36px" placeholder="Enter Presentation"></textarea></div>
</div>
<div class="sh">🧪&nbsp; 3. LABS &nbsp;( MANUAL ENTRY)</div>
<div class="row">
  <div class="col"><span class="lbl">Trop</span><input type="text" name="trop" placeholder="Trop"/></div>
  <div class="col"><span class="lbl">Cr</span><input type="text" name="cr" placeholder="Cr"/></div>
  <div class="col"><span class="lbl">K⁺</span><input type="text" name="k" placeholder="K"/></div>
  <div class="col"><span class="lbl">Hb</span><input type="text" name="hb" placeholder="Hb"/></div>
  <div class="col"><span class="lbl">BNP</span><input type="text" name="bnp" placeholder="BNP"/></div>
  <div class="col"><span class="lbl">Lac</span><input type="text" name="lac" placeholder="Lac"/></div>
  <div class="col"><span class="lbl">Others</span><input type="text" name="others" placeholder="Others"/></div>
</div>
<div class="row" style="gap:4px;margin-top:2px">
  <div style="flex:1;min-width:0"><div class="sh">✅&nbsp; 4. DONE SO</div><textarea name="done_so" style="width:100%;height:40px" placeholder="Enter Done So"></textarea></div>
  <div style="flex:2;min-width:0"><div class="sh">❤️&nbsp; 5. HEMODYNAMICS</div>
    <div class="row">
      <div class="col"><span class="lbl">Profile</span><select name="profile"><option value="">Select Profile</option><option>Warm &amp; Dry</option><option>Warm &amp; Wet</option><option>Cold &amp; Dry</option><option>Cold &amp; Wet</option></select></div>
      <div class="col"><span class="lbl">Volume Status</span><select name="volume_status"><option value="">Select</option><option>Dry</option><option>Wet</option></select></div>
      <div class="col"><span class="lbl">IVC Status</span><select name="ivc_status"><option value="">Select</option><option>Collapsing</option><option>Non-Collapsing</option></select></div>
      <div class="col"><span class="lbl">Support</span><select name="support"><option value="">Select</option><option>Nil</option><option>Inotropes</option><option>Vasopressors</option><option>Mechanical</option></select></div>
      <div class="col"><span class="lbl">Net Fluid Balance (ml)</span><input type="text" name="net_fluid_balance" placeholder="Enter ml"/></div>
    </div>
  </div>
</div>
<div class="sh">💊&nbsp; 6. MANAGEMENT</div>
<div class="row">
  <div class="col" style="flex:2"><span class="lbl">Drugs</span><textarea name="drugs" style="height:36px" placeholder="Enter Drugs"></textarea></div>
  <div class="col" style="flex:1.1"><span class="lbl">Status 1</span><select name="status1"><option value="">Select Status 1</option><option>Stable</option><option>Unstable</option></select></div>
  <div class="col" style="flex:1.1"><span class="lbl">Status 2</span><select name="status2"><option value="">Select Status 2</option><option>Improving</option><option>Same</option><option>Worsening</option></select></div>
  <div class="col" style="flex:2"><span class="lbl">Plan</span><textarea name="plan" style="height:36px" placeholder="Enter Plan"></textarea></div>
  <div class="col" style="flex:2"><span class="lbl">Questions</span><textarea name="questions" style="height:36px" placeholder="Enter Questions"></textarea></div>
</div>
<div style="text-align:center;margin-top:6px;">
  <button type="button" class="savebtn" onclick="save()">💾 SAVE REVIEW</button>
</div>
</form>
<div class="footer">Sri Sri Holistic Hospitals &nbsp;|&nbsp; Cardiology IP Patient Review System</div>
<script>
function save(){{
  var f=document.getElementById('F'),d={{}},e=f.elements;
  for(var i=0;i<e.length;i++){{if(e[i].name)d[e[i].name]=e[i].value;}}
  var now=new Date();
  var dd=String(now.getDate()).padStart(2,'0');
  var mm=String(now.getMonth()+1).padStart(2,'0');
  var yyyy=now.getFullYear();
  var hh=String(now.getHours()).padStart(2,'0');
  var mn=String(now.getMinutes()).padStart(2,'0');
  var ss=String(now.getSeconds()).padStart(2,'0');
  var payload={{
    ward_name:d.ward||"",room_no:d.room_no||"",patient_name:d.patient_name||"",
    ip_no:d.ip_no||"",age:d.age||"",gender:d.gender||"",doctor_name:d.doctor_name||"",
    triage:d.triage||"",disease_bucket:d.disease_bucket||"",
    diagnosis:d.diagnosis||"",past_medical_history:d.past_medical_history||"",
    presentation:d.presentation||"",ecg:d.ecg||"",echo:d.echo||"",ef:"",
    trop:d.trop||"",cr:d.cr||"",k:d.k||"",hb:d.hb||"",
    bnp:d.bnp||"",lac:d.lac||"",others:d.others||"",done_so:d.done_so||"",
    profile:d.profile||"",volume_status:d.volume_status||"",
    ivc_status:d.ivc_status||"",support:d.support||"",
    net_fluid_balance:d.net_fluid_balance||"",
    drugs:d.drugs||"",status1:d.status1||"",status2:d.status2||"",
    plan:d.plan||"",questions:d.questions||"",
    entry_date:dd+'-'+mm+'-'+yyyy,
    entry_time:hh+':'+mn+':'+ss
  }};
  fetch('https://wurnlslilwzcqsqbdoui.supabase.co/rest/v1/patient_reviews',{{
    method:'POST',
    headers:{{
      'Content-Type':'application/json',
      'apikey':'sb_publishable_08eTaF8VfSa-oXM63NM7ew_MZHyk-_l',
      'Authorization':'Bearer sb_publishable_08eTaF8VfSa-oXM63NM7ew_MZHyk-_l',
      'Prefer':'return=minimal'
    }},
    body:JSON.stringify(payload)
  }}).then(function(r){{
    if(r.ok||r.status===201){{
      f.reset();
      var t=document.getElementById('toast');
      t.style.display='block';
      setTimeout(function(){{t.style.display='none';}},2000);
    }}else{{
      r.text().then(function(txt){{showErr('Error '+r.status+': '+txt);}});
    }}
  }}).catch(function(e){{showErr('Network error: '+e);}});
}}
function showErr(m){{var t=document.getElementById('toast');t.style.background='#c0392b';t.innerText=m;t.style.display='block';setTimeout(function(){{t.style.display='none';}},3000);}}
</script>
<div id="toast" style="display:none;position:fixed;bottom:24px;right:24px;background:#0B6E75;color:#fff;padding:12px 22px;border-radius:8px;font-size:14px;font-weight:700;z-index:9999;box-shadow:0 4px 15px rgba(0,0,0,0.2)">✅ Patient Review Saved Successfully!</div>
</body></html>"""

    st_html(form_html, height=700, scrolling=False)

# ════════════════════════════════════════════════════════════
# TAB 2 — VIEW / SEARCH / EDIT / DELETE / EXPORT
# ════════════════════════════════════════════════════════════
with tab2:
    from datetime import date, timedelta

    st.markdown('<div class="sh">🔍&nbsp; Search &amp; Filter</div>', unsafe_allow_html=True)

    # Row 1: Name + IP + Date preset all in one line
    r1c1, r1c2, r1c3 = st.columns([1.2, 1.2, 3])
    search_name = r1c1.text_input("🔎 Patient Name", placeholder="Search name...")
    search_ip   = r1c2.text_input("🔎 IP No", placeholder="Search IP...")
    with r1c3:
        st.markdown("<p style='font-size:14px;font-weight:700;color:#0B3D47;margin:0 0 4px 0'>📅 Date Filter</p>", unsafe_allow_html=True)
        preset = st.radio("dp", ["Today","Yesterday","Last Week","Month Till Date","Custom Range"],
                          horizontal=True, label_visibility="collapsed")
    today = date.today()
    if preset == "Today":
        d_from = d_to = today
    elif preset == "Yesterday":
        d_from = d_to = today - timedelta(days=1)
    elif preset == "Last Week":
        d_from = today - timedelta(days=7)
        d_to   = today
    elif preset == "Month Till Date":
        d_from = today.replace(day=1)
        d_to   = today
    else:
        cr1, cr2 = st.columns(2)
        d_from = cr1.date_input("From", value=today - timedelta(days=7), format="DD-MM-YYYY")
        d_to   = cr2.date_input("To",   value=today, format="DD-MM-YYYY")

    df = get_all()

    # Apply filters
    if search_name:
        df = df[df['patient_name'].str.contains(search_name, case=False, na=False)]
    if search_ip:
        df = df[df['ip_no'].str.contains(search_ip, case=False, na=False)]

    # Date filter
    def parse_date(s):
        try: return datetime.strptime(s, "%d-%m-%Y").date()
        except: return None

    df['_date'] = df['entry_date'].apply(parse_date)
    df = df[df['_date'].apply(lambda x: x is not None and d_from <= x <= d_to)]

    # Export + count row
    col_exp, col_count = st.columns([1,3])
    with col_exp:
        if not df.empty:
            buf = BytesIO()
            df.drop(columns=['_date']).to_excel(buf, index=False, engine='openpyxl')
            st.download_button("📥 Export Excel", buf.getvalue(),
                file_name=f"cardiology_records_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col_count:
        st.markdown(f"<p style='color:#0B6E75;font-weight:700;margin-top:8px'>Total Records: {len(df)}</p>", unsafe_allow_html=True)

    if df.empty:
        st.info("No records found for selected filters.")
    else:
        st.markdown('<div class="sh">📋 Patient Records</div>', unsafe_allow_html=True)

        show_cols = ['id','entry_date','entry_time','ward_name','room_no','patient_name',
                     'ip_no','age','gender','doctor_name','triage','disease_bucket','diagnosis','status1','status2']
        disp = df[show_cols].copy()

        # Build HTML table with edit/delete buttons handled via session state
        header = "<div style='overflow-y:auto;max-height:380px;border:1px solid #b8d0d4;border-radius:6px;width:100%'><table class='rec-table' style='width:100%;table-layout:fixed'>"
        header += "<colgroup><col style='width:35px'><col style='width:82px'><col style='width:62px'><col style='width:90px'><col style='width:48px'><col style='width:130px'><col style='width:88px'><col style='width:36px'><col style='width:55px'><col style='width:115px'><col style='width:55px'><col style='width:105px'><col style='width:130px'><col style='width:55px'><col style='width:68px'></colgroup><thead><tr><th>ID</th><th>Date</th><th>Time</th><th>Ward</th><th>Room</th><th>Patient Name</th><th>IP No</th><th>Age</th><th>Gender</th><th>Doctor</th><th>Triage</th><th>Disease</th><th>Diagnosis</th><th>St.1</th><th>St.2</th></tr></thead><tbody>"
        rows_html = ""
        for _, row in disp.iterrows():
            rid = int(row['id'])
            ov = "overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
            rows_html += f"<tr><td style='{ov}'>{rid}</td><td style='{ov}'>{row['entry_date']}</td><td style='{ov}'>{row['entry_time']}</td><td style='{ov}'>{row['ward_name']}</td><td style='{ov}'>{row['room_no']}</td><td style='{ov}'><b>{row['patient_name']}</b></td><td style='{ov}'>{row['ip_no']}</td><td style='{ov}'>{row['age']}</td><td style='{ov}'>{row['gender']}</td><td style='{ov}'>{row['doctor_name']}</td><td style='{ov}'>{row['triage']}</td><td style='{ov}'>{row['disease_bucket']}</td><td style='{ov}'>{row['diagnosis']}</td><td style='{ov}'>{row['status1']}</td><td style='{ov}'>{row['status2']}</td></tr>"
        st.markdown(header + rows_html + "</tbody></table></div>", unsafe_allow_html=True)

        # Action buttons below table
        st.markdown("<p style='font-size:12px;color:#888;margin-top:4px'>Select record ID to Edit/Delete:</p>", unsafe_allow_html=True)
        act1, act2, act3 = st.columns([1,1,4])
        sel_id = act1.number_input("Record ID", min_value=1, step=1, label_visibility="collapsed")
        if act2.button("✏️ Edit"):
            st.session_state["edit_id"] = int(sel_id)
        if act3.button("🗑️ Delete"):
            delete_record(int(sel_id))
            st.toast("🗑️ Record Deleted!", icon="✅")
            st.rerun()

        st.markdown("---")

    # ── EDIT FORM ────────────────────────────────────────────
    if "edit_id" in st.session_state:
        rid = st.session_state["edit_id"]
        rec = get_record(rid)
        if rec:
            st.markdown(f'<div class="sh">✏️ Edit Record — {rec.get("patient_name","")} (ID: {rid})</div>', unsafe_allow_html=True)

            W=["CTICU","DIALYSIS","DAY CARE","SINGLE","MICU","AMCU","EMERGENCY","DELUXE","ICCU","TWIN SHARING","GENERAL WARD","HDU","PICU","TRIPLE SHARING","SICU","NICU"]
            DR=["","Dr.V.S RAMCHANDRA","Dr.SIVA KUMAR REDDY S","Dr.Pranavi","Dr. Raviteja","Dr.BARANI VELAN S"]
            BK=["","ACS","Chronic CAD","HF","Rhythm/EP","Device","Valve","Shock","Pulmonary","Pericardial / Myocardial"]

            def idx(lst, val):
                try: return lst.index(val)
                except: return 0

            with st.form(f"edit_{rid}"):
                ec = st.columns([1.5,1,2,1.5,0.7,1,2])
                ward   = ec[0].selectbox("Ward", W, index=idx(W, rec.get("ward_name","")))
                room   = ec[1].text_input("Room No", value=rec.get("room_no",""))
                pname  = ec[2].text_input("Patient Name", value=rec.get("patient_name",""))
                ipno   = ec[3].text_input("IP No", value=rec.get("ip_no",""))
                age    = ec[4].text_input("Age", value=rec.get("age",""))
                gen    = ec[5].selectbox("Gender", ["","MALE","FEMALE"], index=idx(["","MALE","FEMALE"], rec.get("gender","")))
                doc    = ec[6].selectbox("Dr. Name", DR, index=idx(DR, rec.get("doctor_name","")))

                ec2 = st.columns([1,1.5,1.5,1.5])
                tri  = ec2[0].selectbox("Triage", ["","Red","Yellow","Green"], index=idx(["","Red","Yellow","Green"], rec.get("triage","")))
                bkt  = ec2[1].selectbox("Disease Bucket", BK, index=idx(BK, rec.get("disease_bucket","")))
                ecg  = ec2[2].text_input("ECG", value=rec.get("ecg",""))
                echo = ec2[3].text_input("ECHO", value=rec.get("echo",""))

                ec3 = st.columns(3)
                diag = ec3[0].text_area("Diagnosis", value=rec.get("diagnosis",""), height=60)
                pmh  = ec3[1].text_area("Past Medical History", value=rec.get("past_medical_history",""), height=60)
                pres = ec3[2].text_area("Presentation", value=rec.get("presentation",""), height=60)

                elc = st.columns(7)
                trop=elc[0].text_input("Trop",value=rec.get("trop",""))
                cr=elc[1].text_input("Cr",value=rec.get("cr",""))
                k=elc[2].text_input("K⁺",value=rec.get("k",""))
                hb=elc[3].text_input("Hb",value=rec.get("hb",""))
                bnp=elc[4].text_input("BNP",value=rec.get("bnp",""))
                lac=elc[5].text_input("Lac",value=rec.get("lac",""))
                oth=elc[6].text_input("Others",value=rec.get("others",""))

                fa,fb = st.columns([1,2])
                with fa:
                    done = st.text_area("Done So", value=rec.get("done_so",""), height=60)
                with fb:
                    hc = st.columns(5)
                    PROF=["","Warm & Dry","Warm & Wet","Cold & Dry","Cold & Wet"]
                    prof=hc[0].selectbox("Profile",PROF,index=idx(PROF,rec.get("profile","")))
                    vol=hc[1].selectbox("Volume Status",["","Dry","Wet"],index=idx(["","Dry","Wet"],rec.get("volume_status","")))
                    ivc=hc[2].selectbox("IVC Status",["","Collapsing","Non-Collapsing"],index=idx(["","Collapsing","Non-Collapsing"],rec.get("ivc_status","")))
                    sup=hc[3].selectbox("Support",["","Nil","Inotropes","Vasopressors","Mechanical"],index=idx(["","Nil","Inotropes","Vasopressors","Mechanical"],rec.get("support","")))
                    nfb=hc[4].text_input("Net Fluid (ml)",value=rec.get("net_fluid_balance",""))

                mc = st.columns([2,1.1,1.1,2,2])
                drg=mc[0].text_area("Drugs",value=rec.get("drugs",""),height=55)
                s1=mc[1].selectbox("Status 1",["","Stable","Unstable"],index=idx(["","Stable","Unstable"],rec.get("status1","")))
                s2=mc[2].selectbox("Status 2",["","Improving","Same","Worsening"],index=idx(["","Improving","Same","Worsening"],rec.get("status2","")))
                pln=mc[3].text_area("Plan",value=rec.get("plan",""),height=55)
                qst=mc[4].text_area("Questions",value=rec.get("questions",""),height=55)

                bc = st.columns([1,1,4])
                save_btn   = bc[0].form_submit_button("💾 Update")
                cancel_btn = bc[1].form_submit_button("❌ Cancel")

            if save_btn:
                update_record(rid, dict(
                    ward=ward,room_no=room,patient_name=pname,ip_no=ipno,age=age,
                    gender=gen,doctor_name=doc,triage=tri,disease_bucket=bkt,
                    diagnosis=diag,past_medical_history=pmh,presentation=pres,
                    ecg=ecg,echo=echo,trop=trop,cr=cr,k=k,hb=hb,bnp=bnp,lac=lac,others=oth,
                    done_so=done,profile=prof,volume_status=vol,ivc_status=ivc,
                    support=sup,net_fluid_balance=nfb,drugs=drg,status1=s1,status2=s2,
                    plan=pln,questions=qst))
                del st.session_state["edit_id"]
                st.toast("✅ Record Updated!", icon="💾")
                st.rerun()

            if cancel_btn:
                del st.session_state["edit_id"]
                st.rerun()


# ════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ════════════════════════════════════════════════════════════
with tab3:
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import date, timedelta

    # ── Dashboard CSS ────────────────────────────────────────
    st.markdown("""
    <style>
    .dash-card{background:#fff;border-radius:10px;padding:10px 14px;
               box-shadow:0 2px 12px rgba(11,110,117,0.10);border-left:4px solid #0B6E75;margin-bottom:8px}
    .dash-num{font-size:1.7rem;font-weight:900;color:#0B3D47;line-height:1}
    .dash-lbl{font-size:12px;color:#6b7f80;font-weight:700;margin-top:3px}
    .dash-sh{background:linear-gradient(90deg,#0B3D47,#0B6E75);color:#fff;
             padding:6px 14px;border-radius:7px;font-weight:800;font-size:13px;
             margin:10px 0 6px 0;display:block;letter-spacing:.5px}
    div[data-testid="stDataFrame"]{border-radius:8px;overflow:hidden}
    </style>
    """, unsafe_allow_html=True)

    # ── Date Filter ──────────────────────────────────────────
    st.markdown('<span class="dash-sh">📅 Dashboard Date Filter</span>', unsafe_allow_html=True)
    df1,df2,df3 = st.columns([1.5,1,1])
    with df1:
        dpreset = st.radio("dboard", ["Today","Yesterday","Last Week","Month Till Date","Custom Range"],
                           horizontal=True, label_visibility="collapsed")
    today = date.today()
    if dpreset == "Today":
        date_from = date_to = today
    elif dpreset == "Yesterday":
        date_from = date_to = today - timedelta(days=1)
    elif dpreset == "Last Week":
        date_from = today - timedelta(days=7); date_to = today
    elif dpreset == "Month Till Date":
        date_from = today.replace(day=1); date_to = today
    else:
        dc1,dc2,_= st.columns([1,1,2])
        date_from = dc1.date_input("From", value=today-timedelta(days=7), format="DD-MM-YYYY", key="df")
        date_to   = dc2.date_input("To",   value=today, format="DD-MM-YYYY", key="dt")

    # ── Load & filter data ───────────────────────────────────
    dfall = get_all()
    def parse_d(s):
        try: return datetime.strptime(s,"%d-%m-%Y").date()
        except: return None
    dfall["_d"] = dfall["entry_date"].apply(parse_d)
    dfilt = dfall[dfall["_d"].apply(lambda x: x is not None and date_from <= x <= date_to)].copy()

    total   = len(dfilt)
    stable   = int(dfilt["status1"].eq("Stable").sum())   if not dfilt.empty and "status1" in dfilt.columns else 0
    unstable = int(dfilt["status1"].eq("Unstable").sum()) if not dfilt.empty and "status1" in dfilt.columns else 0
    red_t    = int(dfilt["triage"].eq("Red").sum())       if not dfilt.empty and "triage"  in dfilt.columns else 0

    # ── KPI Cards ────────────────────────────────────────────
    krow = st.columns([1,1,1,1,1.2])
    krow[0].markdown(f'<div class="dash-card"><div class="dash-num">{total}</div><div class="dash-lbl">👥 Total Patients</div></div>', unsafe_allow_html=True)
    krow[1].markdown(f'<div class="dash-card" style="border-color:#27ae60"><div class="dash-num" style="color:#27ae60">{stable}</div><div class="dash-lbl">✅ Stable</div></div>', unsafe_allow_html=True)
    krow[2].markdown(f'<div class="dash-card" style="border-color:#e74c3c"><div class="dash-num" style="color:#e74c3c">{unstable}</div><div class="dash-lbl">⚠️ Unstable</div></div>', unsafe_allow_html=True)
    krow[3].markdown(f'<div class="dash-card" style="border-color:#e74c3c"><div class="dash-num" style="color:#e74c3c">{red_t}</div><div class="dash-lbl">🔴 Red Triage</div></div>', unsafe_allow_html=True)
    # Export button in 5th card slot
    with krow[4]:
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if not dfilt.empty:
            exp_buf = BytesIO()
            with pd.ExcelWriter(exp_buf, engine="openpyxl") as writer:
                # Sheet 1: All patient data
                dfilt.drop(columns=["_d"]).to_excel(writer, sheet_name="All Patients", index=False)

                # Sheet 2: Doctor summary
                today_str2 = today.strftime("%d-%m-%Y")
                doc_s = dfilt.groupby("doctor_name").agg(Month_Visits=("id","count")).reset_index()
                td2 = dfall[dfall["entry_date"]==today_str2].groupby("doctor_name").size().reset_index(name="Today_Visits")
                doc_s = doc_s.merge(td2, on="doctor_name", how="left").fillna(0)
                doc_s["Today_Visits"] = doc_s["Today_Visits"].astype(int)
                doc_s.columns = ["Doctor Name","Month Visits","Today Visits"]
                doc_s.to_excel(writer, sheet_name="Doctor Summary", index=False)

                # Sheet 3: Disease bucket breakdown
                dis_s = dfilt.groupby(["disease_bucket","status1"]).size().unstack(fill_value=0).reset_index()
                dis_s.columns.name = None
                dis_s.to_excel(writer, sheet_name="Disease Bucket", index=False)

                # Sheet 4: Triage breakdown
                tr_s = dfilt.groupby(["triage","disease_bucket"]).size().reset_index(name="Count")
                tr_s.to_excel(writer, sheet_name="Triage Summary", index=False)

                # Sheet 5: Status summary
                st_s = dfilt["status1"].value_counts().reset_index()
                st_s.columns = ["Status","Count"]
                st_s.to_excel(writer, sheet_name="Status Summary", index=False)

            st.download_button("📥 Export All (5 Sheets)", exp_buf.getvalue(),
                file_name=f"dashboard_{date_from}_{date_to}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    if dfilt.empty:
        st.info("No data for selected date range.")
    else:
        # ── Row 1: Doctor Table + Status Chart ───────────────
        st.markdown('<span class="dash-sh">👨‍⚕️ Doctor-wise Summary &nbsp;|&nbsp; 🟢 Status Distribution</span>', unsafe_allow_html=True)
        col_doc, col_status = st.columns([1.4, 1])

        with col_doc:
            today_str = today.strftime("%d-%m-%Y")
            month_str = today.strftime("%m-%Y")
            doc_grp = dfilt.groupby("doctor_name").agg(
                Month_Visits=("id","count")
            ).reset_index()
            # Today visits
            today_df = dfall[dfall["entry_date"]==today_str]
            today_doc = today_df.groupby("doctor_name").size().reset_index(name="Today_Visits")
            doc_table = doc_grp.merge(today_doc, on="doctor_name", how="left").fillna(0)
            doc_table["Today_Visits"] = doc_table["Today_Visits"].astype(int)
            doc_table.columns = ["Doctor Name","Month Visits","Today Visits"]
            doc_table = doc_table.sort_values("Month Visits", ascending=False).reset_index(drop=True)
            st.dataframe(doc_table, use_container_width=True, hide_index=True,
                column_config={
                    "Doctor Name": st.column_config.TextColumn("👨‍⚕️ Doctor", width="large"),
                    "Month Visits": st.column_config.NumberColumn("📅 Month", width="small"),
                    "Today Visits": st.column_config.NumberColumn("🗓️ Today", width="small"),
                })

        with col_status:
            status_data = dfilt["status1"].value_counts().reset_index()
            status_data.columns = ["Status","Count"]
            colors = {"Stable":"#27ae60","Unstable":"#e74c3c","":"#95a5a6"}
            fig_s = px.pie(status_data, names="Status", values="Count",
                           color="Status", color_discrete_map=colors,
                           hole=0.45)
            fig_s.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=260,
                               legend=dict(orientation="h",y=-0.15),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig_s.update_traces(textinfo="percent+label", textfont_size=12)
            st.plotly_chart(fig_s, use_container_width=True)

        # ── Row 2: Disease Bucket Pie + Table ────────────────
        st.markdown('<span class="dash-sh">🫀 Disease Bucket Distribution</span>', unsafe_allow_html=True)
        col_pie, col_dtbl = st.columns([1,1.2])

        with col_pie:
            dis_data = dfilt["disease_bucket"].replace("","Unknown").value_counts().reset_index()
            dis_data.columns = ["Disease","Count"]
            pal = ["#0B6E75","#0d9199","#1abc9c","#2ecc71","#e74c3c","#e67e22","#9b59b6","#3498db","#f39c12"]
            fig_d = px.pie(dis_data, names="Disease", values="Count",
                           color_discrete_sequence=pal, hole=0.4)
            fig_d.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=300,
                               legend=dict(orientation="v",x=1.02),
                               paper_bgcolor="rgba(0,0,0,0)")
            fig_d.update_traces(textinfo="percent+label", textfont_size=11)
            st.plotly_chart(fig_d, use_container_width=True)

        with col_dtbl:
            dis_tbl = dfilt.groupby(["disease_bucket","status1"]).size().unstack(fill_value=0).reset_index()
            dis_tbl.columns.name = None
            dis_tbl = dis_tbl.rename(columns={"disease_bucket":"Disease Bucket"})
            for col in ["Stable","Unstable","Improving","Same","Worsening"]:
                if col not in dis_tbl.columns: dis_tbl[col] = 0
            dis_tbl["Total"] = dis_tbl.select_dtypes("number").sum(axis=1)
            dis_tbl = dis_tbl.sort_values("Total", ascending=False).reset_index(drop=True)
            st.dataframe(dis_tbl, use_container_width=True, hide_index=True)

        # ── Row 3: Triage Distribution ───────────────────────
        st.markdown('<span class="dash-sh">🚨 Triage-wise Distribution</span>', unsafe_allow_html=True)
        col_tr1, col_tr2 = st.columns([1,1.3])

        with col_tr1:
            triage_data = dfilt["triage"].replace("","Unknown").value_counts().reset_index()
            triage_data.columns = ["Triage","Count"]
            triage_colors = {"Red":"#e74c3c","Yellow":"#f39c12","Green":"#27ae60","Unknown":"#95a5a6"}
            fig_t = px.bar(triage_data, x="Triage", y="Count",
                           color="Triage", color_discrete_map=triage_colors,
                           text="Count")
            fig_t.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=260,
                               showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)",
                               xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#e0eef0"))
            fig_t.update_traces(textposition="outside", textfont_size=13)
            st.plotly_chart(fig_t, use_container_width=True)

        with col_tr2:
            tr_tbl = dfilt.groupby(["triage","disease_bucket"]).size().reset_index(name="Count")
            tr_tbl.columns = ["Triage","Disease Bucket","Count"]
            tr_tbl = tr_tbl.sort_values(["Triage","Count"], ascending=[True,False]).reset_index(drop=True)
            st.dataframe(tr_tbl, use_container_width=True, hide_index=True,
                column_config={
                    "Triage": st.column_config.TextColumn("🚨 Triage"),
                    "Disease Bucket": st.column_config.TextColumn("🫀 Disease"),
                    "Count": st.column_config.NumberColumn("Count"),
                })


st.markdown('<div class="footer">Sri Sri Holistic Hospitals &nbsp;|&nbsp; Cardiology IP Patient Review System</div>', unsafe_allow_html=True)