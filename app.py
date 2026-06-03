from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import base64
import os
import face_recognition
from datetime import datetime
import re
import smtplib
import requests

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

app.secret_key = "security_key_aup_system"

UPLOAD_FOLDER = "static/photos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# ADMIN PASSWORD
# =========================

ADMIN_PASSWORD = "Itcpspd@123"

# =========================
# EMAIL SETTINGS
# =========================

SENDER_EMAIL = "aupitcpspd@gmail.com"
SENDER_PASSWORD = "zacsshoqhqebqzxi"

# =========================
# DATABASE INIT
# =========================

def init_db():

    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            name TEXT,
            jh_name TEXT,
            dmt_name TEXT,
            phone TEXT,
            email TEXT,
            photo_path TEXT,
            submission_time TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# =========================
# EMAIL FUNCTION
# =========================

def send_success_email(receiver_email, employee_name):

    try:

        subject = "AUP Registration Successful"

        body = f"""
NOTE: This is an automated email. Please do not reply.

Hello {employee_name},

Your registration for DIGITALIZATION OF AUP & PASSWORD POLICY was completed successfully.

Your authentication and employee registration have been verified successfully.

Thank you.

Regards,
AUP Security System
"""

        msg = MIMEMultipart()

        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        server.sendmail(
            SENDER_EMAIL,
            receiver_email,
            msg.as_string()
        )

        server.quit()

        print("EMAIL SENT SUCCESSFULLY")

        # =========================
        # AUTO QUARTER SYSTEM
        # =========================

        now = datetime.now()

        month = now.month
        year = now.year

        if month >= 1 and month <= 3:
            current_quarter = "Q1"
            quarter_period = "January - March"
            next_quarter = "Q2"
            next_start = f"April 1, {year}"

        elif month >= 4 and month <= 6:
            current_quarter = "Q2"
            quarter_period = "April - June"
            next_quarter = "Q3"
            next_start = f"July 1, {year}"

        elif month >= 7 and month <= 9:
            current_quarter = "Q3"
            quarter_period = "July - September"
            next_quarter = "Q4"
            next_start = f"October 1, {year}"

        else:
            current_quarter = "Q4"
            quarter_period = "October - December"
            next_quarter = "Q1"
            next_start = f"January 1, {year + 1}"

        # =========================
        # SECOND EMAIL
        # =========================

        policy_subject = f"AUP & Password Policy Update - {current_quarter}"

        policy_body = f"""
Hello {employee_name},

This email contains the currently active AUP & Password Policies.

Current Quarter:
{current_quarter} ({quarter_period}) - {year}

Next Quarter:
{next_quarter}

Next Policy Activation Date:
{next_start}

Important Employee Instructions:

- Employees must update passwords regularly.
- Password sharing is prohibited.
- Face authentication is mandatory.
- Employees must follow cybersecurity rules.
- Employees must review updated policies every quarter.

Regards,
AUP Security System
"""

        policy_msg = MIMEMultipart()
        policy_msg['From'] = SENDER_EMAIL
        policy_msg['To'] = receiver_email
        policy_msg['Subject'] = policy_subject

        policy_msg.attach(MIMEText(policy_body, 'plain'))

        server2 = smtplib.SMTP('smtp.gmail.com', 587)
        server2.starttls()
        server2.login(SENDER_EMAIL, SENDER_PASSWORD)

        server2.sendmail(
            SENDER_EMAIL,
            receiver_email,
            policy_msg.as_string()
        )

        server2.quit()

        print("SECOND EMAIL SENT")

    except Exception as e:
        print("EMAIL ERROR:", e)

# =========================
# SMS FUNCTION
# =========================

def send_sms(phone, employee_name):

    message = f"""
Hello {employee_name},

Your registration for DIGITALIZATION OF AUP & PASSWORD POLICY was completed successfully.

Regards,
AUP Security System
"""

    try:

        response = requests.post(
            'https://textbelt.com/text',
            {
                'phone': phone,
                'message': message,
                'key': 'textbelt'
            }
        )

        print(response.json())

    except Exception as e:
        print("SMS ERROR:", e)

# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/selection")
def selection():
    return render_template("selection.html")

@app.route("/user_options")
def user_options():
    return render_template("user_options.html")

# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == ADMIN_PASSWORD:

            session['admin_logged_in'] = True

            return redirect(url_for("admin_dashboard"))

        return "<h1>Access Denied</h1>"

    return render_template("admin_login.html")

# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin_dashboard")
def admin_dashboard():

    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("employee.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees ORDER BY id DESC")

    employees = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", employees=employees)

