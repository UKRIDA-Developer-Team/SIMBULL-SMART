"""SPK SMART - student anxiety screening & intervention recommendation.

Run locally:  streamlit run streamlit_app.py   (from the app/ folder)
Pages live in app_pages/; shared helpers in ui.py; logic in spk/.
"""
import streamlit as st

import ui

st.set_page_config(page_title="SPK SMART - Kecemasan", page_icon="🧭", layout="wide")

if not ui.artifacts_ok():
    st.error(ui.T("missing_artifacts"))
    st.stop()

ui.sidebar()

pages = [
    st.Page("app_pages/home.py", title=ui.T("nav_home"), icon="🏠", default=True, url_path="home"),
    st.Page("app_pages/recommendation.py", title=ui.T("nav_reco"), icon="🔮", url_path="recommendation"),
    st.Page("app_pages/analysis.py", title=ui.T("nav_analysis"), icon="📊", url_path="analysis"),
    st.Page("app_pages/about.py", title=ui.T("nav_about"), icon="ℹ️", url_path="about"),
]
st.navigation(pages, position="sidebar").run()
