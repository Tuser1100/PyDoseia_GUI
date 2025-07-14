class DoseiaGUI:
    #import streamlit as st
    #import pandas as pd
    #import streamlit_nested_layout
    
    def __init__(self):
        import pandas as pd
        self.df = pd.read_excel("doe_haz_cat_excel.xlsx")
        self.radionuclides = sorted(self.df["Radionuclide"].dropna().unique().tolist())
        self.selected = []
        self.coefficients = {}
        self.run_triggered = False

    def show_rad_info(self):
        import streamlit as st
        import streamlit_nested_layout

        with st.expander("☢️ RAD-INFO"):
            self.selected = st.multiselect("Choose one or more radionuclides:", options=self.radionuclides)
            if self.selected:
                st.markdown("### ℹ️ Radionuclide Info")
                for rn in self.selected:
                    row = self.df[self.df["Radionuclide"] == rn].iloc[0]
                    with st.expander(f"{rn} – click for details"):
                        st.write(f"**Limiting Pathway**: {row['Limiting_Pathway']}")
                        st.write(f"**HC2 Curies**: {row['HC2_Curies']}")
                        st.write(f"**HC2 Grams**: {row['HC2_Grams']}")
                        st.write(f"**HC3 Curies**: {row['HC3_Curies']}")
                        st.write(f"**HC3 Grams**: {row['HC3_Grams']}")

                        dose_choice = st.selectbox(
                            f"Select inhalation dose coefficient for {rn}:",
                            options=['Max', 'F', 'M', 'S'],
                            index=0,
                            key=f"coef_{rn}"
                        )
                        self.coefficients[rn] = dose_choice
            else:
                st.info("Please select radionuclides to see their info.")

    def show_dose_block(self):
        import streamlit as st
        import streamlit_nested_layout
        import pandas as pd
        import time

        if self.selected:
            compute_dose = st.selectbox("Compute dose?", ["No", "Yes"])
            section_title = "🧮 Dose Computation" if compute_dose == "Yes" else "🌫️ Dilution Factor Computation"

            with st.expander(section_title):
                col1, col2 = st.columns(2)
                with col1:
                    release_type = st.selectbox("Release type?", ["Short-term", "Long-term"])
                with col2:
                    plant_time = st.number_input("Plant running time (hours)", min_value=0.0)

                col3, col4 = st.columns(2)
                with col3:
                    downwind_str = st.text_input("Downwind distances (comma-separated, in meters)")
                    try:
                        downwind = [float(x.strip()) for x in downwind_str.split(",") if x.strip() != ""]
                    except ValueError:
                        st.error("Please enter only numeric values separated by commas.")
                        downwind = []
                    height = st.number_input("Release height (m)", min_value=0.0)
                with col4:
                    concentration = st.number_input("Ground-level time-integrated concentration (Z=0)?", min_value=0.0)
                    calm = st.selectbox("Calm correction?", ["No", "Yes"])

                has_meta = st.selectbox("Have meteorological data?", ["No", "Yes"])

                if has_meta == "Yes":
                    uploaded_file = st.file_uploader("Upload meteorological data (CSV/Excel)", type=["csv", "xlsx"])
                    with open("files/sample_met_data.xlsx", "rb") as file:
                        st.download_button(
                            label="📥 Download sample format",
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
                else:
                    st.markdown("Using default meteorological data.")

                with st.expander("✅ Review Your Inputs"):
                    st.write("### Selected Radionuclides and Coefficients")
                    for rn in self.selected:
                        coef = self.coefficients.get(rn, "Max")
                        st.write(f"{rn}: {coef}")
                    st.write(f"Release Type: {release_type}")
                    st.write(f"Plant Time: {plant_time} hrs")
                    st.write(f"Downwind Distances: {downwind}")
                    st.write(f"Release Height: {height} m")
                    st.write(f"Concentration (Z=0): {concentration}")
                    st.write(f"Calm Correction: {calm}")
                    st.write(f"Meteorological Data Provided: {has_meta}")

                if st.button("Run Simulation"):
                    with st.spinner("Running simulation and generating files..."):
                        time.sleep(2.5)  # placeholder for actual logic
                        self.run_triggered = True

                if self.run_triggered:
                    st.success("Simulation complete. Download your files below:")
                    st.download_button("📄 Download Input File", data="Sample Input File", file_name="input_file.txt")
                    st.download_button("🗂️ Download Log File", data="Sample Log Content", file_name="log_file.txt")
                    st.download_button("📊 Download Output File", data="Sample Output Content", file_name="output_file.txt")
        else:
            st.info("Dose computation options will appear after radionuclides are selected.")