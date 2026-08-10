from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
import csv
import os
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# Point directly to appointments.csv inside umi_site directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'appointments.csv')


# ==========================================
# 1. INITIALIZE CSV FILE WITH HEADERS
# ==========================================
if not os.path.exists(EXCEL_FILE):
    with open(EXCEL_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Booking ID', 'Patient Name', 'Age', 'Gender', 
            'Mobile', 'Doctor Assigned', 'Time Slot', 
            'Visit Date', 'Status', 'Booking Timestamp'
        ])


# ==========================================
# 2. HELPER: IMPORT CSV TO MYSQL
# ==========================================
def import_csv():
    print(f"\nReading CSV from: {EXCEL_FILE}")
    if not os.path.exists(EXCEL_FILE):
        print(f"ERROR: CSV File not found at {EXCEL_FILE}")
        return 0

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='#Sagar2003',
            database='umi_health'
        ) 
        cursor = conn.cursor()

        # Fetch existing mobile + visit_date combinations
        cursor.execute("SELECT mobile, visit_date FROM appointments")
        existing_rows = cursor.fetchall()
        existing_records = {(str(m).strip(), str(d).strip()) for m, d in existing_rows}

        with open(EXCEL_FILE, mode='r', encoding='utf-8') as file:
            csv_data = csv.reader(file)
            header = next(csv_data, None)  # Skip header

            sql_query = """
                INSERT INTO appointments 
                (name, age, gender, mobile, doctor_name, appointment_time, visit_date, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            imported_count = 0
            for row_idx, row in enumerate(csv_data, start=1):
                if not row or len(row) < 10:
                    continue

                name = row[1].strip()
                age = int(row[2].strip()) if row[2].strip().isdigit() else 0
                gender = row[3].strip()
                phone = row[4].replace("'", "").strip()
                doctor = row[5].strip()
                time_slot = row[6].strip()
                date = row[7].replace("'", "").strip()
                
                status = row[8].strip()
                if status not in ['Pending', 'Prescribed']:
                    status = 'Pending'
                
                created_at = row[9].replace("'", "").strip()

                if (phone, date) not in existing_records:
                    values = (name, age, gender, phone, doctor, time_slot, date, status, created_at)
                    try:
                        cursor.execute(sql_query, values)
                        existing_records.add((phone, date))
                        imported_count += 1
                    except mysql.connector.Error as err:
                        print(f"Failed to insert row {row_idx} ({name}): {err}")

            conn.commit()
            print(f"SUCCESS: Imported {imported_count} record(s) into MySQL database!")

        cursor.close()
        conn.close()
        return imported_count

    except Exception as e:
        print("DATABASE ERROR:", str(e))
        return 0


# ==========================================
# 3. ROUTES
# ==========================================

@app.route("/", methods=["GET", "POST"])
def web():
    return render_template("auth/login.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "Nurse" and password == "1234":
            return redirect(url_for("nurse_dashboard"))
        elif username == "Doctor" and password == "1234":
            return redirect(url_for("doctor_dashboard"))
        elif username == "Pharma" and password == "1234":
            return redirect(url_for("pharmacy_dashboard"))
        elif username == "Admin" and password == "1234":
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("auth/login.html", error="Invalid Employee ID or Password")

    return render_template("auth/login.html")


@app.route("/nurse")
def nurse_dashboard():
    # 1. Sync any new CSV entries to MySQL first
    import_csv()

    pending_appointments = []
    prescribed_appointments = []
    
    total_pending = 0
    total_prescribed = 0
    total_today = 0

    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='#Sagar2003',
            database='umi_health'
        )
        cursor = conn.cursor(dictionary=True)

        # 2. Fetch Pending Appointments
        cursor.execute("SELECT * FROM appointments WHERE status = 'Pending' ORDER BY id DESC")
        pending_appointments = cursor.fetchall()

        # 3. Fetch Prescribed Appointments
        cursor.execute("SELECT * FROM appointments WHERE status = 'Prescribed' ORDER BY id DESC")
        prescribed_appointments = cursor.fetchall()

        # 4. Calculate Summary Stats
        total_pending = len(pending_appointments)
        total_prescribed = len(prescribed_appointments)
        total_today = total_pending + total_prescribed

        cursor.close()
        conn.close()

    except Exception as e:
        print("DATABASE FETCH ERROR:", str(e))

    return render_template(
        "dashboard/nurse_dashboard.html",
        pending=pending_appointments,
        prescribed=prescribed_appointments,
        total_pending=total_pending,
        total_prescribed=total_prescribed,
        total_today=total_today
    )

@app.route("/book-appointment")
def book_appointment():
    return render_template("patient/book-appointment.html")


@app.route("/doctor")
def doctor_dashboard():
    return render_template("dashboard/doctor_dashboard.html")


@app.route("/pharmacy")
def pharmacy_dashboard():
    return render_template("dashboard/pharmacy_dashboard.html")


@app.route("/admin")
def admin_dashboard():
    return render_template("admin/admin_dashboard.html")


@app.route('/logout')
def logout_page():
    return redirect(url_for('login'))


# --- ADD THIS MISSING ROUTE ---
@app.route('/help')
def help_page():
    return render_template('common/help.html')


# ==========================================
# 4. API ROUTES
# ==========================================

@app.route('/api/book-appointment', methods=['POST'])
def api_book_appointment():
    try:
        data = request.get_json()
        
        booking_id = 1
        if os.path.exists(EXCEL_FILE):
            with open(EXCEL_FILE, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = [row for row in reader if row]
                booking_id = len(rows)

        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        phone = f"'{data.get('phone')}"
        doctor = data.get('doctor')
        time_slot = data.get('time')
        date = f"'{data.get('date')}"
        timestamp = f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        with open(EXCEL_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                booking_id, name, age, gender, phone, 
                doctor, time_slot, date, 'Pending', timestamp
            ])

        return jsonify({"status": "success", "message": "Saved to Excel file!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/download-excel')
def download_excel():
    if os.path.exists(EXCEL_FILE):
        return send_file(
            EXCEL_FILE,
            mimetype='text/csv',
            as_attachment=True,
            download_name='UMI_Appointments.csv'
        )
    return "No appointments found.", 404


@app.route('/api/import-excel-to-db', methods=['POST', 'GET'])
def import_excel_to_db():
    count = import_csv()
    return jsonify({"status": "success", "message": f"Imported {count} records into MySQL!"}), 200


# ==========================================
# 5. SERVER RUNTIME EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Syncing CSV to MySQL on launch...")
    import_csv()
    app.run(debug=True, port=5001)