import streamlit as st
from utils.auth import get_user, get_user_role, get_supabase_client

st.set_page_config(page_title="Admin Panel | Biomarker Tracker")

st.title("🛠 Manage Users")


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
    users_data = supabase.table("user_roles").select("user_id", "email", "role", "lab_id").execute().data
    labs = supabase.table("labs").select("id", "name").execute().data
except Exception as e:
    st.error(f"Failed to load user data: {e}")
    st.stop()

lab_map = {lab["id"]: lab["name"] for lab in labs}
lab_names = list(lab_map.values())
lab_ids = list(lab_map.keys())

st.markdown("### 👥 All Users")

for u in users_data:
    user_id = u["user_id"]
    email = u.get("email", "Unknown")
    current_role = u["role"]
    lab_id = u.get("lab_id")

    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        st.markdown(f"**{email}**")

    with col2:
        new_role = st.selectbox("Role", ["full", "readonly"], index=["full", "readonly"].index(current_role), key=f"role_{user_id}")

    with col3:
        selected_lab = lab_map.get(lab_id, lab_names[0]) if lab_id else lab_names[0]
        new_lab_id = st.selectbox("Lab", lab_names, index=lab_names.index(selected_lab), key=f"lab_{user_id}")


    if st.button("✅ Update", key=f"update_{user_id}"):
        try:
            supabase.table("user_roles").update({
                "role": new_role,
                "lab_id": lab_ids[lab_names.index(new_lab_id)]
            }).eq("user_id", user_id).execute()
            st.success(f"Updated user `{email}` successfully.")
        except Exception as e:
            st.error(f"Error updating user `{email}`: {e}")

    st.markdown("---")
