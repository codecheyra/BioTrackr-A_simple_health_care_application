import streamlit as st
from utils.auth import get_user, get_user_role, logout

st.set_page_config(page_title="Biomarker Tracker", layout="wide")


user = get_user()
if user:
    role = get_user_role(user.id)


    st.sidebar.markdown(f"👤 **Logged in as:** `{user.email}`")
    st.sidebar.markdown(f"🔐 **Access Role:** `{role or 'unknown'}`")


    if role == "admin":
        st.sidebar.markdown("---")
        st.sidebar.markdown("🛠️ **Admin Tools**")
        st.sidebar.page_link("pages/admin_panel.py", label="Manage Users")


    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/lab_onboarding.py", label="Lab Onboarding")
    st.sidebar.page_link("pages/data_entry.py", label="Data Entry")
    st.sidebar.page_link("pages/pdf_upload.py", label="Upload PDF")
    st.sidebar.page_link("pages/dashboard.py", label="Dashboard")
    st.sidebar.page_link("pages/doctor_chatbot.py",  "👩‍⚕️ AI Doctor")


    if st.sidebar.button("🚪 Logout"):
        logout()

else:

    st.sidebar.info("🔐 Please log in to access the platform.")
    st.stop()


st.title("Welcome to the Biomarker Tracker 👋")

st.markdown("""
This platform lets you:
- ✅ Manually enter or upload blood biomarker data (PDFs supported)
- 📈 Visualize trends and flag out-of-range values
- 🧪 Onboard labs with white-label support
- 🛠️ Manage roles and labs (Admins only)
""")
