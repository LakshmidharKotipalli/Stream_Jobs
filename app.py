import streamlit as st
import pandas as pd
import json

# Set page config
st.set_page_config(
    page_title="Job Listings Dashboard",
    layout="wide",
    page_icon="💼"
)

# Inject custom CSS
def local_css():
    css = """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
    }
    .job-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .job-title {
        font-size: 20px;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .job-meta {
        font-size: 16px;
        margin-bottom: 4px;
        color: #555;
    }
    a.job-link {
        color: #1a73e8;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

local_css()

# Load data
try:
    with open("jobs.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("❌ jobs.json not found. Please run the scraper first.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(data)

if df.empty:
    st.warning("No job listings available.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filter Jobs")
    selected_companies = st.multiselect("Select Company", df["company"].unique())
    selected_locations = st.multiselect("Select Location", df["location"].unique())

# Apply filters
filtered_df = df.copy()
if selected_companies:
    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]
if selected_locations:
    filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]

# Metrics
st.markdown("## 📊 Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Jobs", len(filtered_df))
col2.metric("Companies", filtered_df["company"].nunique())
col3.metric("Locations", filtered_df["location"].nunique())

st.markdown("---")

# Job cards
st.markdown("## 💼 Job Listings")
for _, row in filtered_df.iterrows():
    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{row['job_title']}</div>
        <div class="job-meta"><strong>Company:</strong> {row['company']}</div>
        <div class="job-meta"><strong>Location:</strong> {row['location']}</div>
        <a class="job-link" href="{row['job_url']}" target="_blank">🔗 View Job Posting</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("✨ Powered by Streamlit | Built by Lakshmidhar K.")
