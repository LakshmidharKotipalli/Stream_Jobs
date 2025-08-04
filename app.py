import streamlit as st
import pandas as pd
import json
import requests

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

# GitHub raw URL
GITHUB_JSON_URL = "https://github.com/LakshmidharKotipalli/Job_Scraper/blob/main/data/all_jobs.json"

@st.cache_data(show_spinner=False)
def load_jobs_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.DataFrame(json.loads(response.text))
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return pd.DataFrame()

df = load_jobs_from_github(GITHUB_JSON_URL)

# Check for required columns
required_columns = {"company", "job_title", "job_url"}
if not required_columns.issubset(df.columns):
    st.error(f"Missing required columns: {required_columns - set(df.columns)}")
    st.stop()

if df.empty:
    st.warning("No job listings available.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔎 Filter Jobs")
    selected_companies = st.multiselect("Select Company", sorted(df["company"].dropna().unique()))
    selected_titles = st.multiselect("Select Job Title", sorted(df["job_title"].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if selected_companies:
    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]
if selected_titles:
    filtered_df = filtered_df[filtered_df["job_title"].isin(selected_titles)]

# Metrics
st.markdown("## 📊 Overview")
col1, col2 = st.columns(2)
col1.metric("Total Jobs", len(filtered_df))
col2.metric("Companies", filtered_df["company"].nunique())

st.markdown("---")

# Job cards
st.markdown("## 💼 Job Listings")
for _, row in filtered_df.iterrows():
    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{row['job_title']}</div>
        <div class="job-meta"><strong>Company:</strong> {row['company']}</div>
        <a class="job-link" href="{row['job_url']}" target="_blank">🔗 View Job Posting</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("✨ Powered by Streamlit | Data from GitHub")
