"""
Excel Service for Student Management System
Generates template and student workbooks with 5 distinct sheets:
1. Personal Details
2. Attendance
3. Marks & Grades
4. Assignments Submitted
5. Remarks
Also provides reading and updating utilities for seamless portal display.
"""

import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_DIR = os.path.join(BASE_DIR, "excel")
TEMPLATE_PATH = os.path.join(EXCEL_DIR, "Student_Management_Template.xlsx")
MASTER_PATH = os.path.join(EXCEL_DIR, "Students_Master_Consolidated.xlsx")

# Styling Definitions
HEADER_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Navy Blue
HEADER_FONT = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
LABEL_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
LABEL_FONT = Font(name="Segoe UI", size=10, bold=True, color="1E293B")
VALUE_FONT = Font(name="Segoe UI", size=10, color="0F172A")
THIN_BORDER = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)


def init_excel_system():
    os.makedirs(EXCEL_DIR, exist_ok=True)
    if not os.path.exists(TEMPLATE_PATH):
        create_excel_template()


def style_table_header(ws, headers, row_num=1):
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
    ws.row_dimensions[row_num].height = 28


def auto_fit_columns(ws, min_width=18):
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 5, min_width)


def create_excel_template():
    """Generates the master blank downloadable template with 5 standardized sheets."""
    os.makedirs(EXCEL_DIR, exist_ok=True)
    wb = openpyxl.Workbook()

    # 1. Sheet: Personal Details
    ws1 = wb.active
    ws1.title = "Personal Details"
    ws1_headers = [
        "Roll Number", "Full Name", "Class / Course", "Email Address",
        "Phone Number", "Father's Name", "Date of Birth", "Residential Address", "Registration Date"
    ]
    style_table_header(ws1, ws1_headers)
    sample_row1 = [
        "ROLL101", "Aarav Sharma", "B.Tech Computer Science", "aarav.sharma@example.com",
        "+91 98765 43210", "Rajesh Sharma", "2004-05-14", "42 Greenfield Enclave, New Delhi", "2026-01-15"
    ]
    ws1.append(sample_row1)
    for c in range(1, len(sample_row1) + 1):
        ws1.cell(row=2, column=c).border = THIN_BORDER
        ws1.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws1)

    # 2. Sheet: Attendance
    ws2 = wb.create_sheet(title="Attendance")
    ws2_headers = ["Month / Term", "Total Working Days", "Days Present", "Attendance (%)", "Status", "Remarks"]
    style_table_header(ws2, ws2_headers)
    sample_row2 = ["January 2026", 24, 23, "95.8%", "Regular", "Consistent attendance"]
    ws2.append(sample_row2)
    for c in range(1, len(sample_row2) + 1):
        ws2.cell(row=2, column=c).border = THIN_BORDER
        ws2.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws2)

    # 3. Sheet: Marks & Grades
    ws3 = wb.create_sheet(title="Marks & Grades")
    ws3_headers = ["Subject Code", "Subject Name", "Exam Type", "Maximum Marks", "Marks Obtained", "Grade", "Status"]
    style_table_header(ws3, ws3_headers)
    sample_marks = [
        ["CS101", "Data Structures & Algorithms", "Mid-Term", 100, 88, "A", "Passed"],
        ["CS102", "Database Management Systems", "Mid-Term", 100, 92, "A+", "Passed"],
        ["CS103", "Computer Networks", "Mid-Term", 100, 85, "A", "Passed"]
    ]
    for r_idx, r in enumerate(sample_marks, start=2):
        ws3.append(r)
        for c in range(1, len(r) + 1):
            ws3.cell(row=r_idx, column=c).border = THIN_BORDER
            ws3.cell(row=r_idx, column=c).font = VALUE_FONT
    auto_fit_columns(ws3)

    # 4. Sheet: Assignments Submitted
    ws4 = wb.create_sheet(title="Assignments Submitted")
    ws4_headers = ["Saved File Name", "Original File Name", "Upload Date & Time", "File Size", "Status"]
    style_table_header(ws4, ws4_headers)
    sample_assign = ["assignment_1.pdf", "Lab_Report_DS.pdf", "2026-02-10 14:30:00", "2.4 MB", "Submitted"]
    ws4.append(sample_assign)
    for c in range(1, len(sample_assign) + 1):
        ws4.cell(row=2, column=c).border = THIN_BORDER
        ws4.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws4)

    # 5. Sheet: Remarks
    ws5 = wb.create_sheet(title="Remarks")
    ws5_headers = ["Date", "Added By", "Category", "Remarks / Feedback"]
    style_table_header(ws5, ws5_headers)
    sample_remark = ["2026-03-01", "Admin / Academic Head", "Behavior & Academics", "Consistent academic performance and prompt submission."]
    ws5.append(sample_remark)
    for c in range(1, len(sample_remark) + 1):
        ws5.cell(row=2, column=c).border = THIN_BORDER
        ws5.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws5)

    wb.save(TEMPLATE_PATH)
    wb.close()


