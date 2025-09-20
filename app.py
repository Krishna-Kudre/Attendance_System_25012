import sqlite3
import qrcode
import cv2
import os
from datetime import datetime
import pandas as pd

# --------------------- DATABASE SETUP ---------------------
def create_tables():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE,
        name TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# --------------------- STUDENT FUNCTIONS ---------------------
def add_student():
    roll_number = input("Enter Roll Number: ")
    name = input("Enter Student Name: ")
    
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (roll_number, name) VALUES (?, ?)", (roll_number, name))
        conn.commit()
        print(f"Student {name} added successfully!")
        generate_qr(roll_number, name)
    except sqlite3.IntegrityError:
        print("Roll number already exists!")
    conn.close()

def generate_qr(roll_number, name):
    data = f"{roll_number}|{name}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    if not os.path.exists("QR_Codes"):
        os.makedirs("QR_Codes")
    
    filename = f"QR_Codes/qr_{roll_number}.png"
    img.save(filename)
    print(f"QR code saved as {filename}")

# --------------------- ATTENDANCE FROM IMAGE ---------------------
def scan_attendance_from_image():
    folder = input("Enter folder path with QR code images: ")
    if not os.path.exists(folder):
        print("Folder not found!")
        return
    
    detector = cv2.QRCodeDetector()
    for file in os.listdir(folder):
        if file.endswith(".png") or file.endswith(".jpg"):
            path = os.path.join(folder, file)
            img = cv2.imread(path)
            data, bbox, _ = detector.detectAndDecode(img)
            if data:
                roll_number, name = data.split("|")
                mark_attendance(roll_number, name)

def mark_attendance(roll_number, name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT student_id FROM students WHERE roll_number=?", (roll_number,))
    student = cursor.fetchone()
    
    if student:
        student_id = student[0]
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
        if cursor.fetchone():
            print(f"Attendance already marked for {name}")
        else:
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", 
                           (student_id, today, "Present"))
            conn.commit()
            print(f"Attendance marked for {name}")
    conn.close()

# --------------------- REPORT ---------------------
def view_report():
    conn = sqlite3.connect("attendance.db")
    df = pd.read_sql_query('''
    SELECT s.roll_number, s.name, a.date, a.status
    FROM students s
    LEFT JOIN attendance a ON s.student_id = a.student_id
    ORDER BY a.date
    ''', conn)
    
    print(df)
    df.to_csv("attendance_report.csv", index=False)
    print("Report saved as attendance_report.csv")
    conn.close()

# --------------------- MENU ---------------------
def main_menu():
    create_tables()
    while True:
        print("\n----- QR Attendance System (Image-based) -----")
        print("1. Add Student")
        print("2. Scan Attendance from Images")
        print("3. View/Export Attendance Report")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            add_student()
        elif choice == '2':
            scan_attendance_from_image()
        elif choice == '3':
            view_report()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
