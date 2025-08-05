import streamlit as st
import pandas as pd
from PIL import Image
import base64
from doseia_gui import DoseiaGUI

app = DoseiaGUI()
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
        <h1 style='margin-top: 0.2em;'>pyDOSEIA </h1>
        <p style='font-size: 0.9em; color: gray;'>ver 1.0</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

with st.sidebar:
    st.header("📂 File Settings")
    st.text_input("Directory name", value="PyDoseia_Run", key="custom_dir")
    st.text_input("Input file name", value="pydoseia_inp", key="inp_file_name")
    st.text_input("Output file name", value="pydoseia_out", key="out_file_name")
    col_pick1, col_pick2 = st.columns(2)
    with col_pick1:
        pickle_it = st.toggle("Pickle it?", value=False)
        app.inputs["pickle_it"] = pickle_it
    with col_pick2:
        with st.popover("info", icon=":material/info:"):
            st.markdown("### 🧊 Pickle it?")
            st.write(
                "If this is enabled, the program will serialize internal Python objects (like input data) "
                "into a `.pkl` file for advanced reuse, debugging, or deeper analysis. "
                "This is mainly for advanced users or developers."
            )
            st.info("Leave this **off** if you're not sure.")

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "dose"

tabs = st.tabs(["☢️ Dose Computation", "🌫️ Dilution Factor Only"])

with tabs[0]:
    if st.session_state["active_tab"] != "dose":
        app.inputs.clear()
        st.session_state["active_tab"] = "dose"
    st.warning("You have selected **Dose Computation**. Radionuclide selection is required.")
    col1, col2 = st.columns([1, 3])
    with col1:
        app.show_rad_info()
    with col2:
        if app.selected:
            compute_dose = True
            app.inputs["run_dose_computation"] = compute_dose
            app.show_dose_block(compute_dose)
        else:
            st.info("Dose computation options will appear after radionuclides are selected.")

with tabs[1]:
    if st.session_state["active_tab"] != "df":
        app.inputs.clear()
        st.session_state["active_tab"] = "df"
    st.warning("You have selected **Dilution Factor Computation Only**. Radionuclides are not needed.")
    compute_dose = False
    app.inputs["run_dose_computation"] = compute_dose
    app.show_dose_block(compute_dose)

st.divider() 
st.markdown(
    """
    <div style="text-align: center; padding: 1.2em 0 0.8em 0; font-size: 0.9em; color: #444;">
        <p style="margin-bottom: 0.3em;">
            <strong>© Dr. Biswajit Sadhu · Kalpak Gupte</strong> · All rights reserved
        </p>
        <p style="margin-bottom: 0.3em;">
            Licensed under the 
            <a href="https://github.com/BiswajitSadhu/pyDOSEIA/blob/main/LICENSE" target="_blank" style="color: #1f77b4; text-decoration: none;">
                MIT License
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