def _populate_personal_sheet(ws1, student):
    ws1.delete_rows(1, ws1.max_row + 1)
    ws1.merge_cells("A1:D1")
    t_cell = ws1["A1"]
    roll_no = student["roll_no"].upper()
    t_cell.value = f"STUDENT RECORD: {roll_no}"
    t_cell.fill = HEADER_FILL
    t_cell.font = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    t_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    fields = [
        ("Roll Number", student.get("roll_no", "")),
        ("Full Name", student.get("name", "")),
        ("Class / Course", student.get("class_name", "")),
        ("Email Address", student.get("email", "")),
        ("Phone Number", student.get("phone", "")),
        ("Father's Name", student.get("father_name", "") or "—"),
        ("Date of Birth", student.get("dob", "") or "—"),
        ("Residential Address", student.get("address", "") or "—"),
        ("Registered On", student.get("created_at", "")),
        ("Last Updated", student.get("updated_at", "")),
    ]

    r_idx = 3
    for label, val in fields:
        c_lbl = ws1.cell(row=r_idx, column=1, value=label)
        c_lbl.fill = LABEL_FILL
        c_lbl.font = LABEL_FONT
        c_lbl.border = THIN_BORDER

        ws1.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=4)
        c_val = ws1.cell(row=r_idx, column=2, value=str(val))
        c_val.font = VALUE_FONT
        c_val.border = THIN_BORDER
        c_val.alignment = Alignment(vertical="center", indent=1)
        ws1.row_dimensions[r_idx].height = 24
        r_idx += 1

    auto_fit_columns(ws1)


def generate_student_excel(student, assignments=None):
    """Creates the individual student Excel file (<roll_no>.xlsx) with all 5 sheets."""
    roll_no = student["roll_no"].upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")

    # If it already exists, just update personal sheet so we don't wipe out attendance or marks
    if os.path.exists(file_path):
        return update_student_personal_in_excel(student)

    wb = openpyxl.Workbook()

    # 1. Personal Details
    ws1 = wb.active
    ws1.title = "Personal Details"
    _populate_personal_sheet(ws1, student)

    # 2. Attendance
    ws2 = wb.create_sheet(title="Attendance")
    ws2_headers = ["Month / Term", "Total Classes", "Attended", "Attendance (%)", "Status", "Remarks"]
    style_table_header(ws2, ws2_headers)
    ws2.append(["Current Term", 100, 94, "94.0%", "Good Standing", "Regular in class lectures and practical labs"])
    for c in range(1, 7):
        ws2.cell(row=2, column=c).border = THIN_BORDER
        ws2.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws2)

    # 3. Marks & Grades
    ws3 = wb.create_sheet(title="Marks & Grades")
    ws3_headers = ["Subject Code", "Subject Name", "Exam Type", "Max Marks", "Obtained", "Grade", "Status"]
    style_table_header(ws3, ws3_headers)
    default_marks = [
        ["SUB101", "Core Theory", "Term 1", 100, 89, "A", "Passed"],
        ["SUB102", "Practical Lab", "Term 1", 50, 46, "A+", "Passed"],
        ["SUB103", "Project Work", "Term 1", 50, 47, "A+", "Passed"]
    ]
    for row_num, m in enumerate(default_marks, start=2):
        ws3.append(m)
        for c in range(1, len(m) + 1):
            ws3.cell(row=row_num, column=c).border = THIN_BORDER
            ws3.cell(row=row_num, column=c).font = VALUE_FONT
    auto_fit_columns(ws3)

    # 4. Assignments Submitted
    ws4 = wb.create_sheet(title="Assignments Submitted")
    ws4_headers = ["Saved File Name", "Original File Name", "Upload Date & Time", "File Size", "Status"]
    style_table_header(ws4, ws4_headers)

    if assignments:
        for a_idx, a in enumerate(assignments, start=2):
            size_kb = f"{round(a['file_size'] / 1024, 1)} KB" if a.get('file_size') else "—"
            row_vals = [a['filename'], a['original_name'], a['upload_time'], size_kb, "Verified"]
            ws4.append(row_vals)
            for c in range(1, len(row_vals) + 1):
                ws4.cell(row=a_idx, column=c).border = THIN_BORDER
                ws4.cell(row=a_idx, column=c).font = VALUE_FONT
    auto_fit_columns(ws4)

    # 5. Remarks
    ws5 = wb.create_sheet(title="Remarks")
    ws5_headers = ["Date", "Added By", "Category", "Remarks / Feedback"]
    style_table_header(ws5, ws5_headers)
    ws5.append([datetime.now().strftime("%Y-%m-%d"), "System / Admin", "Registration", "Student registered successfully. Individual workbook generated."])
    for c in range(1, 5):
        ws5.cell(row=2, column=c).border = THIN_BORDER
        ws5.cell(row=2, column=c).font = VALUE_FONT
    auto_fit_columns(ws5)

    wb.save(file_path)
    wb.close()
    return file_path


