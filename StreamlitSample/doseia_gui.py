import streamlit as st
import pandas as pd
import yaml
import subprocess
import tempfile
from fields import Fields
from runner import handle_run

fields = Fields()

class DoseiaGUI:
    #import streamlit as st
    #import pandas as pd
    #import streamlit_nested_layout
    #import os
    
    def __init__(self):
        self.df = pd.read_excel("files/doe_haz_cat_excel.xlsx")
        self.radionuclides = sorted(self.df["Radionuclide"].dropna().unique().tolist())
        self.selected = []
        self.coefficients = {}
        self.run_triggered = False
        self.inputs = {}

    def show_rad_info(self):
        with st.expander("☢️ RAD-INFO"):
            self.selected = st.multiselect("Choose one or more radionuclides:", options=self.radionuclides)
            self.inputs["rads_list"] = [rn for rn in self.selected if rn != "H-3"] + (["H-3"] if "H-3" in self.selected else []) #Ensures H-3 is always last rad

            element_list = [rad.split("-")[0] for rad in self.inputs["rads_list"]]
            self.inputs["element_list"] = element_list

            if self.selected:
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

        self.inputs["plot_dilution_factor"] = False
        self.inputs["max_dilution_factor"] = None
        self.inputs["pickle_it"] = st.session_state.get("pickle_it", False) #Restore input from sidebar
        section_title = "🧮 Dose Computation" if compute_dose else "🌫️ Dilution Factor Computation"

        with st.expander(section_title):
            col1, col2 = st.columns(2)
            with col1:
                release_height = fields.validate_scientific_num_inputs(label="Release height (m)", default_val="80.0", key=f"release_height_{'dose' if compute_dose else 'df'}")
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
                measurement_height = fields.validate_scientific_num_inputs(label="Measurement height (m)", default_val="10.0", key=f"measurement_height_{'dose' if compute_dose else 'df'}")
                self.inputs["measurement_height"] = measurement_height
                if release_type == "Long-term":
                    concentration = st.selectbox("Ground-level time-integrated concentration (Z=0)?", ["Yes", "No"], key=f"concentration_{'dose' if compute_dose else 'df'}")
                    self.inputs["max_conc_plume_central_line_gl"] = concentration == "Yes" 
                    #Further logic added 
                    if concentration == "Yes":
                        self.inputs["Z"] = 0
                    else:
                        with st.popover("Enter Z value"):
                            z_value = st.number_input("Z value (m)", min_value=0.0, key="z_val_long")
                            self.inputs["Z"] = z_value
                            
                elif release_type == "Short-term":
                    centerline = st.selectbox("Perform centerline dose projection (Y=0, Z=0)?", ["Yes", "No"], key=f"centerline_{'dose' if compute_dose else 'df'}")
                    self.inputs["max_conc_plume_central_line_gl"] = centerline == "Yes"
                    #Furhter logic added 
                    if centerline == "Yes":
                        self.inputs["Y"] = 0
                        self.inputs["Z"] = 0
                    else:
                        with st.popover("Enter Y and Z values"):
                            y_val = st.number_input("Y value (m)", min_value=0.0, key="y_val_short")
                            z_val = st.number_input("Z value (m)", min_value=0.0, key="z_val_short")
                            self.inputs["Y"] = y_val
                            self.inputs["Z"] = z_val
            
            #Dilution Factor logic, Req modularization
            self.inputs["have_dilution_factor"] = False            
            if compute_dose:
                label = "Annual Discharge (Bq/year)" if release_type == "Long-term" else "Instantaneous Release (Bq)"
                with st.expander(f"{label} per Radionuclide", expanded=True):
                    discharge_vals = [0.0] * len(self.selected)
                    cols = st.columns(5)
                    for idx, rad in enumerate(self.selected):
                        with cols[idx % 5]: 
                            discharge_vals[idx] = fields.validate_scientific_num_inputs(label=f"{rad}", default_val="1.0", key=f"{rad}_discharge")
                    key = "annual_discharge_bq_rad_list" if release_type == "Long-term" else "instantaneous_release_bq_list"
                    self.inputs[key] = discharge_vals

                has_dilution = st.selectbox("Do you already have a dilution factor?", ["No", "Yes"]) #Key not required as this input is inovked only under comp dose
                self.inputs["have_dilution_factor"] = has_dilution == "Yes"

                if has_dilution == "Yes" and downwind:
                    st.markdown("### Enter Dilution Factor per Downwind Distance")
                    dilution_df = pd.DataFrame({
                        "Downwind Distance (m)": downwind,
                        "Dilution Factor": ["" for _ in downwind]
                    })
                    dilution_df = st.data_editor(dilution_df, hide_index=True)

                    # Validate dilution factor values
                    try:
                        dilution_df["Dilution Factor"] = dilution_df["Dilution Factor"].astype(float)
                        dilution_dict = dict(zip(dilution_df["Downwind Distance (m)"], dilution_df["Dilution Factor"]))
                        self.inputs["list_max_dilution_factor"] = dilution_dict
                    except ValueError:
                        st.error("All dilution factor values must be numeric.")
                        self.inputs["list_max_dilution_factor"] = None                        

            if (compute_dose and has_dilution == "No") or (not compute_dose): #METEROLOGICAL DATA HANDLING
                has_meta = st.selectbox("Have meteorological data?", ["No", "Yes"], key=f"has_meta_{'dose' if compute_dose else 'df'}")
                self.inputs["have_met_data"] = self.inputs["scaling_dilution_factor_based_on_met_data_speed_distribution"] = self.inputs["plot_dilution_factor"] = has_meta == "Yes"

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
                        self.inputs = fields.timing_calm_inputs(compute_dose, self.inputs)
                        #TEMPORARY FIX
                        self.inputs["sampling_time"] = 60
        
                    else:
                        st.warning("Please upload a meteorological file to proceed.")
                        self.inputs["path_met_file"] = None

                else:
                    st.markdown("Using default meteorological data.")
                    #self.inputs["path_met_file"] = "sample_met_data.xlsx"

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
                            st.markdown("Default mean wind speed = `1` will be used for all stability categories.")

        if compute_dose:
            self.inputs = fields.dose_type_selector(self.inputs, self.selected)                        

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
            self.inputs = handle_run(self.inputs)
