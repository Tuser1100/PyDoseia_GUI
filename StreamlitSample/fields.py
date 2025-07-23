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
            for idx, sheet_name in enumerate(sheet_names):
                with tabs[idx]:
                    try:
                        sheet_df = met_df.parse(sheet_name)
                        st.markdown(f"#### Preview of `{sheet_name}`")
                        st.dataframe(sheet_df.head())
                        st.markdown("**Detected Columns:**")
                        st.write(sheet_df.columns.tolist())
                    except Exception as e:
                        st.warning(f"Couldn't load sheet `{sheet_name}`: {e}")

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
        