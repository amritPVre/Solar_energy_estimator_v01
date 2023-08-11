# -*- coding: utf-8 -*-
"""
Created on Mon May 22 01:47:14 2023

@author: amrit
"""

import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText


st.set_page_config(page_title="Documentation", page_icon="🗎")

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

def Documentation():
    st.markdown('____')
    st.markdown("""
# Solar Energy Estimator App Documentation

## Overview

The Solar Energy Estimator App is a powerful tool for predicting solar energy production based on specific parameters. It allows users to input various parameters such as plant capacity, location coordinates, tilt angle, azimuth angle, and module type. Based on these inputs, the app generates hourly, daily, and monthly solar irradiance values on an inclined plane (GII) and estimates the corresponding solar energy generation.

The primary data source for the application is the PVLIB library, which uses the NASA Power Database.

## Key Features

### Location-Based Solar Energy Estimation

The user can enter their location coordinates (latitude and longitude), which the app uses to estimate solar irradiance and energy production for that specific location.

### Solar Panel Configuration

The app allows the user to configure their solar panel settings by entering the plant capacity, tilt angle, azimuth angle, and the desired module type. These settings are used to more accurately estimate the energy production.

### Time-Based Energy Estimation

The app provides solar energy generation values for different time frames: hourly, daily, and monthly. This allows users to understand the variability of solar energy production over time and plan accordingly.

### Visual Representation

The app generates dynamic charts for visual representation of the estimated solar energy values, using the powerful plotting library, Plotly.

## API Used

The app leverages the PVLIB Python library to make solar energy predictions. PVLIB provides a set of procedures and functions that allow developers to model solar energy production with a high degree of accuracy.
Link to API: https://pvlib-python.readthedocs.io/en/stable/index.html 

## Functionality

Upon receiving user input, the app employs PVLIB's solar position algorithm to calculate the position of the sun at various times of the day. The solar irradiance on an inclined plane is then calculated based on these solar positions. Finally, the app estimates solar energy production based on the calculated solar irradiance and the solar panel configuration specified by the user.

## Conclusion

The Solar Energy Estimator App is a user-friendly and robust tool for anyone interested in estimating solar energy production. Whether for home use, commercial projects, or academic research, this app provides accurate estimations and insightful visualizations, making the complex task of predicting solar energy generation simple and straightforward.
""")

Documentation()
