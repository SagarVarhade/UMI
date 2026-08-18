import csv
from datetime import datetime
import os
import re
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Absolute directory paths to prevent duplicate file generation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, 'appointments.csv')
DB_FILE = os.path.join(BASE_DIR, 'umi_health.db')


# ==========================================
# 0. DATABASE CONNECTION & SCHEMAS
# ==========================================

def get_db_connection():
    """Establishes connection to local SQLite database file."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enables dict-like column access: row['uhid']
    return conn


def init_db():
    """Creates the appointments table automatically on server startup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uhid TEXT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            place TEXT,
            mobile TEXT,
            doctor_name TEXT,
            appointment_time TEXT,
            visit_date TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


init_db()


# ==========================================
# 1. HELPER FUNCTIONS & MATCHING ENGINE
# ==========================================

def normalize_phone(phone) -> str:
    """Strips non-digits and returns the last 10 digits of a mobile number."""
    if not phone:
        return ""
    digits = re.sub(r'\D', '', str(phone))
    return digits[-10:] if len(digits) >= 10 else digits


def jaro_winkler_similarity(s1: str, s2: str) -> float:
    """Calculates Jaro-Winkler string similarity between 0.0 and 1.0."""
    s1, s2 = str(s1 or '').lower().strip(), str(s2 or '').lower().strip()
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    max_dist = (max(len1, len2) // 2) - 1
    if max_dist < 0:
        max_dist = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] == s2[j]:
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if s1_matches[i]:
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

    jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3.0
    prefix = 0
    for i in range(min(4, len1, len2)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break

    return jaro + (prefix * 0.1 * (1 - jaro))


def check_patient_match(existing_record: dict, incoming_record: dict) -> tuple[float, str, list[str]]:
    """Evaluates match score using Mobile (Layer 1) or Name, Age, Gender, Place (Layer 2)."""
    explanations = []

    phone1 = normalize_phone(existing_record.get("mobile"))
    phone2 = normalize_phone(incoming_record.get("phone") or incoming_record.get("mobile"))

    # Layer 1: Exact Mobile Match
    if phone1 and phone2 and phone1 == phone2:
        return 100.0, "EXACT_PHONE_MATCH", [f"✓ Identical Mobile Number ({phone1})"]

    # Layer 2: Demographic Check
    g1 = str(existing_record.get("gender", "")).strip().upper()
    g2 = str(incoming_record.get("gender", "")).strip().upper()
    if g1 and g2 and g1 != g2:
        return 0.0, "NO_MATCH", ["✗ Gender Mismatch"]

    gender_score = 10.0
    explanations.append("✓ Gender Match (+10.0 pts)")

    # Name Similarity
    name1 = str(existing_record.get("name", "")).strip()
    name2 = str(incoming_record.get("name", "")).strip()
    name_sim = jaro_winkler_similarity(name1, name2)
    name_score = name_sim * 45.0
    explanations.append(f"✓ Name Similarity ({name_sim*100:.1f}%) (+{name_score:.1f} pts)")

    # Age Check
    age_score = 0.0
    try:
        age1 = int(existing_record.get("age", 0))
        age2 = int(incoming_record.get("age", 0))
        diff = abs(age1 - age2)

        if diff == 0:
            age_score = 25.0
            explanations.append("✓ Exact Age Match (+25.0 pts)")
        elif diff == 1:
            age_score = 18.0
            explanations.append("✓ Age Diff 1 Yr (+18.0 pts)")
        elif diff == 2:
            age_score = 10.0
            explanations.append("✓ Age Diff 2 Yrs (+10.0 pts)")
        else:
            explanations.append(f"✗ Age Diff ({diff} yrs) (+0 pts)")
    except (ValueError, TypeError):
        explanations.append("⚠ Invalid/Missing Age (+0 pts)")

    # Place Check
    place1 = str(existing_record.get("place", "")).strip()
    place2 = str(incoming_record.get("place", "")).strip()
    place_sim = jaro_winkler_similarity(place1, place2)
    place_score = place_sim * 20.0
    explanations.append(f"✓ Place Similarity ({place_sim*100:.1f}%) (+{place_score:.1f} pts)")

    total_score = round(gender_score + name_score + age_score + place_score, 2)

    if total_score >= 80.0:
        status = "MATCH_FOUND_NEW_PHONE_PROVIDED"
    elif total_score >= 60.0:
        status = "POTENTIAL_MATCH_REVIEW_REQUIRED"
    else:
        status = "NO_MATCH"

    return total_score, status, explanations


def calculate_match_percentage(rec_a: dict, rec_b: dict) -> float:
    """Pairwise demographic scoring logic used for batch database duplicate scanning."""
    phone_a = normalize_phone(rec_a.get('mobile'))
    phone_b = normalize_phone(rec_b.get('mobile'))
    if phone_a and phone_b and phone_a == phone_b:
        return 100.0

    g1 = str(rec_a.get('gender', '')).strip().upper()
    g2 = str(rec_b.get('gender', '')).strip().upper()
    if g1 and g2 and g1 != g2:
        return 0.0

    name_a = str(rec_a.get('name', '')).strip().lower()
    name_b = str(rec_b.get('name', '')).strip().lower()
    if not name_a or not name_b:
        return 0.0

    name_sim = jaro_winkler_similarity(name_a, name_b)
    if name_sim < 0.75:
        return 0.0

    name_score = name_sim * 55.0

    age_score = 0.0
    try:
        raw_a = re.sub(r'\D', '', str(rec_a.get('age', 0)))
        raw_b = re.sub(r'\D', '', str(rec_b.get('age', 0)))
        age_a = int(raw_a) if raw_a else 0
        age_b = int(raw_b) if raw_b else 0

        diff = abs(age_a - age_b)
        if diff == 0:
            age_score = 25.0
        elif diff == 1:
            age_score = 18.0
        elif diff == 2:
            age_score = 10.0
        elif diff > 5:
            return 0.0
    except (ValueError, TypeError):
        pass

    place_score = 0.0
    place_a = str(rec_a.get('place', '')).strip().lower()
    place_b = str(rec_b.get('place', '')).strip().lower()
    invalid_places = {'none', 'null', 'n/a', 'na', '', 'unknown'}

    if place_a not in invalid_places and place_b not in invalid_places:
        place_sim = jaro_winkler_similarity(place_a, place_b)
        place_score = place_sim * 10.0

    gender_score = 10.0 if (g1 and g2 and g1 == g2) else 0.0

    return round(gender_score + name_score + age_score + place_score, 1)


# ==========================================
# 2. HELPER: IMPORT CSV TO SQLITE
# ==========================================

if not os.path.exists(EXCEL_FILE):
    with open(EXCEL_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Booking ID', 'Patient Name', 'Age', 'Gender', 
            'Mobile', 'Doctor Assigned', 'Time Slot', 
            'Visit Date', 'Status', 'Booking Timestamp'
        ])