# =========================
# LOGOUT
# =========================

@app.route("/admin_logout")
def admin_logout():

    session.pop('admin_logged_in', None)

    return redirect(url_for("index"))

# =========================
# USER PAGES
# =========================

@app.route("/register")
def register():
    return render_template("view.html")

@app.route("/face_login")
def face_login():
    return render_template("face_login.html")

# =========================
# FORM SUBMISSION
# =========================

@app.route("/submit", methods=["POST"])
def submit():

    employee_id = request.form.get("employee_id").strip()
    name = request.form.get("name").strip()
    jh_dmt = request.form.get("jh_dmt_name").strip()
    manual_input = request.form.get("jh_dmt_manual")

    if jh_dmt == "OTHER" and manual_input:
        jh_dmt = manual_input.strip()

    phone = request.form.get("phone").strip()
    email = request.form.get("email").strip()
    photo_data = request.form.get("photo_data")

    if len(employee_id) < 3:
        return "Invalid Employee ID"

    if not re.match(r"^[A-Za-z ]{3,50}$", name):
        return "Invalid Name"

    if len(jh_dmt) < 2:
        return "Invalid JH/DMT Name"

    if not re.match(r"^[6-9]\d{9}$", phone):
        return "Invalid Phone"

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return "Invalid Email"

    photo_path = ""

    if photo_data:

        header, encoded = photo_data.split(",", 1)
        image_data = base64.b64decode(encoded)

        filename = f"{employee_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"

        photo_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(photo_path, "wb") as f:
            f.write(image_data)

    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees
        (employee_id, name, jh_name, dmt_name, phone, email, photo_path, submission_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        name,
        jh_dmt,
        jh_dmt,
        phone,
        email,
        photo_path,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    send_success_email(email, name)
    send_sms(phone, name)

    return render_template("success.html", name=name)

# =========================
# REGISTERED PROFILE PHOTO LOADING
# =========================

@app.route("/load_registered_photo", methods=["POST"])
def load_registered_photo():

    data = request.json
    employee_id = data.get("employee_id", "").strip()
    name = data.get("name", "").strip()

    if not re.match(r"^\d{5}$", employee_id) or len(name) < 3:
        return jsonify({"status": "error", "message": "Enter valid Employee ID and name."})

    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT photo_path FROM employees WHERE employee_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
        (employee_id, name)
    )
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0] or not os.path.exists(row[0]):
        return jsonify({"status": "error", "message": "Registered photo not found for this profile."})

    with open(row[0], "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return jsonify({
        "status": "success",
        "message": "Registered profile loaded.",
        "photo_data": f"data:image/jpeg;base64,{encoded}"
    })

# =========================
# FACE VERIFICATION
# =========================

@app.route("/verify", methods=["POST"])
def verify():

    data = request.json
    mode = data.get("mode", "live")
    employee_id = data.get("employee_id", "").strip()
    name = data.get("name", "").strip()

    if mode == "registered":

        if not re.match(r"^\d{5}$", employee_id) or len(name) < 3:
            return jsonify({"status": "error", "message": "Invalid Employee ID or name."})

        conn = sqlite3.connect("employee.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT photo_path FROM employees WHERE employee_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (employee_id, name)
        )
        row = cursor.fetchone()
        conn.close()

        if row and row[0] and os.path.exists(row[0]):
            return jsonify({
                "status": "success",
                "message": f"Welcome back, {name}! Registered profile matched."
            })

        return jsonify({"status": "error", "message": "Registered profile not found."})

    photo_data = data.get("photo_data")

    if not photo_data:
        return jsonify({"status": "error", "message": "No live photo captured."})

    header, encoded = photo_data.split(",", 1)
    live_blob = base64.b64decode(encoded)

    with open("temp_login.jpg", "wb") as f:
        f.write(live_blob)

    live_img = face_recognition.load_image_file("temp_login.jpg")
    live_encs = face_recognition.face_encodings(live_img)

    if not live_encs:
        return jsonify({"status": "error", "message": "No face detected."})

    conn = sqlite3.connect("employee.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, photo_path FROM employees")
    rows = cursor.fetchall()
    conn.close()

    for name, path in rows:

        if path and os.path.exists(path):

            db_img = face_recognition.load_image_file(path)
            db_encs = face_recognition.face_encodings(db_img)

            if db_encs and face_recognition.compare_faces([db_encs[0]], live_encs[0])[0]:
                return jsonify({
                    "status": "success",
                    "message": f"Welcome, {name}!"
                })

    return jsonify({"status": "error", "message": "Verification Failed."})

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)