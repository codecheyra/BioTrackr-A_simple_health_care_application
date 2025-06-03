import streamlit as st
from utils.auth import get_supabase_client, get_user
from datetime import datetime

st.set_page_config(page_title="Enter Data | Biomarker Tracker")
st.title("🧬 Enter Biomarker Data")


user = get_user()
if not user:
    st.warning("Please log in to continue.")
    st.stop()


biomarker_labels = {
    "Glucose (mg/dL)": "Glucose",
    "WBC count (cells/µL)": "WBC count",
    "Hemoglobin (g/dL)": "Hemoglobin"
}

biomarker_display = st.selectbox("Biomarker", list(biomarker_labels.keys()))
value = st.number_input("Value", step=0.01)
unit = biomarker_display.split("(")[-1].rstrip(")") if "(" in biomarker_display else ""
date = st.date_input("Test Date", datetime.today())

if st.button("➕ Submit"):
    if not value:
        st.warning("Please enter the value.")
        st.stop()

    supabase = get_supabase_client()
    entry = {
        "user_id": user.id,
        "biomarker": biomarker_labels[biomarker_display],
        "value": value,
        "unit": unit,
        "date": str(date)
    }

    try:
        supabase.table("biomarkers").insert(entry).execute()
        st.success("✅ Biomarker data saved successfully.")
    except Exception as e:
        st.error(f"❌ Failed to save data: {e}")
