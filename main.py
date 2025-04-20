import streamlit as st
import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime
import sqlite3
from fpdf import FPDF

# Directories and database
KNOWN_FACES_DIR = "Images"
ATTENDANCE_DB = r'C:\Users\aryan\PycharmProjects\PythonProject5\attendance.db'

# DB setup
conn = sqlite3.connect(ATTENDANCE_DB, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')
conn.commit()

# Load known faces
def load_known_faces():
    known_faces = {}
    for filename in os.listdir(KNOWN_FACES_DIR):
        img_path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces[os.path.splitext(filename)[0]] = encodings[0]
    return known_faces

known_faces = load_known_faces()

# UI
st.set_page_config(page_title="Smart Attendance System", layout="centered")
st.title("📸 Smart Face Recognition Attendance System")

# Sidebar menu
menu = ["Home", "View Attendance", "Download Attendance as PDF", "Search Attendance"]
choice = st.sidebar.selectbox("Select Option", menu)

# Home Page: Subject and Camera Selector
if choice == "Home":
    subject = st.selectbox("Select Subject", ["Math", "Science", "English", "History"], key="subject")
    camera_option = st.selectbox("Select Camera", ["Laptop Camera", "Phone Camera"], key="camera_option")
    phone_cam_url = "http://192.0.0.4:8080/video"  # Update IP as per your phone

    # Init camera session
    if "cap" not in st.session_state:
        st.session_state.cap = None

    if st.button("Start Camera"):
        if st.session_state.cap is None:
            cam_source = 0 if camera_option == "Laptop Camera" else phone_cam_url
            st.session_state.cap = cv2.VideoCapture(cam_source)
            st.success("Camera Started")
        else:
            st.warning("Camera already running!")

    if st.button("Stop Camera"):
        if st.session_state.cap:
            st.session_state.cap.release()
            st.session_state.cap = None
            st.success("Camera Stopped")
        else:
            st.warning("No camera is running!")

    stframe = st.empty()
    if st.session_state.cap and st.session_state.cap.isOpened():
        ret, frame = st.session_state.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(rgb_frame, channels="RGB")

    # Capture attendance
    if st.button("📷 Capture Attendance"):
        if st.session_state.cap and st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                for encoding in face_encodings:
                    matches = face_recognition.compare_faces(list(known_faces.values()), encoding)
                    name = "Unknown"
                    if True in matches:
                        match_index = matches.index(True)
                        name = list(known_faces.keys())[match_index]
                    if name != "Unknown":
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("INSERT INTO attendance (name, subject, timestamp) VALUES (?, ?, ?)",
                                       (name, subject, now))
                        conn.commit()
                        st.success(f"✅ Attendance marked for {name}")
                    else:
                        st.warning("❌ Unknown face")
        else:
            st.warning("Camera not started!")

# View all attendance
elif choice == "View Attendance":
    st.subheader("📋 All Attendance Records")
    cursor.execute("SELECT * FROM attendance")
    rows = cursor.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Name", "Subject", "Timestamp"])
        st.dataframe(df)
    else:
        st.warning("No attendance records found.")

# Download as PDF
elif choice == "Download Attendance as PDF":
    def generate_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Name", border=1, align="C")
        pdf.cell(60, 10, "Subject", border=1, align="C")
        pdf.cell(60, 10, "Timestamp", border=1, align="C")
        pdf.ln()
        cursor.execute("SELECT * FROM attendance")
        rows = cursor.fetchall()
        pdf.set_font("Arial", size=12)
        for row in rows:
            pdf.cell(40, 10, row[1], border=1, align="C")
            pdf.cell(60, 10, row[2], border=1, align="C")
            pdf.cell(60, 10, row[3], border=1, align="C")
            pdf.ln()
        output_file = "attendance.pdf"
        pdf.output(output_file)
        return output_file

    file = generate_pdf()
    with open(file, "rb") as f:
        st.download_button("⬇️ Download Attendance PDF", data=f, file_name="attendance.pdf", mime="application/pdf")

# Search attendance
elif choice == "Search Attendance":
    st.subheader("🔍 Search Attendance")
    student_name = st.text_input("Enter Student Name")
    selected_date = st.date_input("Select Date")
    selected_subject = st.selectbox("Select Subject", ["Math", "Science", "English", "History"], key="search_subject")

    if st.button("Search"):
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        query = "SELECT * FROM attendance WHERE name=? AND subject=? AND DATE(timestamp)=?"
        cursor.execute(query, (student_name, selected_subject, selected_date_str))
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Name", "Subject", "Timestamp"])
            st.dataframe(df)

            def generate_filtered_pdf(df, name, subject, date):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Attendance Report - {name}, {subject}, {date}", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(20, 10, "ID", border=1)
                pdf.cell(50, 10, "Name", border=1)
                pdf.cell(50, 10, "Subject", border=1)
                pdf.cell(60, 10, "Timestamp", border=1)
                pdf.ln()
                pdf.set_font("Arial", '', 10)
                for index, row in df.iterrows():
                    pdf.cell(20, 10, str(row["ID"]), border=1)
                    pdf.cell(50, 10, row["Name"], border=1)
                    pdf.cell(50, 10, row["Subject"], border=1)
                    pdf.cell(60, 10, row["Timestamp"], border=1)
                    pdf.ln()
                filename = f"{name}_{subject}_{date}_Attendance.pdf".replace(" ", "_")
                pdf.output(filename)
                return filename

            filtered_pdf = generate_filtered_pdf(df, student_name, selected_subject, selected_date_str)
            with open(filtered_pdf, "rb") as f:
                st.download_button("📄 Download This Record as PDF", data=f, file_name=filtered_pdf, mime="application/pdf")
        else:
            st.warning(f"No record found for {student_name} on {selected_date_str}")

# Footer
st.markdown("---")
st.markdown("<center>Developed by <b>Aryan Salam</b></center>", unsafe_allow_html=True)
