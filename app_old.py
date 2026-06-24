import streamlit as st

st.set_page_config(
    page_title="Cardiology IP Patient Review System",
    layout="wide"
)

# =========================
# HEADER
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:10px;
border-radius:8px;
text-align:center;">
<h2 style="color:white;margin:0;">
🏥 Cardiology IP Patient Review System
</h2>
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================
# PATIENT DETAILS
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Patient Details
</h4>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6,c7 = st.columns([2,1,2,2,1,1,2])

with c1:
    ward_name = st.selectbox(
        "Ward Name",
        [
            "DIALYSIS","DAY CARE","SINGLE","MICU","AMCU",
            "EMERGENCY","DELUXE","ICCU","TWIN SHARING",
            "GENERAL WARD","HDU","PICU","TRIPLE SHARING",
            "SICU","NICU","CTICU"
        ]
    )

with c2:
    room_no = st.text_input("Room No")

with c3:
    patient_name = st.text_input("Patient Name")

with c4:
    ip_no = st.text_input("IP No")

with c5:
    age = st.number_input("Age", 0, 120)

with c6:
    gender = st.selectbox(
        "Gender",
        ["MALE","FEMALE"]
    )

with c7:
    doctor_name = st.selectbox(
        "Doctor Name",
        [
            "Dr.V.S RAMCHANDRA",
            "Dr.SIVA KUMAR REDDY S",
            "Dr.Pranavi",
            "Dr. Raviteja",
            "Dr.BARANI VELAN S"
        ]
    )

# =========================
# CLINICAL DETAILS
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Clinical Details
</h4>
</div>
""", unsafe_allow_html=True)

col1,col2 = st.columns(2)

with col1:
    triage = st.selectbox(
        "Triage",
        ["Red","Yellow","Green"]
    )

with col2:
    disease_bucket = st.selectbox(
        "Disease Bucket",
        [
            "ACS",
            "Chronic CAD",
            "HF",
            "Rhythm/EP",
            "Device",
            "Valve",
            "Shock",
            "Pulmonary",
            "Pericardial / Myocardial"
        ]
    )

diagnosis = st.text_area("Diagnosis", height=80)

pmh = st.text_area(
    "Past Medical History",
    height=80
)

presentation = st.text_area(
    "Presentation",
    height=80
)

# =========================
# INVESTIGATIONS
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Investigations
</h4>
</div>
""", unsafe_allow_html=True)

i1,i2,i3 = st.columns(3)

with i1:
    ecg = st.text_area("ECG", height=80)

with i2:
    echo = st.text_area("ECHO", height=80)

with i3:
    ef = st.text_input("EF")

# =========================
# LABS
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Labs
</h4>
</div>
""", unsafe_allow_html=True)

l1,l2,l3,l4,l5,l6 = st.columns(6)

with l1:
    trop = st.text_input("Trop")

with l2:
    cr = st.text_input("Cr")

with l3:
    k = st.text_input("K")

with l4:
    hb = st.text_input("Hb")

with l5:
    bnp = st.text_input("BNP")

with l6:
    lac = st.text_input("Lac")

others = st.text_input("Others")

# =========================
# DONE SO
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Done So
</h4>
</div>
""", unsafe_allow_html=True)

done_so = st.text_area(
    "Done So",
    height=60
)

# =========================
# HEMODYNAMICS
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Hemodynamics
</h4>
</div>
""", unsafe_allow_html=True)

h1,h2,h3,h4,h5 = st.columns(5)

with h1:
    profile = st.selectbox(
        "Profile",
        ["Warm","Cold"]
    )

with h2:
    volume_status = st.selectbox(
        "Volume Status",
        ["Dry","Wet"]
    )

with h3:
    ivc_status = st.selectbox(
        "IVC Status",
        ["Collapsing","Non-Collapsing"]
    )

with h4:
    support = st.selectbox(
        "Support",
        [
            "Nil",
            "Inotropes",
            "Vasopressors",
            "Mechanical"
        ]
    )

with h5:
    net_fluid_balance = st.text_input(
        "Net Fluid Balance"
    )

# =========================
# MANAGEMENT
# =========================

st.markdown("""
<div style="
background-color:#0D5C63;
padding:5px;
border-radius:5px;">
<h4 style="color:white;text-align:center;margin:0;">
Management
</h4>
</div>
""", unsafe_allow_html=True)

drugs = st.text_area(
    "Drugs",
    height=80
)

s1,s2 = st.columns(2)

with s1:
    status1 = st.selectbox(
        "Status 1",
        ["Stable","Unstable"]
    )

with s2:
    status2 = st.selectbox(
        "Status 2",
        ["Improving","Same","Worsening"]
    )

plan = st.text_area(
    "Plan",
    height=80
)

questions = st.text_area(
    "Questions",
    height=80
)

st.write("")

st.button("💾 SAVE REVIEW")