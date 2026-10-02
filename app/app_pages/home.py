"""Landing page: problem, who it is for, how it works, call to action."""
import streamlit as st

import ui
from spk import config

rf, meta = ui.load_active()
L = ui.lang()

st.title("🧭 " + ui.T("app_title"))
st.markdown(ui.content("home_intro"))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kriteria SMART" if L == "id" else "SMART criteria", len(config.CRITERIA))
c2.metric("Alternatif penanganan" if L == "id" else "Interventions", len(config.ALTERNATIVES))
c3.metric("MAE model" if L == "id" else "Model MAE", f"{meta['metrics']['mae']:.3f}")
c4.metric("R² model" if L == "id" else "Model R²", f"{meta['metrics']['r2']:.3f}")

st.subheader("Alur kerja" if L == "id" else "How it works")
st.graphviz_chart("""
digraph {
  rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#EEF3FB", color="#4C72B0", fontname="Helvetica"];
  q [label="%s"]; f [label="%s"]; rf [label="Random Forest\\n%s"]; s [label="SMART\\n%s"]; r [label="%s"];
  q -> f -> rf -> s -> r;
}
""" % (("Kuesioner siswa", "11 fitur model", "prediksi skor kecemasan", "prioritas + 5 alternatif", "Rekomendasi\\n+ alasan")
       if L == "id" else
       ("Student questionnaire", "11 model features", "predicts anxiety score", "priority + 5 alternatives", "Recommendation\\n+ reasons")))

st.markdown(ui.content("home_steps"))
st.page_link("app_pages/recommendation.py", label=("Mulai rekomendasi →" if L == "id" else "Start a recommendation →"),
             icon="🔮")
st.page_link("app_pages/analysis.py", label=("Lihat analisis data & model" if L == "id" else "See the data & model analysis"),
             icon="📊")
ui.footer()