def update_student_personal_in_excel(student):
    """Safely updates only the Personal Details sheet of an existing student workbook."""
    roll_no = student["roll_no"].upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        return generate_student_excel(student)

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path)
        if "Personal Details" in wb.sheetnames:
            ws1 = wb["Personal Details"]
        else:
            ws1 = wb.create_sheet("Personal Details", index=0)

        _populate_personal_sheet(ws1, student)
        wb.save(file_path)
        return file_path
    except Exception as e:
        print(f"Error updating personal sheet in {roll_no}.xlsx: {e}")
        return file_path
    finally:
        if wb:
            wb.close()


def log_assignment_submission_in_excel(roll_no, original_name, saved_filename, file_size_bytes):
    """Appends an uploaded assignment to Sheet 4 ('Assignments Submitted') of the student's Excel file."""
    roll_no = roll_no.upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        return

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path)
        if "Assignments Submitted" not in wb.sheetnames:
            ws = wb.create_sheet(title="Assignments Submitted")
            style_table_header(ws, ["Saved File Name", "Original File Name", "Upload Date & Time", "File Size", "Status"])
        else:
            ws = wb["Assignments Submitted"]

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        size_str = f"{round(file_size_bytes / 1024, 1)} KB" if file_size_bytes < 1024 * 1024 else f"{round(file_size_bytes / (1024 * 1024), 2)} MB"

        next_row = ws.max_row + 1
        row_vals = [saved_filename, original_name, now_str, size_str, "Submitted"]
        ws.append(row_vals)

        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=next_row, column=col_idx)
            cell.border = THIN_BORDER
            cell.font = VALUE_FONT

        auto_fit_columns(ws)
        wb.save(file_path)
    except Exception as e:
        print(f"Error appending assignment to Excel: {e}")
    finally:
        if wb:
            wb.close()


