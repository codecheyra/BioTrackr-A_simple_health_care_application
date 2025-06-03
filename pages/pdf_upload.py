import streamlit as st
from utils.auth import get_supabase_client, get_user
from utils.pdf_parser import extract_text_from_pdf, extract_biomarkers
import uuid

st.set_page_config(page_title="Upload Report | Biomarker Tracker")
st.title("📄 Upload Lab Report (PDF)")


user = get_user()
if not user:
    st.warning("Please log in to upload files.")
    st.stop()


uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file and st.button("Upload & Extract"):
    supabase = get_supabase_client()
    file_bytes = uploaded_file.read()
    file_id = str(uuid.uuid4())
    file_path = f"{user.id}/{file_id}.pdf"

    try:

        supabase.storage.from_("reports").upload(file_path, file_bytes)


        supabase.table("pdf_files").insert({
            "user_id": user.id,
            "file_path": file_path,
            "file_name": uploaded_file.name
        }).execute()


        text = extract_text_from_pdf(file_bytes)
        st.text_area("🧾 Extracted Raw Text", text, height=200)


        data = extract_biomarkers(text)

        if not data:
            st.error("❌ No biomarkers detected in the text.")
        else:
            st.subheader("🧬 Parsed Biomarkers")
            for entry in data:
                st.markdown(
                    f"**{entry['biomarker']}**: `{entry['value']} {entry['unit']}`  \n"
                    f"{entry['unit_check']}  \n"
                    f"📅 Date: `{entry['date']}`"
                )

            if st.button("💾 Save Extracted Data"):
                for entry in data:
                    entry["user_id"] = user.id
                    supabase.table("biomarkers").insert(entry).execute()
                st.success("✅ Biomarker data saved successfully!")

    except Exception as e:
        st.error(f"❌ Upload or extraction failed: {e}")
