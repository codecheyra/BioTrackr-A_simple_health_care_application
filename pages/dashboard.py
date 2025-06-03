import streamlit as st
from utils.auth import get_supabase_client, get_user
import pandas as pd
import altair as alt

# Reference clinical ranges
REFERENCE_RANGES = {
    "Glucose": (70, 120),
    "WBC count": (4000, 12000),
    "Hemoglobin": (12, 18)
}

st.set_page_config(page_title="Biomarker Dashboard")
st.title("📈 Biomarker Dashboard")

# --- Authentication ---
user = get_user()
if not user:
    st.warning("Please log in to view your dashboard.")
    st.stop()

# --- Fetch Data ---
supabase = get_supabase_client()
try:
    res = supabase.table("biomarkers").select("*").eq("user_id", user.id).execute()
    rows = res.data
except Exception as e:
    st.warning(f"⚠️ Failed to load biomarker data: {e}")
    st.stop()

if not rows:
    st.info("📭 No biomarker data found. Try entering or uploading data.")
    st.stop()

# --- Prepare DataFrame ---
df = pd.DataFrame(rows)
df["date"] = pd.to_datetime(df["date"])

# --- Select Biomarkers to View ---
all_biomarkers = ["Glucose", "WBC count", "Hemoglobin"]
selected = [b for b in all_biomarkers if st.checkbox(f"Show {b}", value=True)]

if not selected:
    st.warning("Please select at least one biomarker to display.")
    st.stop()

filtered = df[df["biomarker"].isin(selected)].copy()

# --- Flag Abnormal Values ---
def is_abnormal(row):
    low, high = REFERENCE_RANGES.get(row["biomarker"], (None, None))
    return row["value"] < low or row["value"] > high if low is not None and high is not None else False

filtered["abnormal"] = filtered.apply(is_abnormal, axis=1)

# --- Chart ---
line_chart = alt.Chart(filtered).mark_line(point=True).encode(
    x="date:T",
    y="value:Q",
    color="biomarker:N",
    tooltip=["biomarker", "date:T", "value", "unit", "abnormal"]
).properties(title="Biomarker Trends Over Time")

points = alt.Chart(filtered).mark_circle(size=100).encode(
    x="date:T",
    y="value:Q",
    color=alt.condition(
        alt.datum.abnormal,
        alt.value("red"),
        alt.Color("biomarker:N")
    ),
    tooltip=["biomarker", "date:T", "value", "abnormal"]
)

st.altair_chart(line_chart + points, use_container_width=True)

st.markdown("---")
st.subheader("📋 Detailed Data Tables")
for bio in selected:
    st.markdown(f"**{bio}**")
    table = (
        filtered[filtered["biomarker"] == bio]
        [["date", "value", "unit", "abnormal"]]
        .sort_values("date")
        .copy()
    )
    table["abnormal"] = table["abnormal"].map({False: "✅", True: "❌"})
    st.dataframe(table, use_container_width=True)