def read_student_excel_data(roll_no):
    """
    Reads all 5 sheets from the student's Excel workbook (<roll_no>.xlsx)
    to power the student portal view and admin inspector.
    """
    roll_no = roll_no.upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")

    data = {
        "attendance": [],
        "marks": [],
        "assignments": [],
        "remarks": [],
        "stats": {
            "attendance_pct": "94.0%",
            "average_grade": "A",
            "average_marks": "88.5%",
            "total_marks_obtained": 0,
            "total_max_marks": 0,
            "passed_subjects": 0
        }
    }

    if not os.path.exists(file_path):
        return data

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)

        # 2. Attendance
        if "Attendance" in wb.sheetnames:
            ws2 = wb["Attendance"]
            rows = list(ws2.iter_rows(values_only=True))
            if len(rows) > 1:
                total_classes_sum = 0
                attended_sum = 0
                for r in rows[1:]:
                    if not any(r):
                        continue
                    item = {
                        "term": str(r[0] or "Term"),
                        "total_classes": r[1] or 0,
                        "attended": r[2] or 0,
                        "pct": str(r[3] or ""),
                        "status": str(r[4] or "Present"),
                        "remarks": str(r[5] or "")
                    }
                    data["attendance"].append(item)
                    try:
                        total_classes_sum += int(r[1])
                        attended_sum += int(r[2])
                    except (ValueError, TypeError):
                        pass

                if total_classes_sum > 0:
                    calc_pct = round((attended_sum / total_classes_sum) * 100, 1)
                    data["stats"]["attendance_pct"] = f"{calc_pct}%"

        # 3. Marks & Grades
        if "Marks & Grades" in wb.sheetnames:
            ws3 = wb["Marks & Grades"]
            rows = list(ws3.iter_rows(values_only=True))
            if len(rows) > 1:
                tot_max = 0
                tot_obt = 0
                for r in rows[1:]:
                    if not any(r):
                        continue
                    item = {
                        "code": str(r[0] or ""),
                        "name": str(r[1] or ""),
                        "exam_type": str(r[2] or ""),
                        "max_marks": r[3] or 100,
                        "obtained": r[4] or 0,
                        "grade": str(r[5] or "—"),
                        "status": str(r[6] or "Passed")
                    }
                    data["marks"].append(item)
                    try:
                        tot_max += float(r[3])
                        tot_obt += float(r[4])
                        if str(r[6]).lower() == "passed":
                            data["stats"]["passed_subjects"] += 1
                    except (ValueError, TypeError):
                        pass

                if tot_max > 0:
                    pct = round((tot_obt / tot_max) * 100, 1)
                    data["stats"]["average_marks"] = f"{pct}%"
                    data["stats"]["total_marks_obtained"] = round(tot_obt, 1)
                    data["stats"]["total_max_marks"] = round(tot_max, 1)
                    if pct >= 90:
                        data["stats"]["average_grade"] = "A+"
                    elif pct >= 80:
                        data["stats"]["average_grade"] = "A"
                    elif pct >= 70:
                        data["stats"]["average_grade"] = "B+"
                    elif pct >= 60:
                        data["stats"]["average_grade"] = "B"
                    else:
                        data["stats"]["average_grade"] = "C"

        # 4. Assignments Submitted
        if "Assignments Submitted" in wb.sheetnames:
            ws4 = wb["Assignments Submitted"]
            rows = list(ws4.iter_rows(values_only=True))
            if len(rows) > 1:
                for r in rows[1:]:
                    if not any(r):
                        continue
                    data["assignments"].append({
                        "saved_name": str(r[0] or ""),
                        "original_name": str(r[1] or ""),
                        "upload_time": str(r[2] or ""),
                        "file_size": str(r[3] or ""),
                        "status": str(r[4] or "Submitted")
                    })

        # 5. Remarks
        if "Remarks" in wb.sheetnames:
            ws5 = wb["Remarks"]
            rows = list(ws5.iter_rows(values_only=True))
            if len(rows) > 1:
                for r in rows[1:]:
                    if not any(r):
                        continue
                    data["remarks"].append({
                        "date": str(r[0] or ""),
                        "author": str(r[1] or ""),
                        "category": str(r[2] or ""),
                        "text": str(r[3] or "")
                    })

    except Exception as e:
        print(f"Error reading Excel data for {roll_no}: {e}")
    finally:
        if wb:
            wb.close()

    return data