def import_csv():
    """Syncs CSV records into SQLite safely without creating duplicates."""
    if not os.path.exists(EXCEL_FILE):
        return 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT mobile, visit_date FROM appointments")
        existing_rows = [dict(r) for r in cursor.fetchall()]
        
        existing_records = {
            (normalize_phone(r.get('mobile')), str(r.get('visit_date')).strip())
            for r in existing_rows
        }

        with open(EXCEL_FILE, mode='r', encoding='utf-8') as file:
            csv_data = csv.reader(file)
            header = next(csv_data, None)

            sql_query = """
                INSERT INTO appointments 
                (uhid, name, age, gender, place, mobile, doctor_name, appointment_time, visit_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            imported_count = 0
            for row in csv_data:
                if not row or len(row) < 9:
                    continue

                phone = normalize_phone(row[4])
                date = row[7].replace("'", "").strip()

                if (phone, date) in existing_records:
                    continue

                name = row[1].strip()
                age = int(row[2].strip()) if row[2].strip().isdigit() else 0
                gender = row[3].strip()
                doctor = row[5].strip()
                time_slot = row[6].strip()
                status = row[8].strip() if row[8].strip() in ['Pending', 'Prescribed'] else 'Pending'
                created_at = row[9].replace("'", "").strip() if len(row) > 9 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                uhid = f"UHID{int(row[0]):06d}" if str(row[0]).isdigit() else f"UHID{imported_count+1:06d}"

                values = (uhid, name, age, gender, '', phone, doctor, time_slot, date, status, created_at)
                try:
                    cursor.execute(sql_query, values)
                    existing_records.add((phone, date))
                    imported_count += 1
                except sqlite3.Error as err:
                    print(f"Skipped invalid row: {err}")

            conn.commit()

        conn.close()
        return imported_count

    except Exception as e:
        print("CSV SYNC ERROR:", str(e))
        return 0


# ==========================================
# 3. DASHBOARD & SYSTEM ROUTES
# ==========================================

@app.route("/", methods=["GET", "POST"])
def web():
    return render_template("auth/index.html")


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
            return render_template("auth/index.html", error="Invalid Employee ID or Password")

    return render_template("auth/index.html")


@app.route("/nurse")
def nurse_dashboard():
    import_csv()
    today_str = datetime.now().strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM appointments WHERE status = 'Pending' AND DATE(REPLACE(visit_date, '''', '')) = ? ORDER BY id DESC", 
            (today_str,)
        )
        pending_appointments = [dict(r) for r in cursor.fetchall()]

        cursor.execute(
            "SELECT * FROM appointments WHERE status = 'Prescribed' AND DATE(REPLACE(visit_date, '''', '')) = ? ORDER BY id DESC", 
            (today_str,)
        )
        prescribed_appointments = [dict(r) for r in cursor.fetchall()]

        conn.close()

    except Exception as e:
        print("SQLITE FETCH ERROR:", str(e))
        pending_appointments, prescribed_appointments = [], []

    return render_template(
        "dashboard/nurse_dashboard.html",
        pending=pending_appointments,
        prescribed=prescribed_appointments,
        total_pending=len(pending_appointments),
        total_prescribed=len(prescribed_appointments),
        total_today=len(pending_appointments) + len(prescribed_appointments)
    )


@app.route('/duplicates')
def view_duplicates_page():
    """Scans the SQLite database for potential patient duplicates (score >= 80%)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments ORDER BY id ASC")
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()

        duplicate_pairs = []
        seen_pairs = set()

        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                rec_a = records[i]
                rec_b = records[j]

                if rec_a['id'] == rec_b['id']:
                    continue

                uhid_a = str(rec_a.get('uhid') or '').strip()
                uhid_b = str(rec_b.get('uhid') or '').strip()

                # Skip if already merged under the exact same UHID
                if uhid_a and uhid_b and uhid_a == uhid_b:
                    continue

                pair_key = tuple(sorted([rec_a['id'], rec_b['id']]))
                if pair_key in seen_pairs:
                    continue

                score = calculate_match_percentage(rec_a, rec_b)

                if score >= 80.0:
                    seen_pairs.add(pair_key)

                    if uhid_a and not uhid_b:
                        primary_rec, duplicate_rec = rec_a, rec_b
                    elif uhid_b and not uhid_a:
                        primary_rec, duplicate_rec = rec_b, rec_a
                    else:
                        primary_rec, duplicate_rec = rec_a, rec_b

                    primary_uhid = primary_rec.get('uhid') or f"UHID{primary_rec['id']:06d}"
                    duplicate_uhid = duplicate_rec.get('uhid') or f"UHID{duplicate_rec['id']:06d}"

                    duplicate_pairs.append({
                        "score": score,
                        "primary": primary_rec,
                        "primary_uhid": primary_uhid,
                        "duplicate": duplicate_rec,
                        "duplicate_uhid": duplicate_uhid
                    })

        return render_template('duplicates.html', pairs=duplicate_pairs)

    except Exception as e:
        return f"Error loading duplicates dashboard: {str(e)}", 500


