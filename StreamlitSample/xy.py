import streamlit as st
import pandas as pd
import yaml
import subprocess

class DoseiaGUI:
    #import streamlit as st
    #import pandas as pd
    #import streamlit_nested_layout
    #import os
    
    def __init__(self):
        self.df = pd.read_excel("doe_haz_cat_excel.xlsx")
        self.radionuclides = sorted(self.df["Radionuclide"].dropna().unique().tolist())
        self.selected = []
        self.coefficients = {}
        self.run_triggered = False
        self.inputs = {}

    def show_rad_info(self):
        with st.expander("☢️ RAD-INFO"):
            self.selected = st.multiselect("Choose one or more radionuclides:", options=self.radionuclides)
            self.inputs["Selected Radionuclides"] = self.selected

            if self.selected:
                st.markdown("### Inhalation Dose Coefficients per Radionuclide")

                default_coef = ["Max"] * len(self.selected)
                df_selected = pd.DataFrame({
                    "Radionuclide": self.selected,
                    "Inhalation Coefficient": default_coef
                })

                edited_df = st.data_editor(
                    df_selected,
                    column_config={
                        "Inhalation Coefficient": st.column_config.SelectboxColumn(
                            "Inhalation Coefficient",
                            options=["Max", "F", "M", "S"],
                            required=True
                        )
                    },
                    hide_index=True
                )

                self.coefficients = dict(zip(edited_df["Radionuclide"], edited_df["Inhalation Coefficient"]))
                self.inputs["Radionuclide Coefficients"] = self.coefficients

                with st.popover("Radionuclide Info", icon=":material/info:"):
                    st.markdown("### Details for Selected Radionuclides")
                    for rn in self.selected:
                        row = self.df[self.df["Radionuclide"] == rn].iloc[0]
                        st.markdown(f"**{rn}**")
                        st.write(f"Limiting Pathway: {row['Limiting_Pathway']}")
                        st.write(f"HC2 Curies: {row['HC2_Curies']}")
                        st.write(f"HC2 Grams: {row['HC2_Grams']}")
                        st.write(f"HC3 Curies: {row['HC3_Curies']}")
                        st.write(f"HC3 Grams: {row['HC3_Grams']}")
                        st.markdown("---")
            else:
                st.info("Please select radionuclides to see their info.")

    def show_dose_block(self):
        import time
        import os

        if self.selected:
            compute_dose = st.selectbox("Compute dose?", ["No", "Yes"])
            self.inputs["Compute Dose"] = compute_dose
            section_title = "🧮 Dose Computation" if compute_dose == "Yes" else "🌫️ Dilution Factor Computation"

            with st.expander(section_title):
                col1, col2 = st.columns(2)
                with col1:
                    release_height = st.number_input("Release height (m)", min_value=0.0)
                    self.inputs["Release Height (m)"] = release_height
                with col2:
                    downwind_str = st.text_input("Downwind distances (comma-separated, in meters)", "100,200")
                    try:
                        downwind = [float(x.strip()) for x in downwind_str.split(",") if x.strip() != ""]
                    except ValueError:
                        st.error("Please enter only numeric values separated by commas.")
                        downwind = []
                    self.inputs["Downwind Distances (m)"] = downwind

                col3, col4 = st.columns(2)
                with col3:
                    plant_boundary = st.selectbox("Select plant boundary (must be in downwind list):", downwind if downwind else [0])
                    release_type = st.selectbox("Release type:", ["Long-term", "Short-term"])
                    self.inputs["Plant Boundary"] = plant_boundary
                    self.inputs["Release Type"] = release_type
                with col4:
                    measurement_height = st.number_input("Measurement height (m)", min_value=0.0)
                    self.inputs["Measurement Height (m)"] = measurement_height
                    if release_type == "Long-term":
                        concentration = st.number_input("Ground-level time-integrated concentration (Z=0)?", min_value=0.0)
                        self.inputs["Concentration (Z=0)"] = concentration
                    elif release_type == "Short-term":
                        centerline = st.selectbox("Perform centerline dose projection (Y=0, Z=0)?", ["Yes", "No"])
                        self.inputs["Centerline Projection"] = centerline
                
                #TEMPORARY FIX: change to a button
                self.inputs["have_dilution_factor"] = False

                col5, col6 = st.columns(2)
                with col5:
                    timing_str = st.text_input("Plant operation time (start,end in hours)", "0,24")
                    try:
                        timing_values = [float(x.strip()) for x in timing_str.split(",") if x.strip() != ""]
                        if len(timing_values) > 2 or any(t < 0 or t > 24 for t in timing_values):
                            st.error("Please provide up to 2 values between 0 and 24.")
                            timing_values = []
                        elif len(timing_values) == 2 and timing_values[0] > timing_values[1]:
                            st.error("Start time must be less than or equal to end time.")
                            timing_values = []
                        else:
                            self.inputs["start_operation_time"] = timing_values[0] if len(timing_values) > 0 else None
                            self.inputs["end_operation_time"] = timing_values[1] if len(timing_values) > 1 else None                            
                    except ValueError:
                        st.error("Operation time must be numeric values between 0 and 24.")
                        timing_values = []

                with col6:
                    calm = st.selectbox("Calm correction?", ["No", "Yes"])
                    self.inputs["Calm Correction"] = calm

                has_meta = st.selectbox("Have meteorological data?", ["No", "Yes"])
                self.inputs["have_met_data"] = has_meta

                if has_meta == "Yes":
                    uploaded_file = st.file_uploader("Upload meteorological data (CSV/Excel)", type=["csv", "xlsx"])
                    with open("files/sample_met_data.xlsx", "rb") as file:
                        st.download_button(
                            label="Download sample format",
                            icon=":material/download:",
                            data=file,
                            file_name="sample_met_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    if uploaded_file is not None:
                        if uploaded_file.name.endswith(".csv"):
                            met_df = pd.read_csv(uploaded_file)
                        else:
                            met_df = pd.read_excel(uploaded_file)

                        st.markdown("#### Detected Columns:")
                        columns = met_df.columns.tolist()
                        st.write(columns)

                        col_speed = st.selectbox("Column for Wind Speed:", columns)
                        col_direction = st.selectbox("Column for Wind Direction:", columns)
                        col_stability = st.selectbox("Column for Stability:", columns)

                        self.inputs["Meteorological Columns"] = {
                            "Wind Speed Column": col_speed,
                            "Wind Direction Column": col_direction,
                            "Stability Column": col_stability
                        }
                else:
                    st.markdown("Using default meteorological data.")

                with st.expander("Review Your Inputs", icon=":material/overview:"):
                    st.markdown("### 💡 Input Overview")
                    for key, value in self.inputs.items():
                        if value is None or value == []:
                            continue

                        label = key.replace("_", " ").capitalize()

                        if isinstance(value, dict):
                            st.markdown(f"**{label}:**")
                            for sub_key, sub_value in value.items():
                                st.markdown(f"- {sub_key}: `{sub_value}`")
                        elif isinstance(value, list):
                            st.markdown(f"**{label}:**")
                            for item in value:
                                st.markdown(f"- `{item}`")
                        else:
                            st.markdown(f"**{label}:** `{value}`")

                if st.button("Run Simulation", icon=":material/manufacturing:"):
                    with st.spinner("Running simulation and generating files..."):
                        time.sleep(2.5)
                        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                        os.makedirs(downloads_path, exist_ok=True)

                        # 1. Save input YAML
                        yaml_path = os.path.join(downloads_path, "input_log.yaml")
                        yaml_data = yaml.dump(self.inputs, sort_keys=False, allow_unicode=True, default_flow_style=False)
                        with open(yaml_path, "w") as f:
                            f.write(yaml_data)

                        # 2. Run backend subprocess
                        logdir_name = downloads_path
                        input_filename = "input_log"
                        command = (
                            f"python ../main.py "
                            f"--config_file \"{yaml_path}\" "
                            f"--logdir \"{downloads_path}\" "
                            f"--output_file_name \"input_log\""
                        )
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)

                        # 3. Handle result
                        if result.returncode != 0:
                            st.error("❌ Backend processing failed:")
                            st.code(result.stderr)
                            st.text(result.stdout)
                            st.session_state["run_triggered"] = False
                        else:
                            st.success("Simulation complete. Files saved to Downloads folder.", icon=":material/published_with_changes:")
                            st.session_state["run_triggered"] = True

                    st.download_button("📘 Download YAML Input Log", data=yaml_data, file_name="input_log.yaml", mime="text/yaml")

                # 4. Show downloads after success
                if st.session_state.get("run_triggered", False):
                    log_path = os.path.join(downloads_path, "pydoseia_log_file.txt")
                    if os.path.exists(log_path):
                        with open(log_path, "r") as f:
                            st.download_button("🗂️ Download Log File", f.read(), file_name="pydoseia_log_file.txt")

                    out_path = os.path.join(downloads_path, "pydoseia_out_file.txt")
                    if os.path.exists(out_path):
                        with open(out_path, "r") as f:
                            st.download_button("📊 Download Output File", f.read(), file_name="pydoseia_out_file.txt")

        else:
            st.info("Dose computation options will appear after radionuclides are selected.")


st.set_page_config(page_title="pyDOSEIA GUI", page_icon=":musical_note:", layout="wide")

app = DoseiaGUI()
col1, col2 = st.columns([1, 3])
with col1:
    app.show_rad_info()
with col2:
    app.show_dose_block()
