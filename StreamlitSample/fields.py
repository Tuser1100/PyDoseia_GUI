import pandas as pd
import os, tempfile
import streamlit as st

class Fields:

    def __init__(self):
        self.df2 = pd.read_csv("Annex_H_ICRP119_dcf_inhal_reactive_soluble_gases_public.csv")["Nuclide"].dropna().unique().tolist()

    def met_data(self, uploaded_file, existing_inputs):
        temp_dir = tempfile.gettempdir()
        saved_path = os.path.join(temp_dir, uploaded_file.name)
        with open(saved_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        #Store uploaded path
        existing_inputs["path_met_file"] = saved_path

        if uploaded_file.name.endswith(".csv"):
            met_df = pd.read_csv(uploaded_file)
            st.markdown("#### Detected Columns:")
            columns = met_df.columns.tolist()
            st.write(columns)

            col1, col2, col3 = st.columns(3)
            with col1:
                col_time = st.selectbox("Column for Time:", columns)
                col_stability = st.selectbox("Column for Stability:", columns)
            with col2:
                col_speed = st.selectbox("Column for Wind Speed:", columns)
                num_days = st.number_input("Number of days for which meteorological data is available (CSV):", min_value=1, step=1)
            with col3:
                col_direction = st.selectbox("Column for Wind Direction:", columns)

            existing_inputs["num_days"] = int(num_days)
            _=''' Using List instead
            existing_inputs["column_names"] = {
                "Time Column": col_time,
                "Wind Speed Column": col_speed,
                "Wind Direction Column": col_direction,
                "Stability Column": col_stability }
            '''
            existing_inputs["column_names"] = [col_time, col_speed, col_direction, col_stability]            

        else:
            met_df = pd.ExcelFile(saved_path)
            sheet_names = met_df.sheet_names

            tabs = st.tabs([f"📄 {name}" for name in sheet_names])
            col_headers = []
            for idx, sheet_name in enumerate(sheet_names):
                with tabs[idx]:
                    try:
                        sheet_df = met_df.parse(sheet_name)
                        st.markdown(f"#### Preview of `{sheet_name}`")
                        st.dataframe(sheet_df.head())
                        st.markdown("**Detected Columns:**")
                        st.write(sheet_df.columns.tolist())
                        col_headers.append(set(sheet_df.columns.tolist()))
                    except Exception as e:
                        st.warning(f"Couldn't load sheet `{sheet_name}`: {e}")


            # Check for inconsistent columns (names only, order ignored)
            if len(set(frozenset(cols) for cols in col_headers)) > 1:
                st.error("❌ Inconsistent column names across sheets. All sheets must have the same named columns.")
                return existing_inputs

            selected_sheets = st.multiselect("Select Excel sheets to use for meteorological data:", options=sheet_names)
            existing_inputs["excel_sheet_name"] = selected_sheets
            if selected_sheets:
                existing_inputs["column_names"] = {}
                num_days_list = []

                st.markdown("---")
                st.markdown("### Select columns for each selected sheet:")
                for sheet in selected_sheets:
                    st.markdown(f"#### 🔽 Sheet: `{sheet}`")
                    try:
                        sheet_df = met_df.parse(sheet)
                        columns = sheet_df.columns.tolist()

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            col_time = st.selectbox(f"{sheet} - Time Column", columns, key=f"{sheet}_time")
                            col_stability = st.selectbox(f"{sheet} - Stability Column", columns, key=f"{sheet}_stab")
                        with col2:
                            col_speed = st.selectbox(f"{sheet} - Wind Speed Column", columns, key=f"{sheet}_speed")
                            days = st.number_input(f"{sheet} - Number of Days", min_value=1, step=1, key=f"{sheet}_days")
                            num_days_list.append(int(days))
                        with col3:
                            col_direction = st.selectbox(f"{sheet} - Wind Direction Column", columns, key=f"{sheet}_dir")
    
                        _='''lIST INSTEAD
                        existing_inputs["column_names"][sheet] = {
                            "Time Column": col_time,
                            "Wind Speed Column": col_speed,
                            "Wind Direction Column": col_direction,
                            "Stability Column": col_stability
                            }
                        '''
                        existing_inputs["column_names"] = [col_time, col_speed, col_direction, col_stability]                                    

                    except Exception as e:
                        st.warning(f"Could not process sheet `{sheet}` for column selection: {e}")
                
                existing_inputs["num_days"] = num_days_list

        return existing_inputs

    #To avoid redunancy in met_data func
    def timing_calm_inputs (self, compute_dose, existing_inputs):
        col1, col2 = st.columns(2)
        with col1:
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
                    existing_inputs["start_operation_time"] = timing_values[0] if len(timing_values) > 0 else None
                    existing_inputs["end_operation_time"] = timing_values[1] if len(timing_values) > 1 else None                            
            except ValueError:
                st.error("Operation time must be numeric values between 0 and 24.")
                timing_values = []

        with col2:
            calm = st.selectbox("Calm correction?", ["No", "Yes"], key=f"calm_{'dose' if compute_dose else 'df'}")
            existing_inputs["calm_correction"] = calm
        
        return existing_inputs

    def dose_type_selector(self, existing_inputs, selected_rads):
        import streamlit as st

        with st.expander("Select Dose Types", icon=":material/category:"):
            st.markdown("Click to select one or more applicable dose types:")

            #options = ["Inhalation Dose", "Plume Shine", "Ground Shine", "Submersion Dose", "Ingestion Dose"]
            col= st.columns(5)
            selected_types = []

            #toggle across one line
            with col[0]:
                inhalation = st.toggle("Inhalation Dose", value=True, key="inhalation_dose")
                if inhalation: selected_types.append("Inhalation Dose")
            with col[1]:
                ground = st.toggle("Ground Shine", value=True, key="ground_shine")
                if ground: selected_types.append("Ground Shine")
            with col[2]:
                submersion = st.toggle("Submersion Dose", value=True, key="submersion_dose")
                if submersion: selected_types.append("Submersion Dose")
            with col[3]:
                plume = st.toggle("Plume Shine", value=True, key="plume_shine")
                if plume: selected_types.append("Plume Shine")
            with col[4]:
                ingestion = st.toggle("Ingestion Dose", value=True, key="ingestion_dose")
                if ingestion: selected_types.append("Ingestion Dose")

            existing_inputs["selected_dose_types"] = selected_types

            st.divider()

            # Age Group
            ag_msg = "Plume Shine dose runs irrespective of age group"
            age_str = st.text_input("Age Group List separated by commas(years)", value="1,5,15,70", help=ag_msg, key="age_group_input")
            try:
                age_list = [float(a.strip()) for a in age_str.split(",") if a.strip() != ""]
                if any(age < 1 for age in age_list):
                    st.error("All age group values must be **greater than or equal to 1**.")
                    existing_inputs["age_group"] = []
                if any(age >= 110 for age in age_list):
                    st.warning("Wow! Anyone aged 110+ must be radiantly timeless. Proceed with legendary caution.")
                existing_inputs["age_group"] = age_list
            except ValueError:
                st.error("Please enter valid numeric values for age groups.")
                existing_inputs["age_group"] = []

            # Shared Progeny Logic (for Ground Shine & Submersion Dose)
            if "Ground Shine" in selected_types or "Submersion Dose" in selected_types:
                col1, col2 = st.columns([1, 2])
                with col1:
                    consider_progeny = st.toggle("Consider progeny?", value=False, key="consider_progeny_dose")
                    existing_inputs["consider_progeny"] = consider_progeny
                with col2:
                    if consider_progeny:
                        ignore_half_life = st.number_input("Provide half-life(seconds):", min_value=0.0, value=1800.0, step=100.0, 
                                                            help="Provide half life value (in seconds) below which the effect of progenies will be ignored (Default: 1800).", 
                                                            key="ignore_half_life_dose")
                        existing_inputs["ignore_half_life"] = ignore_half_life

            col = st.columns([0.95,0.9,1,1,1])
            # Inhalation Dose Popover
            if "Inhalation Dose" in selected_types:
                with col[0]:
                    with st.popover("Inhalation Dose Inputs", icon="🫁"):
                        st.markdown("### Inhalation Dose Types per Selected Radionuclide")
                        if not selected_rads:
                            st.info("Please select radionuclides above to configure inhalation dose types.")
                        else:
                            default_coef = ["Max"] * len(selected_rads)
                            df_selected = pd.DataFrame({
                                "Radionuclide": selected_rads,
                                "Inhalation Type": default_coef
                            })
                            options = ["Max", "F", "M", "S", "V"] if any(rn in self.df2 for rn in selected_rads) else ["Max", "F", "M", "S"]
                            edited_df = st.data_editor(
                                df_selected,
                                column_config={
                                    "Inhalation Type": st.column_config.SelectboxColumn(
                                        "Inhalation Type",
                                        options=options,
                                        required=True
                                    )
                                },
                                hide_index=True,
                                key="inhale_type_editor"
                            )
                            type_rad = dict(zip(edited_df["Radionuclide"], edited_df["Inhalation Type"]))
                            existing_inputs["type_rad"] = type_rad

            #Ground Shine Dose Popover
            if "Ground Shine" in selected_types:
                with col[1]:
                    with st.popover("Ground Shine Inputs", icon="🪨"):
                        st.markdown("### Ground Shine Configuration")
                        weather_corr = st.selectbox("Apply weathering correction?", ["Yes", "No"], key="weathering_corr")
                        exposure_period = st.number_input("Exposure period (years)", min_value=0.0, value=30.0, step=0.5, key="exposure_period")
                        existing_inputs["weathering_corr"] = (weather_corr == "Yes")
                        existing_inputs["exposure_period"] = exposure_period

            #Submersion Dose Popover
            if "Submersion Dose" in selected_types:
                with col[2]:
                    with st.popover("Submersion Dose Inputs", icon=":material/flood:"):
                        st.markdown("### Submersion Dose Configuration")
                        st.info("No additional inputs for submersion dose at this time.")

            #Plume Shine Dose Popover
            if "Plume Shine" in selected_types:
                with col[3]:
                    with st.popover("Plume Shine Dose Inputs", icon="🌫️"):
                        st.markdown("### Plume Shine Configuration")
                        st.info("No additional inputs for Plume shine dose at this time.")
                        ps_parallel = st.toggle("Run using parallel processing", value=True, disabled=True, key="plume_parallel_toggle")
                        existing_inputs["run_plume_shine_dose"] = plume  # 'plume' is already True if toggle selected
                        existing_inputs["run_ps_dose_parallel"] = ps_parallel

            #Ingestion Dose Popover
            if "Ingestion Dose" in selected_types:
                with col[4]:
                    with st.popover("Ingestion Dose Inputs", icon=":material/vo2_max:"):
                        existing_inputs = self.ingestion_inputs(existing_inputs)

            # TODO: Add popovers for the other types here when needed
            # For example: if "Plume Shine" in selected_types: ...

        return existing_inputs

    def ingestion_inputs(self, existing_inputs):
        st.markdown("### Ingestion Dose Configuration")

        # 1. Soil Type
        soil = st.selectbox("Select soil type:", ["peatsoil", "othersoil"], key="ing_soil_type")
        existing_inputs["soiltype"] = soil

        # 2. Detect which age groups are present
        age_group = existing_inputs.get("age_group", [])
        ad = len([_ for _ in age_group if _ >= 18])
        adult_present = ad > 0
        infant_present = 1 in age_group
        only_infant_present = 1 in age_group and ad == 0

        # 3. Shared help messages for all inges inputs
        help_dict = {
            "alpha_wet_crops": "fraction of deposited activity intercepted by the edible portion of vegetation `[m2/kg]`",
            "alpha_dry_forage": "fraction of deposited activity intercepted by the edible portion of vegetation `[m2/kg]`",
            "t_e_food_crops": "Time of exposure of crops to fallout during growing season `[days]`",
            "t_e_forage_grass": "Time of exposure of crops to fallout during growing season `[days]`",
            "t_b": "duration of discharge of material in a day; for 30 years it is 11000 `[?]`",
            "t_h_wet_crops": "delay time i.e. time interval between harvest and consumption of wet crops `[days]`",
            "t_h_animal_pasture": "Time interval stored feed and consumption `[days]`",
            "t_h_animal_stored_feed": "time in animal feed `[days]`",
            "C_wi": "concentration of radionuclide in water `[Bq/m3]`",
            "f_p": "fraction of the year that animal consumes fresh pasture vegetation `[unitless]`",
            "alpha": "fraction of deposited activity intercepted by the edible portion of vegetation per unit mass `[m2/kg]`",
            "t_e": "Time of exposure of crops to fallout during growing season `[days]`",
            "t_m": "average time between collection and human consumption of milk `[days]`",
            "t_f": "average time between collection and human consumption of meat `[days]`",
            "q_m": "amount of feed (in dry matter) consumed per day `[kg/day]`",
            "q_w": "amount of water consumed by animal per day `[m3/d]`",
            "q_f": "amount of feed consumed by animal; goat and sheep; meat producing animal `[Kg/d]`",
            "q_w_meat": "water intake of meat producing animal `[m3/day]`",
            #"F_v [Bq/kg dry soil]": "concentration for uptake of radionuclide from soil by edible parts of crops. "
            #"c_pi": "concentration of radionuclide in stored feeds (Bq/Kg). "
            #"t_h_delay_time" : "90 (day). "
            "DID_veg": "Annual intake of vegetables `[kg/day]`",
            "DID_milk": "Annual intake of milk `[l/day]`",
            "DID_meat": "Annual intake of meat `[kg/day]`",
            "DID_fish": "Annual intake of fish `[kg/day]`",
            "DID_water_and_beverage": "Annual intake of water and beverages `[m³/day]`",
        }

        # 4. Default dictionaries
        default_inges = {
            'alpha_wet_crops': 0.3, 
            'alpha_dry_forage': 3.0, 
            't_e_food_crops': 60.0, 
            't_e_forage_grass': 30.0,
            't_b': 11000.0, 
            't_h_wet_crops': 14.0, 
            't_h_animal_pasture': 0.0, 
            't_h_animal_stored_feed': 90.0,
            'C_wi': 0.0, 
            'f_p': 0.7, 
            'alpha': 3.0, 
            't_e': 30.0, 
            't_m': 1.0, 
            't_f': 20.0, 
            'q_m': 16.0, 
            'q_w': 0.06,
            'q_f': 1.2, 
            'q_w_meat': 0.004
        }

        default_adult = {
            'DID_veg': 1.050,
            'DID_milk': 0.500,
            'DID_meat': 0.040,
            'DID_fish': 0.050,
            'DID_water_and_beverage': 0.002
        }

        default_infant = {
            'DID_veg': 0.215,
            'DID_milk': 0.400,
            'DID_meat': 0.0032876,
            'DID_fish': 0.004109,
            'DID_water_and_beverage': 0.0007123
        }

        # 5. Setup tabs
        tab_labels = ["Ingestion Parameters"]
        if adult_present:
            tab_labels.append("Adult Ingestion")
        if infant_present or only_infant_present:
            tab_labels.append("Infant Ingestion")

        tab_objs = st.tabs(tab_labels)
        
        with tab_objs[0]:
            st.subheader("Ingestion Parameters")
            inges_param = {}
            cols = st.columns(3)
            for i, (param, default) in enumerate(default_inges.items()):
                with cols[i % 3]:
                    inges_param[param] = st.number_input(label=param, value=default, format="%.10f", help=help_dict[param], key=f"inges_{param}")
            existing_inputs["inges_param_dict"] = inges_param

        tab_idx = 1

        if adult_present:
            with tab_objs[tab_idx]:
                st.subheader("Adult Ingestion Parameters")
                inges_adult = {}
                cols = st.columns(3)
                for i, (param, default) in enumerate(default_adult.items()):
                    with cols[i % 3]:
                        inges_adult[param] = st.number_input(label=param, value=default, format="%.10f", help=help_dict[param], key=f"adult_{param}")
                existing_inputs["inges_param_dict_adult"] = inges_adult
            tab_idx += 1

        if infant_present or only_infant_present:
            with tab_objs[tab_idx]:
                st.subheader("Infant Ingestion Parameters")
                inges_infant = {}
                cols = st.columns(3)
                for i, (param, default) in enumerate(default_infant.items()):
                    with cols[i % 3]:
                        inges_infant[param] = st.number_input(label=param, value=default, format="%.10f", help=help_dict[param], key=f"infant_{param}")
                existing_inputs["inges_param_dict_infant"] = inges_infant

        return existing_inputs
