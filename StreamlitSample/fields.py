import pandas as pd
import os, tempfile
import streamlit as st

class Fields:

    def __init__(self):
        pass

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

    def dose_type_selector(self, existing_inputs):
        import streamlit as st

        with st.expander("Select Dose Types", icon=":material/category:"):
            st.markdown("Click to select one or more applicable dose types:")

            #options = ["Inhalation Dose", "Plume Shine", "Ground Shine", "Submersion Dose", "Ingestion Dose"]
            col= st.columns(5)
            selected_types = []

            #toggle across one line
            with col[0]:
                inhalation = st.toggle("Inhahalation Dose", value=True, key="inhalation_dose")
                if inhalation: selected_types.append("Inhalation Dose")
            with col[1]:
                ground = st.toggle("Ground Shine", value=True, key="ground_shine")
                if ground: selected_types.append("Ground Shine")
            with col[2]:
                submersion = st.toggle("Submersion Dose", value=True, key="submersion_dose")
                if submersion: selected_types.append("Submersion Dose")
            with col[3]:
                ingestion = st.toggle("Ingestion Dose", value=True, key="ingestion_dose")
                if ingestion: selected_types.append("Ingestion Dose")
            with col[4]:
                plume = st.toggle("Plume Shine", value=True, key="plume_shine")
                if plume: selected_types.append("Plume Shine")

            existing_inputs["selected_dose_types"] = selected_types

            st.divider()

            if "Ground Shine" in selected_types:
                with st.popover("Ground Shine Inputs", icon=":material/info:"):
                    st.markdown("### 🪨 Ground Shine Configuration")
                    weather_corr = st.selectbox("Apply weathering correction?", ["Yes", "No"], key="weathering_corr")
                    exposure_period = st.number_input("Exposure period (years)", min_value=0.0, value=1.0, step=0.5, key="exposure_period")
                    existing_inputs["weathering_corr"] = (weather_corr == "Yes")
                    existing_inputs["exposure_period"] = exposure_period

            # TODO: Add popovers for the other types here when needed
            # For example: if "Plume Shine" in selected_types: ...

        return existing_inputs
