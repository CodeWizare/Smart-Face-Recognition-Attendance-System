import sqlite3

# Connect to the SQLite database (it will create the database file if it doesn't exist)
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Insert students
students = [
    ("Aryan"),
    ("Bipul"),
    ("Akshay"),
    ("Sudhansu"),
    ("Uday"),
    ("Meri Wali"),
    ("Yash"),
    ("Bhumi"),
    ("Pradeep")
]

cursor.executemany('INSERT INTO Students (name) VALUES (?)', [(name,) for name in students])

# Insert subjects
subjects = [
    ("Math"),
    ("Science"),
    ("English"),
    ("History"),
    ("Computer Science")
]

cursor.executemany('INSERT INTO Subjects (subject_name) VALUES (?)', [(subject,) for subject in subjects])

# Insert attendance records
attendance_data = [
    ("Aryan", "Math", "2025-04-01", "Present"),
    ("Bipul", "Science", "2025-04-01", "Absent"),
    ("Akshay", "English", "2025-04-01", "Present"),
    ("Sudhansu", "History", "2025-04-01", "Absent"),
    ("Uday", "Math", "2025-04-01", "Present"),
    ("Meri Wali", "Science", "2025-04-01", "Present"),
    ("Yash", "English", "2025-04-01", "Absent"),
    ("Bhumi", "History", "2025-04-01", "Present"),
    ("Pradeep", "Computer Science", "2025-04-01", "Absent")
]

# Insert attendance data
for student_name, subject_name, date, status in attendance_data:
    cursor.execute('''
        INSERT INTO Attendance (student_id, subject_id, date, status)
        SELECT s.id, sub.id, ?, ?
        FROM Students s
        JOIN Subjects sub ON sub.subject_name = ?
        WHERE s.name = ?
    ''', (date, status, subject_name, student_name))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("All records inserted successfully!")
