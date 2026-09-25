"""Method, data, model, evaluation, limitations and ethics."""
import pandas as pd
import streamlit as st

import ui
from spk import config, i18n

rf, meta = ui.load_active()
base, base_meta = ui.load_base()
L = ui.lang()

st.title("ℹ️ " + ui.T("nav_about"))
st.markdown(ui.content("about_intro"))

st.subheader("Arsitektur sistem" if L == "id" else "System architecture")
st.graphviz_chart("""
digraph {
  rankdir=LR; compound=true; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];
  subgraph cluster_off { label="%s"; style=dashed; color="#999999";
    kag [label="Kaggle 1M → 20k", fillcolor="#FFF4E0"]; gf [label="Google Form\\n(%s)", fillcolor="#FFF4E0"];
    tr [label="scripts/train.py\\n(kaggle | real | compare)", fillcolor="#EEF3FB"];
    kag -> tr; gf -> tr; }
  subgraph cluster_art { label="models/"; style=dashed; color="#999999";
    m [label="RF .joblib\\n+ metadata.json", fillcolor="#E8F5E9"]; }
  subgraph cluster_app { label="Streamlit Cloud"; style=dashed; color="#999999";
    ui [label="app_pages/\\n(%s)", fillcolor="#EEF3FB"];
    g [label="spk/gform.py\\n%s", fillcolor="#FFFFFF"];
    p [label="spk/model.py\\nRF predict", fillcolor="#FFFFFF"];
    s [label="spk/smart.py\\nSMART + %s", fillcolor="#FFFFFF"];
    e [label="spk/explain.py\\nrecommend.py", fillcolor="#FFFFFF"];
    ui -> g -> p -> s -> e -> ui; }
  tr -> m; m -> p;
}
""" % (("Pelatihan offline", "rahasia, tidak di-commit", "Beranda · Rekomendasi · Analisis · Tentang", "jawaban → fitur", "sensitivitas")
       if L == "id" else
       ("Offline training", "confidential, not committed", "Home · Recommendation · Analysis · About", "answers → features", "sensitivity")))

st.markdown(ui.content("about_method"))

st.subheader("Kriteria & jenis" if L == "id" else "Criteria & types")
st.table(pd.DataFrame({
    ui.T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
    ui.T("type"): [ui.T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
    "Profil A · " + i18n.alt("Sleep", L): [config.WEIGHTS_A["Sleep"][c] for c in config.CRITERIA],
    "Profil A · " + i18n.alt("Counseling", L): [config.WEIGHTS_A["Counseling"][c] for c in config.CRITERIA],
}).set_index(ui.T("criterion")))

st.subheader("Alternatif" if L == "id" else "Alternatives")
for a in config.ALTERNATIVES:
    st.markdown(f"- **{i18n.alt(a, L)}** — {i18n.alt_desc(a, L)}")

st.subheader("Model")
hp = meta.get("hyperparameters", {})
st.markdown(
    f"- {'Sumber data' if L == 'id' else 'Data source'}: `{meta['data_source']}`"
    f" · {'strategi' if L == 'id' else 'strategy'}: `{meta.get('strategy', 'kaggle base')}`\n"
    f"- RandomForestRegressor: n_estimators={meta.get('n_estimators_total', hp.get('n_estimators'))}, "
    f"max_depth={hp.get('max_depth')}, min_samples_leaf={hp.get('min_samples_leaf')}, "
    f"max_features={hp.get('max_features')}, random_state={hp.get('random_state')}\n"
    f"- MAE {meta['metrics']['mae']:.4f} · RMSE {meta['metrics']['rmse']:.4f} · R² {meta['metrics']['r2']:.4f}"
    f" ({meta.get('metrics_note', 'Kaggle test set')})\n"
    f"- Kaggle base: MAE {base_meta['metrics']['mae']:.4f} · R² {base_meta['metrics']['r2']:.4f}"
)

st.markdown(ui.content("about_limits"))
st.subheader("Tim" if L == "id" else "Team")
st.markdown("Kelompok 1 — Steven Feryanta · Steven Iwan · Triemas Putra · Davidson Rafael")
ui.footer()
