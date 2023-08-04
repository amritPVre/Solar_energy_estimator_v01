# -*- coding: utf-8 -*-
"""
Created on Mon May 22 01:47:14 2023

@author: amrit
"""

import streamlit as st

st.set_page_config(page_title="Disclaimer", page_icon="🧑🏻‍💻")

def about_me():
    st.write("# Welcome to My App Collections! 👋")
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
