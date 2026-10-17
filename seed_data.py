"""
Seed data script to initialize SQLite database, create default admin,
seed sample students with secure tokens, and generate their 5-sheet Excel workbooks.
"""

import os
import db
import excel_service

def seed():
    print("[*] Initializing SQLite database...")
    db.init_db()

    print("[*] Initializing Excel directory and template...")
    excel_service.init_excel_system()

    sample_students = [
        {
            "roll_no": "ROLL101",
            "name": "Aarav Sharma",
            "class_name": "B.Tech Computer Science",
            "email": "aarav.sharma@example.com",
            "phone": "+91 98765 43210",
            "father_name": "Rajesh Sharma",
            "dob": "2004-05-14",
            "address": "42 Greenfield Enclave, New Delhi, India"
        },
        {
            "roll_no": "ROLL102",
            "name": "Priya Patel",
            "class_name": "B.Sc Information Technology",
            "email": "priya.patel@example.com",
            "phone": "+91 98234 56789",
            "father_name": "Mahesh Patel",
            "dob": "2005-08-22",
            "address": "15 Lotus Apartments, Ahmedabad, Gujarat"
        },
        {
            "roll_no": "ROLL103",
            "name": "Rohan Verma",
            "class_name": "BCA (Software Engineering)",
            "email": "rohan.verma@example.com",
            "phone": "+91 97112 34567",
            "father_name": "Sunil Verma",
            "dob": "2004-11-03",
            "address": "88 Civil Lines, Jaipur, Rajasthan"
        }
    ]

    for s in sample_students:
        roll_no, token = db.create_or_update_student(s)
        student_obj = db.get_student(roll_no)
        excel_service.generate_student_excel(student_obj)
        print(f"[+] Seeded {roll_no}: {s['name']} | Token: {token}")

    print("[*] Seed data completed successfully!")

if __name__ == "__main__":
    seed()