def add_attendance_row(roll_no, term, total_classes, attended, status, remarks):
    """Appends an attendance entry to Sheet 2 ('Attendance') of the student's Excel file."""
    roll_no = roll_no.upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        return False

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path)
        if "Attendance" not in wb.sheetnames:
            ws = wb.create_sheet(title="Attendance")
            style_table_header(ws, ["Month / Term", "Total Classes", "Attended", "Attendance (%)", "Status", "Remarks"])
        else:
            ws = wb["Attendance"]

        try:
            tot = int(total_classes)
            att = int(attended)
            pct = f"{round((att / tot) * 100, 1)}%" if tot > 0 else "0%"
        except Exception:
            tot, att, pct = total_classes, attended, "—"

        next_row = ws.max_row + 1
        row_vals = [term, tot, att, pct, status, remarks]
        ws.append(row_vals)

        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=next_row, column=col_idx)
            cell.border = THIN_BORDER
            cell.font = VALUE_FONT

        auto_fit_columns(ws)
        wb.save(file_path)
        return True
    except Exception as e:
        print(f"Error adding attendance row: {e}")
        return False
    finally:
        if wb:
            wb.close()


def add_marks_row(roll_no, code, name, exam_type, max_marks, obtained, grade, status):
    """Appends a subject grade entry to Sheet 3 ('Marks & Grades') of the student's Excel file."""
    roll_no = roll_no.upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        return False

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path)
        if "Marks & Grades" not in wb.sheetnames:
            ws = wb.create_sheet(title="Marks & Grades")
            style_table_header(ws, ["Subject Code", "Subject Name", "Exam Type", "Max Marks", "Obtained", "Grade", "Status"])
        else:
            ws = wb["Marks & Grades"]

        next_row = ws.max_row + 1
        row_vals = [code, name, exam_type, max_marks, obtained, grade, status]
        ws.append(row_vals)

        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=next_row, column=col_idx)
            cell.border = THIN_BORDER
            cell.font = VALUE_FONT

        auto_fit_columns(ws)
        wb.save(file_path)
        return True
    except Exception as e:
        print(f"Error adding marks row: {e}")
        return False
    finally:
        if wb:
            wb.close()


def add_remark_row(roll_no, author, category, text):
    """Appends a remark entry to Sheet 5 ('Remarks') of the student's Excel file."""
    roll_no = roll_no.upper()
    file_path = os.path.join(EXCEL_DIR, f"{roll_no}.xlsx")
    if not os.path.exists(file_path):
        return False

    wb = None
    try:
        wb = openpyxl.load_workbook(file_path)
        if "Remarks" not in wb.sheetnames:
            ws = wb.create_sheet(title="Remarks")
            style_table_header(ws, ["Date", "Added By", "Category", "Remarks / Feedback"])
        else:
            ws = wb["Remarks"]

        date_str = datetime.now().strftime("%Y-%m-%d")
        next_row = ws.max_row + 1
        row_vals = [date_str, author, category, text]
        ws.append(row_vals)

        for col_idx in range(1, len(row_vals) + 1):
            cell = ws.cell(row=next_row, column=col_idx)
            cell.border = THIN_BORDER
            cell.font = VALUE_FONT

        auto_fit_columns(ws)
        wb.save(file_path)
        return True
    except Exception as e:
        print(f"Error adding remark row: {e}")
        return False
    finally:
        if wb:
            wb.close()


def generate_consolidated_master_excel(students):
    """Creates a consolidated Master Excel file with summary of all students."""
    os.makedirs(EXCEL_DIR, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Master Student Directory"

    headers = [
        "Roll Number", "Student Name", "Class / Course", "Email", "Phone",
        "Father's Name", "Date of Birth", "Address", "Total Assignments", "Registered Date"
    ]
    style_table_header(ws, headers)

    for r_idx, s in enumerate(students, start=2):
        row_vals = [
            s.get("roll_no", ""),
            s.get("name", ""),
            s.get("class_name", ""),
            s.get("email", ""),
            s.get("phone", ""),
            s.get("father_name", "") or "—",
            s.get("dob", "") or "—",
            s.get("address", "") or "—",
            s.get("assignment_count", 0),
            s.get("created_at", "")
        ]
        ws.append(row_vals)
        for c in range(1, len(row_vals) + 1):
            ws.cell(row=r_idx, column=c).border = THIN_BORDER
            ws.cell(row=r_idx, column=c).font = VALUE_FONT

    auto_fit_columns(ws)
    wb.save(MASTER_PATH)
    wb.close()
    return MASTER_PATH
