import streamlit as st
from utils.auth import get_user, get_supabase_client

st.set_page_config(page_title="Lab Onboarding | Biomarker Tracker")
st.title("🏷️ Onboard a New Lab")


user = get_user()
if not user:
    st.warning("Please log in.")
    st.stop()


name = st.text_input("Lab Name")
logo_url = st.text_input("Logo URL (optional)")
primary_color = st.color_picker("Primary Brand Color")
domain = st.text_input("Custom Domain (optional)")

if st.button("🚀 Create Lab"):
    if not name.strip():
        st.warning("Lab name is required.")
        st.stop()

    lab_data = {
        "name": name,
        "logo_url": logo_url or None,
        "primary_color": primary_color,
        "domain": domain or None
    }

    supabase = get_supabase_client()
    try:
        supabase.table("labs").insert(lab_data).execute()
        st.success(f"✅ Lab '{name}' created successfully.")
    except Exception as e:
        st.error(f"❌ Failed to create lab: {e}")
