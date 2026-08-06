from flask import Flask, render_template,redirect,url_for,request

app = Flask(__name__)

# ==========================
# Authentication
# ==========================
from flask import render_template, request, redirect, url_for

@app.route("/", methods=["GET", "POST"])
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
            return render_template(
                "auth/login.html",
                error="Invalid Employee ID or Password"
            )

    return render_template("auth/login.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("auth/login.html")


# ==========================
# Nurse
# ==========================

@app.route("/nurse")
def nurse_dashboard():
    return render_template("dashboard/nurse_dashboard.html")


@app.route("/book-appointment")
def book_appointment():
    return render_template("patient/book-appointment.html")


# ==========================
# Doctor
# ==========================

@app.route("/doctor")
def doctor_dashboard():
    return render_template("dashboard/doctor_dashboard.html")


@app.route("/prescription")
def prescription():
    return render_template("doctor/prescription.html")


@app.route("/prescription-template")
def prescription_template():
    return render_template("doctor/prescription_template.html")


@app.route("/doctor_schedule")
def doctor_schedule():
    return render_template("doctor/doctor_schedule.html")


# ==========================
# Pharmacy
# ==========================

@app.route("/pharmacy")
def pharmacy_dashboard():
    return render_template("dashboard/pharmacy_dashboard.html")


@app.route("/medicine-inventory")
def medicine_inventory():
    return render_template("pharmacy/medicine_inventory.html")


@app.route("/dispense-medicine")
def dispense_medicine():
    return render_template("pharmacy/dispense_medicine.html")


# ==========================
# Admin
# ==========================

@app.route("/admin")
def admin_dashboard():
    return render_template("admin/admin_dashboard.html")


@app.route("/manage-users")
def manage_users():
    return render_template("admin/manage_users.html")


@app.route("/reports")
def reports():
    return render_template("admin/reports.html")

@app.route('/logout')
def logout_page():
    return redirect(url_for('login'))


@app.route('/help')
def help_page():
    return render_template('common/help.html')
# ==========================
# Main
# ==========================

if __name__ == "__main__":
    app.run(debug=True)   