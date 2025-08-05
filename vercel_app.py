import streamlit as st
import pandas as pd
import requests
import json
from pathlib import Path

# GitHub Raw Folder Path (Replace with your own)
GITHUB_USER = "LakshmidharKotipalli"
REPO_NAME = "Job_Scraper"
FOLDER_PATH = "data"
BRANCH = "main"

@st.cache_data
def fetch_json_files():
    # GitHub API URL to list contents of a folder
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{FOLDER_PATH}?ref={BRANCH}"
    res = requests.get(api_url)
    files = res.json()
    
    all_jobs = []

    for file in files:
        if file['name'].endswith('.json'):
            raw_url = file['download_url']
            try:
                data = requests.get(raw_url).json()
                if isinstance(data, list):
                    all_jobs.extend(data)
            except Exception as e:
                st.warning(f"⚠️ Could not load {file['name']}: {e}")

    return pd.DataFrame(all_jobs)

# Load Data
st.set_page_config(page_title="IT Job Tracker", layout="wide")
st.title("🚀 AI-Powered Job Listings")
st.caption("Scraped from multiple career sites via GitHub.")

df = fetch_json_files()

if df.empty:
    st.error("No job data available.")
else:
    # Filter UI
    with st.sidebar:
        st.header("🔍 Filter Jobs")
        companies = st.multiselect("Company", options=sorted(df['company site'].dropna().unique()))
        titles = st.text_input("Job Title Contains").lower()
        location = st.text_input("Location Contains").lower()

    filtered_df = df.copy()

    if companies:
        filtered_df = filtered_df[filtered_df['company site'].isin(companies)]

    if titles:
        filtered_df = filtered_df[filtered_df['job title'].str.lower().str.contains(titles)]

    if location:
        filtered_df = filtered_df[filtered_df['location'].str.lower().str.contains(location)]

    # Show Results
    st.markdown(f"### 🎯 {len(filtered_df)} Job(s) Found")
    
    for _, row in filtered_df.iterrows():
        st.markdown(f"""
        <div style="border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px;">
            <h4 style="margin-bottom:5px;">{row['job title']}</h4>
            <p style="margin:2px 0;"><strong>Company:</strong> {row['company site']}</p>
            <p style="margin:2px 0;"><strong>Location:</strong> {row.get('location', 'N/A')}</p>
            <a href="{row['job url']}" target="_blank">🔗 View Job</a>
        </div>
        """, unsafe_allow_html=True)
