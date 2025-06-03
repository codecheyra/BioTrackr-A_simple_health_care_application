import streamlit as st
from utils.auth import get_user, get_user_role, get_supabase_client

st.set_page_config(page_title="Admin Dashboard | Biomarker Tracker")

st.title("📋 Admin Dashboard")

# --- Auth & Access Control ---
user = get_user()
if not user:
    st.warning("Please log in.")
    st.stop()

role = get_user_role(user.id)
if role != "full":
    st.error("Access denied: Full-access users only.")
    st.stop()

supabase = get_supabase_client()


try:
    labs = supabase.table("labs").select("*").execute().data
    users = supabase.table("user_roles").select("user_id", "email", "role", "lab_id").execute().data
    pdfs = supabase.table("pdf_files").select("id").execute().data
    biomarker_entries = supabase.table("biomarkers").select("id").execute().data
except Exception as e:
    st.error(f"Error loading admin data: {e}")
    st.stop()


st.subheader("📊 System Summary")
st.metric("Total Labs", len(labs))
st.metric("Registered Users", len(users))
st.metric("Uploaded PDFs", len(pdfs))
st.metric("Biomarker Entries", len(biomarker_entries))


st.subheader("🏥 Labs")
for lab in labs:
    st.markdown(f"""
    **{lab['name']}**
    - Domain: `{lab.get('domain', 'N/A')}`
    - Primary Color: `{lab.get('primary_color', '#000000')}`
    - Users Assigned: `{sum(1 for u in users if u.get('lab_id') == lab['id'])}`
    """)
    st.markdown("---")
