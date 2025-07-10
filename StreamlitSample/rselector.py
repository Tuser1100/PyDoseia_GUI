def r_selector():
    import streamlit as st
    import pandas as pd
    import streamlit_nested_layout

    excel_path = "doe_haz_cat_excel.xlsx"
    df = pd.read_excel(excel_path)

    radionuclides = sorted(df["Radionuclide"].dropna().unique().tolist())

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("☢️ RAD-INFO"):
            selected = st.multiselect("Choose one or more radionuclides:", options=radionuclides)

            if selected:
                st.markdown("### ℹ️ Radionuclide Info")
                for rn in selected:
                    row = df[df["Radionuclide"] == rn].iloc[0]
                    with st.expander(f"{rn} – click for details"):
                        st.write(f"**Limiting Pathway**: {row['Limiting_Pathway']}")
                        st.write(f"**HC2 Curies**: {row['HC2_Curies']}")
                        st.write(f"**HC2 Grams**: {row['HC2_Grams']}")
                        st.write(f"**HC3 Curies**: {row['HC3_Curies']}")
                        st.write(f"**HC3 Grams**: {row['HC3_Grams']}")
            else:
                st.info("Please select radionuclides to see their info.")

    with col2:
        with st.expander("🧮 Dose Computation"):
            if selected:
                compute_dose = st.selectbox("Compute dose?", ["No", "Yes"])

                if compute_dose == "No":
                    dilution = st.selectbox("Compute dilution factor?", ["No", "Yes"])
                    if dilution == "Yes":
                        release_type = st.selectbox("Release type?", ["Short-term", "Long-term"])

                        plant_time = st.number_input("Plant running time (hours)", min_value=0)
                        has_meta = st.selectbox("Have meteorological data?", ["No", "Yes"])

                        if has_meta == "Yes":
                            uploaded_file = st.file_uploader("Upload meteorological data (CSV/Excel)", type=["csv", "xlsx"])
                            st.markdown("[📥 Download sample format](sample_met_data.xlsx)")

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
                            downwind = st.number_input("Downwind distance (m) including plant boundary", min_value=0.0)
                            height = st.number_input("Release height (m)", min_value=0.0)
                            concentration = st.number_input("Ground-level time-integrated concentration (Z=0)?", min_value=0.0)
                            calm = st.selectbox("Calm correction?", ["No", "Yes"])
                else:
                    st.info("Dose computation logic will be added here.")
            else:
                st.info("Dose computation options will appear after radionuclides are selected.")
