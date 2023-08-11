# -*- coding: utf-8 -*-
"""
Created on Mon May 22 01:47:14 2023

@author: amrit
"""

import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="About Me", page_icon="🧑🏻‍💻")

#Feedback, Rating & e-mail

conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

mail_pass=st.secrets['mail_pass']


cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY,
        rating INTEGER NOT NULL,
        feedback_text TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")
conn.commit()

# Add rating slider to sidebar
rating = st.sidebar.slider("Rate our app:", 0, 5, 3)

# Add feedback text area to sidebar
feedback = st.sidebar.text_area("Please leave your feedback:")

# Add email input to sidebar
email = st.sidebar.text_input("Please enter your email:")

def send_email(email):
    message = """\
    <html>
      <body>
        <p>Thank you for your valuable feedback!<br><br>
        We're excited to share what's coming in the next upgrade of our app:
        </p>
        <ul>
          <li><strong>Secure Login Access:</strong> Enhanced security to protect your data.</li>
          <li><strong>Download Data in Spreadsheet:</strong> Export your information with ease.</li>
          <li><strong>PDF Report Generation:</strong> Create detailed reports in PDF format.</li>
        </ul>
        <p>Your insights help us improve, and we look forward to offering you these new features soon. Stay tuned!<br><br>
        Best,<br>
        Amrit Mandal</p>
      </body>
    </html>
    """

    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Thank You for Your Feedback'
    msg['From'] = 'solarapp98@gmail.com'
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('solarapp98@gmail.com', mail_pass)
        server.send_message(msg)

# Add submission button to sidebar
if st.sidebar.button("Submit Feedback"):
    cursor.execute("INSERT INTO feedback (rating, feedback_text, email) VALUES (?, ?, ?)", (rating, feedback, email))
    conn.commit()
    send_email(email)
    st.sidebar.write("Thank you for your feedback! A thank you note has been sent to your email.")
    


#Main Program#---------------------------------------


def about_me():
    st.write("# Welcome to My Solar Energy Estimator App! 👋")
    st.markdown('____')
    st.title("About Me")

    st.header("Amrit Mandal")
    st.markdown("""
    - Phone: +91 8116401052
    - Email: [amrit.mandal0191@gmail.com](mailto:amrit.mandal0191@gmail.com)
    - LinkedIn: [https://www.linkedin.com/in/amritmandal](https://www.linkedin.com/in/amritmandal)
    """)
    st.markdown('____')
    st.subheader("Solar PV Professional")
    st.markdown("""
    - Software Skills: Pvsyst, PlantPredict, Helioscope, AutoCAD, SketchUp, SolarGIS, HOMER, MS Office & Project & Other various Solar PV Engg. Related Tools
    - Soft Skills: Creativity, Collaboration, Problem Solving, Communication
    """)
    st.markdown('____')

about_me()