@app.route('/book-appointment')
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
    return redirect(url_for('web'))


@app.route('/help')
def help_page():
    return render_template('common/help.html')


# ==========================================
# 4. API & MATCHING ENDPOINTS
# ==========================================

@app.route('/api/merge-patients', methods=['POST'])
def api_merge_patients():
    """Merges a duplicate record with a primary record in SQLite."""
    try:
        data = request.get_json(force=True)
        primary_uhid = data.get('primary_uhid')
        duplicate_id = data.get('duplicate_id')

        if not primary_uhid or not duplicate_id:
            return jsonify({"status": "error", "message": "Missing primary_uhid or duplicate_id"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update duplicate record with primary UHID
        sql_duplicate = "UPDATE appointments SET uhid = ? WHERE id = ?"
        cursor.execute(sql_duplicate, (primary_uhid, duplicate_id))

        # Ensure primary record itself has the UHID string set
        try:
            primary_id = int(re.sub(r'\D', '', str(primary_uhid)))
            sql_primary = "UPDATE appointments SET uhid = ? WHERE id = ? AND (uhid IS NULL OR uhid = '')"
            cursor.execute(sql_primary, (primary_uhid, primary_id))
        except ValueError:
            pass

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": f"Database updated successfully. Records merged under {primary_uhid}."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/get-patient-by-mobile/<mobile>', methods=['GET'])
def api_get_patient_by_mobile(mobile):
    """Fetches patient details using mobile search."""
    try:
        clean_mobile = re.sub(r'\D', '', str(mobile or ''))[-10:]

        if not clean_mobile or len(clean_mobile) < 10:
            return jsonify({"found": False, "message": "Valid 10-digit mobile required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM appointments WHERE mobile LIKE ? ORDER BY id DESC LIMIT 1"
        cursor.execute(sql, (f"%{clean_mobile}%",))
        row = cursor.fetchone()

        conn.close()

        if row:
            patient = dict(row)
            assigned_uhid = patient.get("uhid") if patient.get("uhid") else f"UHID{patient['id']:06d}"

            return jsonify({
                "found": True,
                "patient": {
                    "uhid": assigned_uhid,
                    "name": patient.get("name", ""),
                    "age": patient.get("age", ""),
                    "gender": patient.get("gender", ""),
                    "place": patient.get("place", "")
                }
            }), 200

        return jsonify({"found": False, "message": "No patient found"}), 200

    except Exception as e:
        return jsonify({"found": False, "error": str(e)}), 500


@app.route('/api/check-patient-duplicate', methods=['POST'])
def api_check_patient_duplicate():
    """Detects duplicate records on single booking submission."""
    try:
        incoming_data = request.get_json()
        if not incoming_data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments")
        all_patients = [dict(r) for r in cursor.fetchall()]
        conn.close()

        highest_score = 0.0
        best_match = None
        match_status = "NO_MATCH"
        match_reasons = []

        for patient in all_patients:
            score, status, reasons = check_patient_match(patient, incoming_data)

            if status == "EXACT_PHONE_MATCH":
                return jsonify({
                    "status": "EXACT_PHONE_MATCH",
                    "score": 100.0,
                    "matched_patient": patient,
                    "reasons": reasons
                }), 200

            if score > highest_score:
                highest_score = score
                best_match = patient
                match_status = status
                match_reasons = reasons

        return jsonify({
            "status": match_status,
            "score": highest_score,
            "matched_patient": best_match,
            "reasons": match_reasons
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/book-appointment', methods=['POST'])
def api_book_appointment():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        name = str(data.get('name') or data.get('patient_name') or '').strip()
        raw_age = str(data.get('age', '')).strip()
        age = int(raw_age) if raw_age.isdigit() else 0
        gender = str(data.get('gender', '')).strip()
        
        raw_phone = data.get('phone') or data.get('mobile') or ''
        phone = normalize_phone(raw_phone)
        
        place = str(data.get('place', '')).strip()
        doctor = str(data.get('doctor') or data.get('doctor_name') or '').strip()
        time_slot = str(data.get('time') or data.get('appointment_time') or '').strip()
        
        raw_date = str(data.get('date') or data.get('visit_date') or '').replace("'", "").strip()
        try:
            date = datetime.strptime(raw_date, "%Y-%m-%d").date().strftime('%Y-%m-%d')
        except ValueError:
            date = datetime.now().strftime('%Y-%m-%d')

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        force_new_uhid = data.get('force_new_uhid', False)
        selected_existing_uhid = data.get('existing_uhid', None)

        if not name:
            return jsonify({"status": "error", "message": "Patient Name is required!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        assigned_uhid = None

        if selected_existing_uhid and not force_new_uhid:
            assigned_uhid = selected_existing_uhid

        elif not force_new_uhid and phone and len(phone) >= 10:
            cursor.execute(
                "SELECT uhid, id FROM appointments WHERE mobile LIKE ? ORDER BY id DESC LIMIT 1",
                (f"%{phone}%",)
            )
            row = cursor.fetchone()
            if row:
                phone_match = dict(row)
                assigned_uhid = phone_match.get('uhid') or f"UHID{phone_match['id']:06d}"

        if not assigned_uhid:
            cursor.execute("SELECT MAX(id) AS max_id FROM appointments")
            row = cursor.fetchone()
            max_id = row['max_id'] if row and row['max_id'] else 0
            next_id = max_id + 1
            assigned_uhid = f"UHID{next_id:06d}"

        sql_query = """
            INSERT INTO appointments 
            (uhid, name, age, gender, place, mobile, doctor_name, appointment_time, visit_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (assigned_uhid, name, age, gender, place, phone, doctor, time_slot, date, 'Pending', timestamp)

        cursor.execute(sql_query, values)
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "status": "success", 
            "message": f"Appointment booked successfully under {assigned_uhid}",
            "uhid": assigned_uhid,
            "id": inserted_id
        }), 200

    except sqlite3.Error as db_err:
        return jsonify({"status": "error", "message": f"Database Error: {str(db_err)}"}), 500

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
    return jsonify({"status": "success", "message": f"Imported {count} records into SQLite!"}), 200


# ==========================================
# 5. SERVER RUNTIME EXECUTION
# ==========================================

if __name__ == "__main__":
    print("Syncing CSV to SQLite on launch...")
    import_csv()
    app.run(debug=True, port=5001)
