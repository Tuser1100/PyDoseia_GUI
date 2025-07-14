import streamlit as st
import pandas as pd
from PIL import Image
import base64
from doseia_gui import DoseiaGUI

st.set_page_config(page_title="pyDOSEIA GUI", page_icon=":musical_note:", layout="wide")

logo_path = "img/pyD.jpg"

def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image(logo_path)

with st.container():
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{logo_base64}' width='120'/>
        <h1 style='margin-top: 0.2em;'>pyDOSEIA – Radiation Dose Simulation Interface</h1>
        <p style='font-size: 0.9em; color: gray;'>ver 1.0</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

app = DoseiaGUI()
col1, col2 = st.columns([1,3])
with col1:
    app.show_rad_info()
with col2:
    app.show_dose_block()
