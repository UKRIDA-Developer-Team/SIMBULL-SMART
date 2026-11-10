"""Method, data, model, evaluation, limitations and ethics."""
import pandas as pd
import streamlit as st

import ui
from spk import config, i18n

rf, meta = ui.load_active()
base, base_meta = ui.load_base()
L = ui.lang()
T = ui.T
TEAM = [("Steven Feryanta", "412025028"), ("Steven Iwan", "412024008"),
        ("Triemas Putra", "412024018"), ("Davidson Rafael", "412024030")]

ui.page_header(T("about_title"), ui.content("about_intro").replace("**", ""))
st.space("small")

ui.section(T("about_arch"))
with st.container(border=True, key="card_arch"):
    st.graphviz_chart("""
digraph {
  rankdir=LR; compound=true; bgcolor="transparent"; nodesep=0.35; ranksep=0.45;
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, color="#D9D5CC", penwidth=1,
        fontcolor="#1D2725", margin="0.18,0.08"];
  edge [color="#8A9491", arrowsize=0.6];
  subgraph cluster_off { label="%s"; style="rounded,dashed"; color="#D9D5CC"; fontname="Helvetica"; fontsize=10; fontcolor="#5D6A67";
    kag [label="Kaggle 1M\\n(%s)", fillcolor="#FBF4E8"]; gf [label="Google Form\\n(%s)", fillcolor="#FBF4E8"];
    tr [label="scripts/train.py\\n(kaggle | real | compare)", fillcolor="#FFFFFF"];
    kag -> tr; gf -> tr; }
  subgraph cluster_art { label="models/"; style="rounded,dashed"; color="#D9D5CC"; fontname="Helvetica"; fontsize=10; fontcolor="#5D6A67";
    m [label="RF .joblib\\n+ metadata.json", fillcolor="#E6F0ED"]; }
  subgraph cluster_app { label="Streamlit Cloud"; style="rounded,dashed"; color="#D9D5CC"; fontname="Helvetica"; fontsize=10; fontcolor="#5D6A67";
    ui [label="app_pages/\\n(%s)", fillcolor="#1E6B5C", fontcolor="#FFFFFF", color="#1E6B5C"];
    g [label="spk/gform.py\\n%s", fillcolor="#FFFFFF"];
    p [label="spk/model.py\\nRF predict", fillcolor="#FFFFFF"];
    s [label="spk/smart.py\\nSMART + %s", fillcolor="#FFFFFF"];
    e [label="spk/explain.py · xai.py\\nrecommend.py", fillcolor="#FFFFFF"];
    ui -> g -> p -> s -> e -> ui; }
  tr -> m; m -> p;
}
""" % (("Pelatihan offline", "usia %d-%d · latih/uji 80/20" % config.AGE_RANGE, "rahasia, tidak di-commit", "Beranda · Rekomendasi · Analisis\\nData Mining · Tentang", "jawaban → fitur", "sensitivitas")
       if L == "id" else
       ("Offline training", "age %d-%d · train/test 80/20" % config.AGE_RANGE, "confidential, not committed", "Home · Recommendation · Analysis\\nData Mining · About", "answers → features", "sensitivity")))

st.space("small")
with st.container(border=True, key="card_method"):
    st.markdown(ui.content("about_method"))

st.space("small")
c1, c2 = st.columns([1.25, 1], gap="medium")
with c1:
    ui.section(T("about_criteria"))
    st.table(pd.DataFrame({
        T("criterion"): [i18n.feature(c, L) for c in config.CRITERIA],
        T("type"): [T(config.CRITERIA_TYPE[c]) for c in config.CRITERIA],
        "A · " + i18n.alt("Sleep", L): [round(config.WEIGHTS_A["Sleep"][c], 3) for c in config.CRITERIA],
        "A · " + i18n.alt("Counseling", L): [round(config.WEIGHTS_A["Counseling"][c], 3) for c in config.CRITERIA],
    }).set_index(T("criterion")))
with c2:
    ui.section(T("about_alts"))
    for a in config.ALTERNATIVES:
        st.markdown(f":material/{ui.ALT_ICONS[a]}: **{i18n.alt(a, L)}** · {i18n.alt_desc(a, L)}")

st.space("small")
ui.section(T("about_model"))
hp = meta.get("hyperparameters", {})
m = meta["metrics"]
k = st.columns(4, gap="small")
k[0].metric("MAE", f"{m['mae']:.4f}", border=True)
k[1].metric("RMSE", f"{m['rmse']:.4f}", border=True)
k[2].metric("R²", f"{m['r2']:.4f}", border=True)
k[3].metric("n_estimators", meta.get("n_estimators_total", hp.get("n_estimators")), border=True)
st.caption(
    f"{ui.model_note()} · {'strategi' if L == 'id' else 'strategy'}: `{meta.get('strategy', 'kaggle base')}` · "
    f"max_depth={hp.get('max_depth')}, min_samples_leaf={hp.get('min_samples_leaf')}, "
    f"max_features={hp.get('max_features')}, max_samples={hp.get('max_samples')}, "
    f"random_state={hp.get('random_state')} · "
    f"{meta.get('metrics_note', 'Kaggle test set')} · "
    f"Kaggle base: MAE {base_meta['metrics']['mae']:.4f}, R² {base_meta['metrics']['r2']:.4f}")

st.space("small")
with st.container(border=True, key="card_limits"):
    st.markdown(ui.content("about_limits"))

st.space("small")
ui.section(T("about_team"))
team = st.columns(len(TEAM), gap="small")
for col, (name, nim) in zip(team, TEAM):
    initials = "".join(w[0] for w in name.split()[:2])
    with col.container(border=True, key=f"card_team_{nim}"):
        st.html(f"<div class='spk-person'><span class='spk-avatar'>{initials}</span>"
                f"<div><p class='spk-person-name'>{name}</p><p class='spk-person-id'>{nim}</p></div></div>")

ui.footer()
