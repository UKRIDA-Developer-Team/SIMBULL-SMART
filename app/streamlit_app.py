"""SPK SMART - student anxiety screening & intervention recommendation.

Run locally:  streamlit run streamlit_app.py   (from the app/ folder)
Pages live in app_pages/; shared helpers in ui.py; styles in assets/style.css; logic in spk/.
"""
import streamlit as st

import ui

st.set_page_config(page_title="SPK SMART", page_icon=str(ui.ASSETS_DIR / "mark.svg"), layout="wide")

if not ui.artifacts_ok():
    st.error(ui.T("missing_artifacts"))
    st.stop()

ui.setup()

pages = [
    st.Page("app_pages/home.py", title=ui.T("nav_home"), default=True, url_path="home"),
    st.Page("app_pages/recommendation.py", title=ui.T("nav_reco"), url_path="recommendation"),
    st.Page("app_pages/analysis.py", title=ui.T("nav_analysis"), url_path="analysis"),
    st.Page("app_pages/about.py", title=ui.T("nav_about"), url_path="about"),
]
st.navigation(pages, position="top").run()
