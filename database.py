import sqlite3

conn = sqlite3.connect("cardiology_review.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patient_reviews (

id INTEGER PRIMARY KEY AUTOINCREMENT,

ward_name TEXT,
room_no TEXT,

patient_name TEXT,
ip_no TEXT,
age INTEGER,
gender TEXT,
doctor_name TEXT,

triage TEXT,
disease_bucket TEXT,

diagnosis TEXT,
past_medical_history TEXT,
presentation TEXT,

ecg TEXT,
echo TEXT,
ef TEXT,

trop TEXT,
cr TEXT,
k TEXT,
hb TEXT,
bnp TEXT,
lac TEXT,
others TEXT,

done_so TEXT,

profile TEXT,
volume_status TEXT,
ivc_status TEXT,
support TEXT,
net_fluid_balance TEXT,

drugs TEXT,

status1 TEXT,
status2 TEXT,

plan TEXT,
questions TEXT,

entry_date TEXT,
entry_time TEXT

)
""")

conn.commit()
conn.close()

print("Database Created Successfully")