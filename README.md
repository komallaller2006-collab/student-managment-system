# 🎓 Student Management System

A production-ready, responsive **Student Management System** with token-protected student portals, automated multi-sheet Excel generation, and assignment coursework submission.

Built with **Python (Flask)**, **openpyxl**, **SQLite**, and **HTML5/Vanilla CSS3/JavaScript**.

---

## 🌟 Core Features & Implementation

### 1. 🛡️ Admin Panel (Authentication Required)
- **Secure Authentication**: Salted and hashed admin password verification via Werkzeug PBKDF2 (`admin` / `admin123`).
- **Student Registration**: Admin inputs Roll Number, Name, Class/Course, Email, Phone, Father's Name, DOB, and Address.
- **Dynamic Secure Link Generation**: Instant generation of unique personal links with high-entropy cryptographic tokens:
  ```
  http://localhost:5000/student/ROLL101?token=xyz...
  ```
- **Instant Excel Auto-Creation**: Every registered student automatically receives a custom, professionally styled Excel file (`excel/<roll_no>.xlsx`) with **5 distinct sheets**:
  1. `Personal Details`
  2. `Attendance`
  3. `Marks & Grades`
  4. `Assignments Submitted`
  5. `Remarks`
- **Admin Dashboard**:
  - Live search and filter across Roll No, Student Name, Course, Email, and Phone.
  - View individual student portal.
  - Edit student profile, add attendance, log marks, and add remarks directly into their Excel file.
  - Instant one-click download for any student's individual Excel workbook.
  - Delete student records with SQLite cascade and file cleanup.
  - Global assignment submission viewer with file downloads.
  - Downloadable standardized 5-sheet blank template (`Student_Management_Template.xlsx`).
  - Consolidated Master Excel export (`Students_Master_Directory.xlsx`).

---

### 2. 🎒 Student Portal (Personal Token Link)
- **Token-Secured Access**: Accessible via `/student/<roll_no>?token=<secure_token>`.
- **Live Academic Dashboard**:
  - Live calculated Attendance Rate from Sheet 2.
  - Live calculated GPA & Marks Average from Sheet 3.
  - Overall coursework submission counter.
- **Assignment Upload**:
  - Students can upload coursework files (`.pdf`, `.doc`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.webp`, Max 10 MB).
  - Files are stored in `uploads/<roll_no>/<timestamp>_<filename>`.
  - Recorded in the SQLite `assignments` database.
  - Automatically logged into **Sheet 4 ("Assignments Submitted")** of the student's Excel workbook with filename, date, time, and file size.
- **Direct Excel Download**: Students can click **"Download Excel Record"** to download their own up-to-date `.xlsx` file at any time.

---

### 3. 🔒 Access Control & Security
- **Strict Roll Number & Token Binding**:
  - Changing the roll number in the URL (e.g., trying to access `ROLL102` with `ROLL101`'s token) immediately triggers **`403 Access Denied`**.
  - Accessing `/student/<roll_no>` without a token triggers **`403 Access Denied`**.
  - Attempting to upload files or download files for another roll number without admin authentication is blocked with **`403 Access Denied`**.
- **Admin-Only Oversight**: Only authenticated admins have global access to view, edit, or download any student's file without token restriction.
- **Input Sanitization & File Security**:
  - Roll numbers sanitized via regex pattern matching.
  - Filenames sanitized using `secure_filename`.
  - Max upload limit enforced at server level (10 MB).
  - Allowed file extension whitelist strictly validated.

---

## 📁 Project Structure

```
student management system/
│── app.py                    # Flask application server, routing, security & uploads
│── db.py                     # SQLite database schema, token management & queries
│── excel_service.py          # openpyxl engine: 5 sheets, template generation, read/write
│── requirements.txt          # Python dependencies (Flask, openpyxl)
│── seed_data.py              # Sample student seeder script
│── test_suite.py             # 7-phase automated test verification suite
│── run.bat                   # 1-Click launcher for Windows
│── README.md                 # Complete documentation
│
├── data/
│   └── students.db           # SQLite database (admins, students, assignments)
│
├── excel/                    # Student Excel workbooks & template
│   ├── Student_Management_Template.xlsx
│   ├── ROLL101.xlsx
│   ├── ROLL102.xlsx
│   └── ROLL103.xlsx
│
├── uploads/                  # Submitted student assignments (isolated by roll number)
│   ├── ROLL101/
│   ├── ROLL102/
│   └── ROLL103/
│
├── static/
│   ├── css/
│   │   └── style.css         # Modern design system (Plus Jakarta Sans, cards, badges)
│   └── js/
│       └── main.js           # AJAX copy-to-clipboard, live search filter
│
└── templates/
    ├── base.html             # Master layout, navigation, flash alerts, modal
    ├── login.html            # Admin login screen
    ├── dashboard.html        # Admin management dashboard & registration
    ├── edit_student.html     # Student editor (personal info, marks, attendance, remarks)
    ├── student_view.html     # Student portal with 5 Excel sheets & upload box
    └── access_denied.html    # 403 Access Denied security screen
```

---

## 🚀 How to Run

### Method 1: 1-Click Launcher (Windows)
Double-click `run.bat` in the project root directory. It will start the server and open your default browser to `http://localhost:5000`.

### Method 2: Command Line (PowerShell / Command Prompt)

1. Open a terminal in the project directory:
   ```bash
   cd "C:\Users\komal\OneDrive\Desktop\student management system"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Optional: Seed sample students:
   ```bash
   python seed_data.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your web browser:
   **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Running Automated Tests

To run the complete automated test suite verifying all 7 security and functionality criteria:
```bash
python test_suite.py
```

Expected output:
```
==================================================
 [SUCCESS] ALL 7 AUTOMATED TESTS PASSED (100% OK)!
==================================================
```

---

## 🔑 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`
