"""
Student Management System — Main Application Server
Flask web application with SQLite database and openpyxl multi-sheet Excel engine.
Enforces strict token-based access control, secure assignment uploads,
Excel synchronizations, and an admin management dashboard.
"""

import os
import re
from datetime import datetime
from functools import wraps
# pyrefly: ignore[missing-import]
from flask import(
    Flask, render_template, request, redirect,
    url_for, flash, session, send_file, jsonify, abort
)
from werkzeug.utils import secure_filename

import db
import excel_service

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "student_mgmt_secure_token_secret_2026_xyz")

# Max upload size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
EXCEL_DIR = os.path.join(BASE_DIR, "excel")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Admin authentication required.", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if db.verify_admin(username, password):
            session["admin_logged_in"] = True
            session["admin_user"] = username
            flash("Welcome back, Administrator!", "success")
            return redirect(request.args.get("next") or url_for("dashboard"))
        else:
            flash("Invalid admin credentials. Use admin / admin123", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Successfully signed out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    students = db.get_all_students()
    all_assignments = db.get_all_assignments()

    total_students = len(students)
    total_assignments = len(all_assignments)
    unique_classes = len(set(s.get("class_name") for s in students if s.get("class_name")))

    return render_template(
        "dashboard.html",
        students=students,
        assignments=all_assignments,
        total_students=total_students,
        total_assignments=total_assignments,
        unique_classes=unique_classes,
        admin_user=session.get("admin_user", "Admin")
    )


@app.route("/register_student", methods=["POST"])
@login_required
def register_student():
    roll_no = request.form.get("roll_no", "").strip().upper()
    name = request.form.get("name", "").strip()
    class_name = request.form.get("class_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    father_name = request.form.get("father_name", "").strip()
    dob = request.form.get("dob", "").strip()
    address = request.form.get("address", "").strip()

    # Validation
    if not roll_no or not name or not class_name or not email or not phone:
        flash("Please fill in all required fields (Roll Number, Name, Class, Email, Phone).", "danger")
        return redirect(url_for("dashboard"))

    # Sanitize roll number (alphanumeric and dashes)
    clean_roll = re.sub(r'[^a-zA-Z0-9_\-]', '', roll_no)
    if not clean_roll:
        flash("Invalid characters in Roll Number.", "danger")
        return redirect(url_for("dashboard"))

    student_data = {
        "roll_no": clean_roll,
        "name": name,
        "class_name": class_name,
        "email": email,
        "phone": phone,
        "father_name": father_name,
        "dob": dob,
        "address": address
    }

    # Save to SQLite and get token
    roll_no, token = db.create_or_update_student(student_data)
    student = db.get_student(roll_no)

    # Generate individual Excel file with 5 sheets
    excel_service.generate_student_excel(student)

    personal_link = url_for("student_view", roll_no=roll_no, token=token, _external=True)

    flash(f"Student {name} (Roll: {roll_no}) registered successfully! Personal link generated.", "success")
    session["last_generated_link"] = {
        "roll_no": roll_no,
        "name": name,
        "link": personal_link,
        "token": token
    }
    return redirect(url_for("dashboard"))


@app.route("/student/<roll_no>")
def student_view(roll_no):
    roll_no = roll_no.strip().upper()
    token = request.args.get("token", "").strip()
    is_admin = session.get("admin_logged_in", False)

    # ACCESS CONTROL / SECURITY CHECK
    # Admin can view any student directly.
    # Students MUST have a valid token strictly matching this roll number.
    if not is_admin:
        if not token or not db.validate_student_access(roll_no, token):
            return render_template("access_denied.html", roll_no=roll_no), 403

    student = db.get_student(roll_no)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("login"))

    assignments = db.get_student_assignments(roll_no)
    has_excel = os.path.exists(os.path.join(EXCEL_DIR, f"{roll_no}.xlsx"))

    # Read live attendance, marks, remarks from Excel
    excel_data = excel_service.read_student_excel_data(roll_no)

    return render_template(
        "student_view.html",
        student=student,
        assignments=assignments,
        excel_data=excel_data,
        token=token,
        is_admin=is_admin,
        has_excel=has_excel
    )


@app.route("/student/<roll_no>/upload", methods=["POST"])
def upload_assignment(roll_no):
    roll_no = roll_no.strip().upper()
    token = request.form.get("token", "").strip()
    is_admin = session.get("admin_logged_in", False)

    # ACCESS CONTROL
    if not is_admin and not db.validate_student_access(roll_no, token):
        return render_template("access_denied.html", roll_no=roll_no), 403

    if "assignment_file" not in request.files:
        flash("No file selected for upload.", "danger")
        return redirect(url_for("student_view", roll_no=roll_no, token=token))

    file = request.files["assignment_file"]
    if file.filename == "":
        flash("Please select a valid file to upload.", "warning")
        return redirect(url_for("student_view", roll_no=roll_no, token=token))

    if not allowed_file(file.filename):
        flash("Invalid file format. Allowed types: PDF, DOC, DOCX, PNG, JPG, JPEG, WEBP (Max 10 MB).", "danger")
        return redirect(url_for("student_view", roll_no=roll_no, token=token))

    # Save file securely
    orig_name = file.filename
    clean_name = secure_filename(orig_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"{timestamp}_{clean_name}"

    student_upload_dir = os.path.join(UPLOADS_DIR, roll_no)
    os.makedirs(student_upload_dir, exist_ok=True)
    file_path = os.path.join(student_upload_dir, stored_filename)

    file.save(file_path)
    file_size = os.path.getsize(file_path)

    # 1. Log in SQLite DB
    db.log_assignment(roll_no, stored_filename, orig_name, file_path, file_size)

    # 2. Log in student's Excel file Sheet 4
    excel_service.log_assignment_submission_in_excel(roll_no, orig_name, stored_filename, file_size)

    flash(f"Assignment '{orig_name}' successfully submitted and recorded in your Excel file!", "success")
    return redirect(url_for("student_view", roll_no=roll_no, token=token))


@app.route("/student/<roll_no>/edit", methods=["GET", "POST"])
@login_required
def edit_student(roll_no):
    roll_no = roll_no.strip().upper()
    student = db.get_student(roll_no)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        father_name = request.form.get("father_name", "").strip()
        dob = request.form.get("dob", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not class_name or not email or not phone:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("edit_student", roll_no=roll_no))

        student_data = {
            "roll_no": roll_no,
            "name": name,
            "class_name": class_name,
            "email": email,
            "phone": phone,
            "father_name": father_name,
            "dob": dob,
            "address": address
        }

        # Update SQLite DB
        db.create_or_update_student(student_data)
        updated_student = db.get_student(roll_no)

        # Update Sheet 1 of Excel without disturbing other sheets
        excel_service.update_student_personal_in_excel(updated_student)

        flash(f"Student record for {roll_no} updated successfully!", "success")
        return redirect(url_for("dashboard"))

    excel_data = excel_service.read_student_excel_data(roll_no)
    assignments = db.get_student_assignments(roll_no)

    return render_template(
        "edit_student.html",
        student=student,
        excel_data=excel_data,
        assignments=assignments
    )


@app.route("/student/<roll_no>/add_attendance", methods=["POST"])
@login_required
def add_attendance(roll_no):
    roll_no = roll_no.strip().upper()
    term = request.form.get("term", "").strip()
    total_classes = request.form.get("total_classes", "").strip()
    attended = request.form.get("attended", "").strip()
    status = request.form.get("status", "Regular").strip()
    remarks = request.form.get("remarks", "").strip()

    if term and total_classes and attended:
        excel_service.add_attendance_row(roll_no, term, total_classes, attended, status, remarks)
        flash(f"Attendance for {term} added to {roll_no}'s Excel record.", "success")
    else:
        flash("Missing attendance details.", "warning")

    return redirect(url_for("edit_student", roll_no=roll_no))


@app.route("/student/<roll_no>/add_mark", methods=["POST"])
@login_required
def add_mark(roll_no):
    roll_no = roll_no.strip().upper()
    code = request.form.get("code", "").strip()
    name = request.form.get("name", "").strip()
    exam_type = request.form.get("exam_type", "Term Exam").strip()
    max_marks = request.form.get("max_marks", "100").strip()
    obtained = request.form.get("obtained", "0").strip()
    grade = request.form.get("grade", "A").strip()
    status = request.form.get("status", "Passed").strip()

    if code and name and max_marks and obtained:
        excel_service.add_marks_row(roll_no, code, name, exam_type, max_marks, obtained, grade, status)
        flash(f"Subject '{name}' grade logged to {roll_no}'s Excel record.", "success")
    else:
        flash("Missing subject or marks details.", "warning")

    return redirect(url_for("edit_student", roll_no=roll_no))


@app.route("/student/<roll_no>/add_remark", methods=["POST"])
@login_required
def add_remark(roll_no):
    roll_no = roll_no.strip().upper()
    category = request.form.get("category", "General").strip()
    author = session.get("admin_user", "Admin")
    remarks_text = request.form.get("remarks", "").strip()

    if remarks_text:
        excel_service.add_remark_row(roll_no, author, category, remarks_text)
        flash(f"Remark added to {roll_no}'s Excel record.", "success")
    else:
        flash("Remark text cannot be empty.", "warning")

    return redirect(url_for("edit_student", roll_no=roll_no))


@app.route("/api/student/<roll_no>")
@login_required
def api_get_student(roll_no):
    student = db.get_student(roll_no)
    if not student:
        return jsonify({"success": False, "error": "Not found"}), 404
    return jsonify({"success": True, "student": student})


@app.route("/download/excel/<roll_no>")
def download_student_excel(roll_no):
    roll_no = roll_no.strip().upper()
    token = request.args.get("token", "").strip()
    is_admin = session.get("admin_logged_in", False)

    # Security check: must be admin or valid student token
    if not is_admin and not db.validate_student_access(roll_no, token):
        return render_template("access_denied.html", roll_no=roll_no), 403

    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        student = db.get_student(roll_no)
        if student:
            assignments = db.get_student_assignments(roll_no)
            file_path = excel_service.generate_student_excel(student, assignments)
        else:
            flash("Excel record not found.", "warning")
            return redirect(url_for("dashboard") if is_admin else url_for("login"))

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{roll_no}_Record.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/download/template")
def download_template():
    """Download clean blank Excel template with all 5 standard sheets."""
    excel_service.init_excel_system()
    template_path = excel_service.TEMPLATE_PATH
    return send_file(
        template_path,
        as_attachment=True,
        download_name="Student_Management_Template.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/download/master_excel")
@login_required
def download_master_excel():
    """Download consolidated master Excel file for all registered students."""
    students = db.get_all_students()
    master_path = excel_service.generate_consolidated_master_excel(students)
    return send_file(
        master_path,
        as_attachment=True,
        download_name="Students_Master_Directory.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/download/assignment/<int:assignment_id>")
def download_assignment(assignment_id):
    """Download submitted assignment file (token or admin required)."""
    conn = db.get_db_connection()
    row = conn.cursor().execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    conn.close()

    if not row:
        abort(404)

    roll_no = row["roll_no"]
    token = request.args.get("token", "").strip()
    is_admin = session.get("admin_logged_in", False)

    if not is_admin and not db.validate_student_access(roll_no, token):
        return render_template("access_denied.html", roll_no=roll_no), 403

    if not os.path.exists(row["file_path"]):
        flash("File no longer exists on server.", "danger")
        return redirect(url_for("dashboard") if is_admin else url_for("student_view", roll_no=roll_no, token=token))

    return send_file(
        row["file_path"],
        as_attachment=True,
        download_name=row["original_name"]
    )


@app.route("/delete_student/<roll_no>", methods=["POST"])
@login_required
def delete_student_record(roll_no):
    roll_no = roll_no.strip().upper()
    db.delete_student(roll_no)

    # Remove Excel file
    excel_file = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if os.path.exists(excel_file):
        try:
            os.remove(excel_file)
        except Exception:
            pass

    flash(f"Student record for Roll No: {roll_no} deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.errorhandler(413)
def request_entity_too_large(error):
    flash("File size exceeds 10 MB limit. Please upload a smaller file.", "danger")
    return redirect(request.referrer or url_for("login"))


if __name__ == "__main__":
    db.init_db()
    excel_service.init_excel_system()
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(EXCEL_DIR, exist_ok=True)
    print("==============================================================")
    print(" [*] Student Management System Server Starting...")
    print(" [*] Local URL: http://localhost:5000")
    print(" [*] Admin Login: admin / admin123")
    print("==============================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
