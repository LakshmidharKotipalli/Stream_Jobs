import streamlit as st
import pandas as pd
import json
import requests

# Streamlit page config
st.set_page_config(page_title="Job Listings Dashboard", layout="wide", page_icon="💼")

# Apply minimal CSS styling
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

# GitHub API URL for the 'data' folder in your repo
GITHUB_API_URL = "https://github.com/LakshmidharKotipalli/Job_Scraper/data"

@st.cache_data(show_spinner=True)
def load_all_json_from_github_folder(api_url):
    all_jobs = []
    error_files = []

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()
        json_files = [f for f in files if f["name"].endswith(".json")]

        for file in json_files:
            raw_url = file["download_url"]
            try:
                file_resp = requests.get(raw_url)
                file_resp.raise_for_status()
                jobs = json.loads(file_resp.text)

                if isinstance(jobs, list):
                    all_jobs.extend(jobs)
                else:
                    error_files.append(file["name"])
            except Exception as e:
                error_files.append(file["name"])

    except Exception as e:
        st.error(f"❌ Failed to connect to GitHub API: {e}")
        return pd.DataFrame()

    if error_files:
        st.warning(f"⚠️ Skipped {len(error_files)} malformed or empty files: {', '.join(error_files)}")

    return pd.DataFrame(all_jobs)

# Load job data
df = load_all_json_from_github_folder(GITHUB_API_URL)

# Check columns
required_columns = {"title", "url", "company_site"}
if not required_columns.issubset(df.columns):
    st.error(f"❌ Missing required columns: {required_columns - set(df.columns)}")
    st.stop()

if df.empty:
    st.warning("No job listings available.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Jobs")
    selected_sites = st.multiselect("Filter by Company Site", sorted(df["company_site"].dropna().unique()))
    selected_titles = st.multiselect("Filter by Job Title", sorted(df["title"].dropna().unique()))

# Apply filters
filtered_df = df.copy()
if selected_sites:
    filtered_df = filtered_df[filtered_df["company_site"].isin(selected_sites)]
if selected_titles:
    filtered_df = filtered_df[filtered_df["title"].isin(selected_titles)]

# Summary metrics
st.markdown("## 📊 Overview")
col1, col2 = st.columns(2)
col1.metric("Total Jobs", len(filtered_df))
col2.metric("Company Sites", filtered_df["company_site"].nunique())

st.markdown("---")

# Display job cards
st.markdown("## 💼 Job Listings")
for _, row in filtered_df.iterrows():
    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{row['title']}</div>
        <div class="job-meta"><strong>Company Site:</strong> <a href="{row['company_site']}" target="_blank">{row['company_site']}</a></div>
        <a class="job-link" href="{row['url']}" target="_blank">🔗 View Job Posting</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("✨ Powered by Streamlit | Live data from GitHub folder")
