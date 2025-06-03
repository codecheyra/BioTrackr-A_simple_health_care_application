import streamlit as st
from utils.auth import get_supabase_client, get_user, signup, login

st.set_page_config(page_title="Login | Biomarker Tracker")

st.title("🔐 Login / Sign Up")


user = get_user()
if user:
    st.success(f"✅ You are already logged in as `{user.email}`.")
    st.stop()


tab = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)

email = st.text_input("Email")
# phone_number = st.text_input("Phone Number")
password = st.text_input("Password", type="password")

if tab == "Login":
    if st.button("Login"):
        try:
            result = login(email, password)
            st.session_state["user"] = result.user
            st.success("🎉 Login successful!")
            # st.experimental_rerun()
        except Exception as e:
            st.error(f"❌ Login failed: {e}")

elif tab == "Sign Up":
    if st.button("Sign Up"):
        try:
            result = signup(email, password)
            st.success("✅ Signup successful! Please check your email to confirm.")
        except Exception as e:
            st.error(f"❌ Signup failed: {e}")

# st.session_state["user_id"] = phone_number
# st.write("Current user ID (phone number):", st.session_state.get("user_id", "Not set"))
