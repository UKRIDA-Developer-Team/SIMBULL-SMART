"""SI SMART - student anxiety screening & intervention recommendation.

Run locally:  streamlit run streamlit_app.py   (from the app/ folder)

Two zones share one top bar (see ui.ZONES):
- app:    app_pages/ (home, one student, a class, help), for counselors
- report: app_pages/report/ (chapters 1-8), the technical report for examiners
Shared helpers live in ui.py, report.py and result_views.py; styles in assets/; logic in spk/.
"""
import streamlit as st

import ui

st.set_page_config(page_title="SI SMART", page_icon=str(ui.ASSETS_DIR / "mark.svg"), layout="wide")

if not ui.artifacts_ok():
    st.error(ui.T("missing_artifacts"))
    st.stop()

page = st.navigation(ui.build_pages(), position="hidden")
ui.setup(page)
page.run()
