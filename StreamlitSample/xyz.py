import streamlit as st
import pandas as pd
import yaml
import subprocess
import tempfile
from fields import Fields

fields = Fields()

class DoseiaGUI:
    #import streamlit as st
    #import pandas as pd
    #import streamlit_nested_layout
    #import os
    
    def __init__(self):
        self.df = pd.read_excel("doe_haz_cat_excel.xlsx")
        self.df2 = pd.read_csv("Annex_H_ICRP119_dcf_inhal_reactive_soluble_gases_public.csv")["Nuclide"].dropna().unique().tolist()
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
                st.markdown("### Inhalation Dose Types per Radionuclide")

                default_coef = ["Max"] * len(self.selected)
                df_selected = pd.DataFrame({
                    "Radionuclide": self.selected,
                    "Inhalation Type": default_coef
                })

                edited_df = st.data_editor(
                    df_selected,
                    column_config={
                        "Inhalation Type": st.column_config.SelectboxColumn(
                            "Inhalation Type",
                            options=["Max", "F", "M", "S", "V"] if any(rn in self.df2 for rn in self.selected) else ["Max", "F", "M", "S"],
                            required=True
                        )
                    },
                    hide_index=True
                )

                self.coefficients = dict(zip(edited_df["Radionuclide"], edited_df["Inhalation Type"]))
                self.inputs["type_rad"] = self.coefficients

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

    def show_dose_block(self, compute_dose):
        import time
        import os

        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads_path, exist_ok=True)

        with st.container():
            col_pick1, col_pick2 = st.columns([10, 1])
            with col_pick1:
                pickle_it = st.toggle("Pickle it?", value=False, key=f"pkl_toggle_{'dose' if compute_dose else 'df'}")
                self.inputs["pickle_it"] = pickle_it
            with col_pick2:
                with st.popover("info", icon=":material/info:"):
                    st.markdown("### 🧊 Pickle it?")
                    st.write(
                        "If this is enabled, the program will serialize internal Python objects (like input data) "
                        "into a `.pkl` file for advanced reuse, debugging, or deeper analysis. "
                        "This is mainly for advanced users or developers."
                    )
                    st.info("Leave this **off** if you're not sure.")

        section_title = "🧮 Dose Computation" if compute_dose else "🌫️ Dilution Factor Computation"

        with st.expander(section_title):
            col1, col2 = st.columns(2)
            with col1:
                release_height = st.number_input("Release height (m)", min_value=0.0, key=f"release_height_{'dose' if compute_dose else 'df'}")
                self.inputs["release_height"] = release_height
            with col2:
                downwind_str = st.text_input("Downwind distances (comma-separated, in meters)", "100,200", key=f"downwind_dist_{'dose' if compute_dose else 'df'}")
                try:
                    downwind = [float(x.strip()) for x in downwind_str.split(",") if x.strip() != ""]
                except ValueError:
                    st.error("Please enter only numeric values separated by commas.")
                    downwind = []
                self.inputs["downwind_distances"] = downwind

            col3, col4 = st.columns(2)
            with col3:
                plant_boundary = st.selectbox("Select plant boundary (must be in downwind list):", downwind if downwind else [0], key=f"plant_boundary_{'dose' if compute_dose else 'df'}")
                release_type = st.selectbox("Release type:", ["Long-term", "Short-term"], key=f"release_type_{'dose' if compute_dose else 'df'}")
                self.inputs["plant_boundary"] = plant_boundary
                self.inputs["long_term_release"] = release_type == "Long-term"  #key name as per backend expectation
                self.inputs["single_plume"] = release_type == "Short-term"
            with col4:
                measurement_height = st.number_input("Measurement height (m)", min_value=0.0, key=f"measurement_height_{'dose' if compute_dose else 'df'}")
                self.inputs["measurement_height"] = measurement_height
                if release_type == "Long-term":
                    concentration = st.selectbox("Ground-level time-integrated concentration (Z=0)?", ["Yes", "No"], key=f"concentration_{'dose' if compute_dose else 'df'}")
                    self.inputs["max_conc_plume_central_line_gl"] = concentration == "Yes" 
                    #Further logic to be added from continuous plume func/ inp z when No
                    if concentration == "Yes":
                        self.inputs["Z"] = 0
                    else:
                        with st.popover("Enter Z value"):
                            z_value = st.number_input("Z value (m)", min_value=0.0, key="z_val_long")
                            self.inputs["Z"] = z_value
                            
                elif release_type == "Short-term":
                    centerline = st.selectbox("Perform centerline dose projection (Y=0, Z=0)?", ["Yes", "No"], key=f"centerline_{'dose' if compute_dose else 'df'}")
                    self.inputs["max_conc_plume_central_line_gl"] = centerline == "Yes"
                    #Furhter logic to be added from single plume func/ inp y,z when No
                    if centerline == "Yes":
                        self.inputs["Y"] = 0
                        self.inputs["Z"] = 0
                    else:
                        with st.popover("Enter Y and Z values"):
                            y_val = st.number_input("Y value (m)", min_value=0.0, key="y_val_short")
                            z_val = st.number_input("Z value (m)", min_value=0.0, key="z_val_short")
                            self.inputs["Y"] = y_val
                            self.inputs["Z"] = z_val
            
            #TEMPORARY FIX: change to a button
            self.inputs["have_dilution_factor"] = False
                        
            #Duplicacy & redundancy errors 
            _ = '''  
            has_dilution = st.selectbox("Do you already have a dilution factor?", ["No", "Yes"])
            self.inputs["dilution_factor"] = has_dilution

            if has_dilution == "No":
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
                self.inputs["Calm_correction"] = st.selectbox("Calm correction?", ["No", "Yes"])

            elif has_dilution == "Yes" and downwind:
                st.markdown("### Enter Dilution Factor per Downwind Distance")
                dilution_df = pd.DataFrame({
                    "Downwind Distance (m)": downwind,
                    "Dilution Factor": ["" for _ in downwind]
                })
                dilution_df = st.data_editor(dilution_df, hide_index=True)

                # Validate dilution factor values
                try:
                    dilution_df["Dilution Factor"] = dilution_df["Dilution Factor"].astype(float)
                except ValueError:
                    st.error("All dilution factor values must be numeric.")
            '''

            col5, col6 = st.columns(2)
            with col5:
                timing_str = st.text_input("Plant operation time (start,end in hours)", "0,24", key=f"operation_time_{'dose' if compute_dose else 'df'}")
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
                calm = st.selectbox("Calm correction?", ["No", "Yes"], key=f"calm_{'dose' if compute_dose else 'df'}")
                self.inputs["calm_correction"] = calm

            has_meta = st.selectbox("Have meteorological data?", ["No", "Yes"], key=f"has_meta_{'dose' if compute_dose else 'df'}")
            self.inputs["have_met_data"] = has_meta == "Yes"

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
                    self.inputs = fields.met_data(uploaded_file, self.inputs)
                    #TEMPORARY FIX
                    self.inputs["sampling_time"] = 60
    
                else:
                    st.warning("Please upload a meteorological file to proceed.")
                    self.inputs["path_met_data"] = None

            else:
                st.markdown("Using default meteorological data.")
                self.inputs["path_met_file"] = "sample_met_data.xlsx"

                scale_choice = st.selectbox("Would you like to scale dilution factor with your own mean wind speed?", ["No", "Yes"], key=f"scale_choice_{'dose' if compute_dose else 'df'}")
                self.inputs["like_to_scale_with_mean_speed"] = scale_choice == "Yes"
                if scale_choice == "Yes":
                    st.markdown("### 🌬️ Mean Wind Speed for Stability Categories")
                    stab_cols = st.columns(6)
                    mean_speed_inputs = []
                    for i, cat in enumerate(["A", "B", "C", "D", "E", "F"]):
                        with stab_cols[i]:
                            mean_speed = st.number_input(f"{cat}", min_value=0.0, value=1.0, step=0.1, key=f"stab_{cat}_{'dose' if compute_dose else 'df'}")
                            mean_speed_inputs.append(mean_speed)
                    self.inputs["ask_mean_speed_data"] = mean_speed_inputs
                else:
                    with st.popover("Note", icon=":material/info:"):
                        st.markdown("**Dilution factor won't be scaled** because meteorological data was not provided.")
                        st.write("Default mean wind speed = `1` will be used for all stability categories.")

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

            if st.button("Run", icon=":material/manufacturing:", key=f"run_btn_{'dose' if compute_dose else 'df'}"):
                with st.spinner("Running simulation and generating files..."):
                    time.sleep(2.5)

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
                        f"--output_file_name \"output_log.out\""
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
                log_path = os.path.join(downloads_path, "input_log_info.log")
                if os.path.exists(log_path):
                    with open(log_path, "r") as f:
                        st.download_button("🗂️ Download Log File", f.read(), file_name="pydoseia_log_file.txt")

                out_path = os.path.join(downloads_path, "input_log")
                if os.path.exists(out_path):
                    with open(out_path, "r") as f:
                        st.download_button("📊 Download Output File", f.read(), file_name="pydoseia_out_file.txt")


st.set_page_config(page_title="pyDOSEIA GUI", page_icon=":musical_note:", layout="wide")

app = DoseiaGUI()
tabs = st.tabs(["☢️ Dose Computation", "🌫️ Dilution Factor Only"])

with tabs[0]:
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
    st.warning("You have selected **Dilution Factor Computation Only**. Radionuclides are not needed.")
    compute_dose = False
    app.inputs["run_dose_computation"] = compute_dose
    app.show_dose_block(compute_dose)
