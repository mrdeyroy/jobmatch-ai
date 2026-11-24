import streamlit as st
import httpx
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="JobMatch AI",
    page_icon="💼",
    layout="wide",
)

st.title("💼 JobMatch AI — Multi-Platform Career Engine")
st.markdown("Search across ATS platforms (Greenhouse, Ashby, Lever, RemoteOK) and match opportunities with AI.")

tabs = st.tabs(["🔍 Search Jobs", "📥 Ingest Jobs", "📄 ATS & Tailor", "⚙️ System Status"])

# Tab 1: Search Jobs
with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Job Title / Skills / Keywords", value="Python")
    with col2:
        location = st.text_input("Location / Remote", value="")

    col_opt1, col_opt2, col_opt3 = st.columns([1, 1, 2])
    with col_opt1:
        is_live = st.checkbox("Live Platform Search", value=True, help="Query Greenhouse, Ashby, Lever, RemoteOK directly in real-time")
    with col_opt2:
        limit = st.slider("Limit", min_value=5, max_value=30, value=10)

    if st.button("Search Jobs", type="primary"):
        with st.spinner("Searching across platforms..."):
            try:
                payload = {
                    "query": query,
                    "location": location if location else None,
                    "limit": limit,
                    "live": is_live,
                }
                # Internal container or host request
                url = f"{API_BASE_URL}/jobs/search"
                resp = httpx.post(url, json=payload, timeout=25.0)
                if resp.status_code == 200:
                    jobs = resp.json()
                    st.success(f"Found {len(jobs)} jobs ({'Live Search' if is_live else 'Database Index'})")

                    for j in jobs:
                        with st.container(border=True):
                            header_col1, header_col2 = st.columns([4, 1])
                            with header_col1:
                                st.subheader(j["title"])
                                st.caption(f"🏢 **{j['company']}** | 📍 {j['location']} | 🏷️ Source: `{j.get('source', 'unknown').upper()}`")
                            with header_col2:
                                if j.get("url"):
                                    st.link_button("Apply / View Job ↗", j["url"])

                            if j.get("requirements"):
                                st.write("**Tags / Departments:** " + " ".join([f"`{r}`" for r in j["requirements"]]))

                            with st.expander("View Full Job Description"):
                                st.write(j.get("description", "No description available."))
                else:
                    st.error(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to API ({API_BASE_URL}): {e}")

# Tab 2: Ingest Jobs
with tabs[1]:
    st.subheader("Ingest Real Postings into PostgreSQL")
    st.write("Scrapes public boards across Greenhouse, Ashby, Lever, and RemoteOK, strips HTML, verifies liveness, and commits them to pgvector/PostgreSQL.")

    ingest_query = st.text_input("Target Keyword/Role for Ingestion", value="Engineer")
    ingest_limit = st.number_input("Maximum Listings to Ingest", min_value=5, max_value=50, value=10)

    if st.button("Start Ingestion", type="secondary"):
        with st.spinner("Fetching and persisting jobs..."):
            try:
                payload = {"query": ingest_query, "limit": int(ingest_limit)}
                resp = httpx.post(f"{API_BASE_URL}/jobs/ingest", json=payload, timeout=40.0)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Ingestion complete! Ingested {data.get('ingested_count', 0)} new jobs.")
                else:
                    st.error(f"Ingestion failed: {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")

# Tab 3: ATS & Tailor
with tabs[2]:
    st.subheader("ATS Resume Scorer & CV Tailor")
    sample_cv = st.text_area("Paste Résumé / CV Text", height=150, placeholder="Experienced backend developer with Python, FastAPI, Docker...")
    sample_jd = st.text_area("Paste Job Description", height=150, placeholder="Looking for Senior Python Developer with FastAPI and PostgreSQL...")

    if st.button("Evaluate Match & ATS Score"):
        with st.spinner("Evaluating..."):
            try:
                resp = httpx.post(f"{API_BASE_URL}/cv/tailor", json={"cv_text": sample_cv, "jd_text": sample_jd}, timeout=15.0)
                if resp.status_code == 200:
                    st.json(resp.json())
                else:
                    st.error(resp.text)
            except Exception as e:
                st.error(f"API Error: {e}")

# Tab 4: System Status
with tabs[3]:
    st.subheader("Platform Health & Services")
    try:
        resp = httpx.get(f"{API_BASE_URL}/health", timeout=5.0)
        if resp.status_code == 200:
            st.success("API: Online and Healthy (FastAPI)")
        else:
            st.warning(f"API returned status {resp.status_code}")
    except Exception as e:
        st.error(f"API is unreachable: {e}")

    st.markdown("""
    - **API Base URL:** `http://localhost:8000`
    - **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Database:** PostgreSQL 16 + pgvector on `localhost:5432`
    """)
