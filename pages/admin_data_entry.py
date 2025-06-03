import streamlit as st
from utils.auth import get_user, get_user_role, get_supabase_client
from datetime import datetime

st.set_page_config(page_title="Upload for Patient")
st.title("🩺 Upload Patient Biomarker Data")


user = get_user()
if not user:
    st.warning("Please log in.")
    st.stop()

role = get_user_role(user.id)
if role != "full":
    st.error("Only admins can upload data for other users.")
    st.stop()


patient_id = st.text_input("Enter Patient's Phone Number")


biomarker = st.selectbox("Biomarker", ["Glucose", "WBC count", "Hemoglobin"])
value = st.number_input("Value", step=0.01)
date = st.date_input("Test Date", datetime.today())


if st.button("Submit Data"):
    if not patient_id.strip():
        st.warning("Please enter a valid phone number.")
        st.stop()

    supabase = get_supabase_client()
    try:
        supabase.table("biomarkers").insert({
            "user_id": patient_id.strip(),
            "biomarker": biomarker,
            "value": value,
            "date": str(date)
        }).execute()
        st.success(f"✅ Data saved for patient `{patient_id}`.")
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
