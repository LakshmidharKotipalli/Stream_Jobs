import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(page_title="Job Listings", layout="wide")

# Custom CSS
st.markdown("""
<style>
.job-card {
    background: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.job-title {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
}
.job-link {
    color: #1a73e8;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# GitHub raw URLs
BASE_URL = "https://raw.githubusercontent.com/LakshmidharKotipalli/Job_Scraper/main/data"
FILES = [f"{BASE_URL}/jobs_batch_{i}_of_10.json" for i in range(1, 11)]

@st.cache_data(show_spinner=True)
def load_all_json(urls):
    all_data = []
    for url in urls:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            records = json.loads(resp.text)
            if isinstance(records, list):
                all_data.extend(records)
        except Exception as e:
            st.warning(f"⚠️ Failed to load {url}: {e}")
    return pd.DataFrame(all_data)

df = load_all_json(FILES)

# Check required columns
required = {"title", "url", "company_site"}
if not required.issubset(df.columns):
    st.error(f"Missing required columns: {required - set(df.columns)}")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    selected_titles = st.multiselect("Filter by Job Title", sorted(df['title'].dropna().unique()))
    selected_sites = st.multiselect("Filter by Company Site", sorted(df['company_site'].dropna().unique()))

if selected_titles:
    df = df[df['title'].isin(selected_titles)]
if selected_sites:
    df = df[df['company_site'].isin(selected_sites)]

# 🔍 Search by words in title or company_site
search_query = st.text_input("🔎 Search jobs by keyword (title or company)")

if search_query:
    search_words = search_query.lower().split()
    mask = df['title'].str.lower().fillna('').apply(
        lambda x: any(word in x for word in search_words)
    ) | df['company_site'].str.lower().fillna('').apply(
        lambda x: any(word in x for word in search_words)
    )
    df = df[mask]

# Summary
st.markdown("## 📊 Summary")
col1, col2 = st.columns(2)
col1.metric("Total Jobs", len(df))
col2.metric("Unique Companies", df['company_site'].nunique())

# Job cards
st.markdown("## 💼 Job Listings")
if df.empty:
    st.info("No results found. Try changing filters or search terms.")
else:
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">{row['title']}</div>
            <p><strong>Company Site:</strong> <a href="{row['company_site']}" target="_blank">{row['company_site']}</a></p>
            <p><a class="job-link" href="{row['url']}" target="_blank">🔗 View Job Posting</a></p>
        </div>
        """, unsafe_allow_html=True)

st.caption("✨ Streamlit app | Powered by GitHub job data")
