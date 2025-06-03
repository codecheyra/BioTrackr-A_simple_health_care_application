from supabase import create_client
import streamlit as st
from dotenv import load_dotenv
import os


load_dotenv()


SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))


assert SUPABASE_URL and SUPABASE_KEY and SUPABASE_KEY.startswith("ey"), "Supabase credentials are invalid or missing"

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)



def login(email, password):
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def signup(email, password):
    supabase = get_supabase_client()
    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })


    full_access_emails = ["kethavathajaykumar2002@gmail.com", "k.ajay.kumar2201@gmail.com"]
    role = "full" if email in full_access_emails else "readonly"

    user_id = response.user.id if response.user else None
    if user_id:
        try:
            supabase.table("user_roles").insert({
                "user_id": user_id,
                "role": role,
                "email": email,
                "lab_id": None
            }).execute()
        except Exception as e:
            print("Error assigning role:", e)

    return response

def get_user():
    return st.session_state.get("user", None)

def get_user_role(user_id):
    supabase = get_supabase_client()
    # st.write("login user id", user_id)
    try:
        result = supabase.table("user_roles").select("role").eq("user_id", user_id).single().execute()
        return result.data["role"] if result.data else None
    except Exception as e:
        print("Role lookup failed:", e)
        return None

def logout():
    if "user" in st.session_state:
        del st.session_state["user"]
    st.success("🔒 Logged out successfully.")
    # st.experimental_rerun()
