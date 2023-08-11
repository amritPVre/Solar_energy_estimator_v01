# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 19:33:17 2023

@author: amrit
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pvlib
from pvlib import location
from pvlib import irradiance
from plotly.subplots import make_subplots
#from tzwhere.tzwhere import tzwhere
import folium
from streamlit_folium import folium_static
import base64
import requests
from PIL import Image
from io import BytesIO
from geopy.geocoders import Nominatim
import pytz
from pytz import timezone
import sqlite3
import smtplib
from email.mime.text import MIMEText


st.set_page_config(page_title="Solar Energy Estimator", page_icon="☀️",layout="wide")

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


st.markdown(
    """
    <div style="background-color:#eb4423;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Solar Energy Estimator</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write('\n')
st.write('\n')

st.markdown(
    """
    <div style="background-color:#dae5e8;padding:10px;border-radius:10px"><h7 style="color:#3b404a;text-align:center;">
    Welcome to the Solar Energy Estimator! This application is a robust tool designed to help users calculate 
    potential solar energy production based on specific inputs such as plant capacity, location coordinates, 
    tilt angle, azimuth angle, and selected module. Leveraging NASA's POWER database and the PVLib Python library, 
    the app provides detailed hourly, daily, and monthly estimates of solar irradiance on an inclined plane and 
    respective solar energy generation values. Explore the impact of varying conditions and setups on your 
    solar energy outcomes and make informed decisions about your solar energy projects. Let's harness 
    the power of the sun efficiently and sustainably!
    </h7>
    </div>
    """,
    unsafe_allow_html=True,
    )
st.write('\n')
st.write('\n')
st.write('_______')


st.write('\n')

all_timezones = pytz.all_timezones
default_ix=all_timezones.index('Asia/Calcutta')


# Load module specifications from CSV
module_df = pd.read_csv('module_data.csv')
col1,col2,col3=st.columns([0.5,2,0.5])
# Begin form
with col2.form(key='my_form'):
    # Get plant capacity from user
    plant_cap = st.number_input("Enter the plant capacity in kW")
    # User inputs
    latitude = st.number_input('Enter latitude',22.7)
    longitude = st.number_input('Enter longitude',73.7)
    tz_str = st.selectbox("Select your Time Zone", all_timezones,index=default_ix)
    
    # Let users select a model
    module_selection = st.selectbox("Select a model", options=module_df['Model Name'].unique())
    # Get selected module data
    module = module_df[(module_df['Model Name'] == module_selection)].iloc[0]
    module_efficiency = module['Efficiency'] / 100
    surface_tilt = st.slider('Enter surface tilt',0.0,90.00,20.00,0.10)
    surface_azimuth = st.slider('Enter surface azimuth (180 means facing direct to south)',-180,180,180,1)
    #module_efficiency = st.number_input('Enter module efficiency (%)', min_value=0.0, max_value=100.0, step=0.1, value=21.0, format='%f') / 100
    pr = st.number_input('Enter plant Performance Ratio (%PR)', min_value=0.0, max_value=100.0, step=0.1, value=81.0, format='%f') / 100
    module_watt_peak = module['Watt peak']
    area=module['Area']

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    

if submitted:
    total_modules = round(plant_cap / (module_watt_peak / 1000),0)
    plant_capacity=(total_modules*module_watt_peak)/1000
    total_area=area*total_modules
    tz_str=tz_str
    
    col1,col2=st.columns([1,1])
    with col1:
            # Create a map centered at the input coordinates
        m = folium.Map(location=[latitude, longitude], width='50%', height='50%')
        # Add a marker at the input coordinates
        folium.Marker([latitude, longitude]).add_to(m)
        # Display the map
        folium_static(m)
    
    with col2:
        # Display the image
        image_path = '2.2_SolarPVDiagram.png'
        st.image(image_path, caption='A Schematic Diagram of Solar Photovoltaic Power Plant', use_column_width=True)

    st.write('______________')
    a1,a2,a3=st.columns([0.5,2,0.5])
    a2.header('Daily & Monthly Solar Irradiation Values')
    st.write('\n')
    m1,m2,m3=st.columns(3)
    
    col1,col2=st.columns(2)
    

    # Get specific energy production for each month using PVLIB
    def calculate_solar_production(latitude, longitude, tz_str, surface_tilt, surface_azimuth, module_efficiency, pr):
        # Define the location
        site = location.Location(latitude, longitude, tz=tz_str)

        # Define a range of dates for one year
        times = pd.date_range(start='2021-01-01', end='2022-01-01', freq='H', tz=tz_str)
        times = times[:-1]  # remove the last hour

        # Get solar azimuth and zenith to pass to the transposition function
        solar_position = site.get_solarposition(times)

        # Get irradiance data using the DISC model
        irrad_data = site.get_clearsky(times)

        # Calculate POA irradiance
        poa_irrad = irradiance.get_total_irradiance(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth, solar_zenith=solar_position['apparent_zenith'], solar_azimuth=solar_position['azimuth'], dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'])
        
        #st.write(poa_irrad)
        daily_gii=(poa_irrad['poa_global']/1000).resample('D').sum()
        #max-min values
        max_daily_gii=daily_gii.max()
        min_daily_gii=daily_gii.min()

        
        m1.metric(label='Max Daily GII (kWh/m\u00b2)',value="{:.2f}".format(max_daily_gii))
        m2.metric(label='Yearly Total GII (kWh/m\u00b2)/year',value="{:.2f}".format(daily_gii.sum()))
        m3.metric(label='Min Daily GII (kWh/m\u00b2)',value="{:.2f}".format(min_daily_gii))
        
        daily_gii=pd.DataFrame({"Daily Solar Irradiation (kWh/m2)": daily_gii})
       
        
        col1.write('Daily Solar Irradiation')
        col1.write(daily_gii)
        

        
        
        
        monthly_gii = daily_gii.resample('M').sum()
        monthly_gii=pd.DataFrame(monthly_gii)
        monthly_gii.columns = ["Monthly Solar Irradiation (kWh/m2)"]
        monthly_gii = monthly_gii.reset_index()
        # Convert the dates to datetime objects & get the month names
        monthly_gii['Month'] = pd.to_datetime(monthly_gii['index']).dt.month_name()
        monthly_gii = monthly_gii.drop(columns=['index'])
        # Make 'Month' column to be the first column
        monthly_gii = monthly_gii.set_index('Month').reset_index()
        
        col2.write('Monthly Solar Irradiation')
        col2.write(monthly_gii)
        # Convert irradiance to energy production
        
        #ploting of Daily solar GII
            
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=daily_gii.index, y=daily_gii['Daily Solar Irradiation (kWh/m2)'], mode='lines', name='Daily Solar Irradiation'))
        
        # Add titles and labels
        fig1.update_layout(title_text="Daily Solar Irradiation (kWh/m2)")
        fig1.update_xaxes(title_text="Date")
        fig1.update_yaxes(title_text="Irradiation")
        
        col1.plotly_chart(fig1, use_container_width=True)
        
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
                        x=monthly_gii['Month'],
                        y=monthly_gii['Monthly Solar Irradiation (kWh/m2)'],
                        name="Monthly Solar Irradiation (kWh/m2)",
                        marker_color='indianred'
        ))
        
        fig2.update_layout(title_text='Monthly Solar Irradiation (kWh/m2)',
                          xaxis=dict(type='category'))
                
        
        col2.plotly_chart(fig2, use_container_width=True)
        
        
        hourly_production = (poa_irrad['poa_global']/1000) * module_efficiency* pr
        daily_production = hourly_production.resample('D').sum()
        monthly_production = daily_production.resample('M').sum()
        
        
        

        return daily_production, monthly_production
        
    
    daily_production, specific_energy = calculate_solar_production(latitude, longitude, tz_str, surface_tilt, surface_azimuth, module_efficiency, pr)
    energy_df = pd.DataFrame(columns=['Month', 'Solar Energy Production'])
    
    #st.write('Daily Production',daily_production)
    #st.write('spec_energy',specific_energy)
    #st.write('totalarea',total_area)
    
    st.write('_________')
    a1,a2,a3=st.columns([0.5,2,0.5])
    a2.header('Daily & Monthly Solar Energy Generation Values')
    st.write('\n')
    m1,m2,m3=st.columns(3)
    col1,col2=st.columns(2)
        



    #st.write('//Updated Daily Solar Energy',daily_production)
    total_daily_production = daily_production * total_area
    
    m1.metric(label='Max Daily Solar Energy (kWh)',value="{:.2f}".format(total_daily_production.max()))
    m2.metric(label='Yearly Total Solar Energy (kWh/year)',value="{:.2f}".format(total_daily_production.sum()))
    m3.metric(label='Min Daily Solar Energy (kWh)',value="{:.2f}".format(total_daily_production.min()))

    total_daily_production=pd.DataFrame({"Daily Solar Energy Production (kWh)": total_daily_production})

    col1.write('Daily Solar Energy Production')
    col1.write(total_daily_production)
    total_daily_production.index = daily_production.index.tz_localize(None)
    
    total_monthly_production=total_daily_production.resample('M').sum()
    total_monthly_production=pd.DataFrame(total_monthly_production)
    total_monthly_production.columns=["Monthly Solar Energy Production (kWh)"]
    
   
    total_monthly_production = total_monthly_production.reset_index()
    # Convert the dates to datetime objects & get the month names
    total_monthly_production['Month'] = pd.to_datetime(total_monthly_production['index']).dt.month_name()
    total_monthly_production = total_monthly_production.drop(columns=['index'])
    # Make 'Month' column to be the first column
    total_monthly_production = total_monthly_production.set_index('Month').reset_index()
    
    col2.write('Monthly Solar Energy Production')
    col2.write(total_monthly_production)
    
    #Data Visualization#-----------------------------------------
    #Daily Values
    st.write('_________')

    # Create DataFrame for plotting
    
    col1,col2=st.columns(2)

    
    
    # Plotting of daily solar energy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=total_daily_production.index, y=total_daily_production['Daily Solar Energy Production (kWh)'], mode='lines', name='Daily Solar Energy Production'))
    
    # Add titles and labels
    fig.update_layout(title_text="Daily Solar Energy Production (kWh)")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Energy")
    
    col1.plotly_chart(fig, use_container_width=True)
    
    # Plotting of monthly solar energy
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
                    x=total_monthly_production['Month'],
                    y=total_monthly_production['Monthly Solar Energy Production (kWh)'],
                    name="Monthly Solar Energy Production (kWh)",
                    marker_color='blue'
    ))
    
    fig2.update_layout(title_text='Monthly Solar Energy Production (kWh)',
                      xaxis=dict(type='category'))
            
    
    col2.plotly_chart(fig2, use_container_width=True)
