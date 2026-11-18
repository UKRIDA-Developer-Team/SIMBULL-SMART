"""Result pieces shared by the app zone (one student, a class) and report chapter 3."""
import html

import pandas as pd
import streamlit as st

import ui
from spk import config, explain, i18n, plots, recommend, xai


T = ui.T


def _help(text: str) -> str:
    """A small (?) mark; hovering or focusing it shows the text."""
    return (f"<span class='spk-help' tabindex='0' title='{html.escape(text, quote=True)}' "
            f"aria-label='{html.escape(text, quote=True)}'>?</span>")


def hero_html(a) -> str:
    L = ui.lang()
    best = a.best
    anx_band, prio_band = ui.band(a.rf_percentile), ui.band(a.priority_percentile)
    group = html.escape(ui.reference_group())
    return f"""
<div class="spk-hero">
  <div class="spk-hero-main">
    <span class="spk-icon spk-icon-tile">{ui.ALT_ICONS[best]}</span>
    <p class="spk-hero-label">{T('res_best')}</p>
    <p class="spk-hero-alt">{html.escape(i18n.alt(best, L))}</p>
    <p class="spk-hero-desc">{html.escape(i18n.alt_desc(best, L))}</p>
    <p class="spk-hero-fine">{T('res_fit', s=float(a.ranking.iloc[0]))}</p>
  </div>
  <div class="spk-hero-stat">
    <p class="spk-hero-label">{T('res_pred')}</p>
    <p class="spk-hero-value">{a.rf_score:.2f}<span> / 10</span></p>
    <span class="spk-chip-row"><span class="spk-chip is-{anx_band}">{T(f'band_{anx_band}')}</span>{_help(ui.band_help('anx'))}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-{anx_band}" style="width:{min(100, a.rf_score * 10):.1f}%"></div></div>
    <p class="spk-hero-fine">{T('res_pred_note', p=a.rf_percentile, group=group)}</p>
  </div>
  <div class="spk-hero-stat">
    <p class="spk-hero-label">{T('res_priority')}</p>
    <p class="spk-hero-value">{a.priority:.3f}<span> / 1</span></p>
    <span class="spk-chip-row"><span class="spk-chip is-{prio_band}">{T(f'prio_{prio_band}')}</span>{_help(ui.band_help('prio'))}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-{prio_band}" style="width:{min(100, a.priority * 100):.1f}%"></div></div>
    <p class="spk-hero-fine">{T('res_priority_note', p=a.priority_percentile, group=group)}</p>
  </div>
</div>"""


# ---------------------------------------------------------------- explainable AI
def _num(feature: str, value) -> str:
    return f"{float(value):.0f}" if feature in ("age", "academic_performance") else f"{float(value):.1f}"


def chain_html(a, expl) -> str:
    """Stage 1 (RF) -> stage 2 (SMART) -> result, as three linked boxes."""
    L = ui.lang()
    steps = [
        (T("xai_chain_rf"), T("xai_chain_rf_d", pred=expl.prediction)),
        (T("xai_chain_smart"), T("xai_chain_smart_d")),
        (T("xai_chain_out"), T("xai_chain_out_d", alt=i18n.alt(a.best, L), score=float(a.ranking.iloc[0]))),
    ]
    boxes = [f"<div class='spk-chain-step'><p class='spk-chain-label'>{html.escape(t)}</p>"
             f"<p class='spk-chain-value'>{html.escape(d)}</p></div>" for t, d in steps]
    arrow = "<span class='spk-icon spk-chain-arrow'>arrow_forward</span>"
    return f"<div class='spk-chain'>{arrow.join(boxes)}</div>"


def what_if_view(features: dict, key: str):
    L = ui.lang()
    rf, meta = ui.load_active()
    st.caption(T("xai_whatif_lead", n=f"{len(ui.load_reference()):,}"))
    cf = xai.counterfactuals(rf, meta, features, ui.weights(), ui.xai_targets())
    if len(cf) == 1:
        st.success(T("xai_whatif_none"), icon=":material/check_circle:")
    else:
        rows = []
        for label, r in cf.iterrows():
            if label == "current":
                name = T("xai_current")
            elif label == "all":
                name = T("xai_all")
            else:
                name = f"{i18n.feature(label, L)}: {_num(label, r['from'])} → {_num(label, r['to'])}"
            first = label == "current"
            rows.append({
                T("xai_scenario"): name,
                T("xai_pred_col"): f"{r['prediction']:.2f}" + ("" if first else f" ({r['delta_prediction']:+.2f})"),
                T("xai_prio_col"): f"{r['priority']:.3f}" + ("" if first else f" ({r['delta_priority']:+.3f})"),
                T("xai_best_col"): i18n.alt(r["best"], L) + (f" · {T('xai_changed')}" if r["best_changed"] else ""),
            })
        table = pd.DataFrame(rows).set_index(T("xai_scenario"))
        changed = cf["best_changed"].to_numpy()
        st.table(table.style.apply(lambda frame: pd.DataFrame(
            [["background-color: #FBEAD2" if c else ""] * frame.shape[1] for c in changed],
            index=frame.index, columns=frame.columns), axis=None))
    st.caption(T("xai_whatif_note"))

    st.markdown(f"**{T('xai_try')}**")
    what_if_try(features, key)


# Factors the what-if tool can move: the actionable ones, plus the report grade.
WHAT_IF_FACTORS = list(xai.ACTIONABLE) + ["academic_performance"]


def what_if_try(features: dict, key: str, compact: bool = False):
    """Change one or more factors together and see the prediction, priority and recommendation.

    Starts with the factor that raises this student's prediction most. compact=True (app zone) shows
    the outcome as three short lines instead of metric tiles."""
    L = ui.lang()
    rf, meta = ui.load_active()
    effects = ui.shap_explanation(features).values.reindex(WHAT_IF_FACTORS)
    first = effects.idxmax() if effects.max() > 0 else WHAT_IF_FACTORS[0]
    picked = st.multiselect(T("xai_try_features"), WHAT_IF_FACTORS, default=[first], key=f"wi_feats_{key}_{L}",
                            format_func=lambda f: i18n.feature(f, L), placeholder=T("xai_try_pick"))
    changes = {}
    cols = st.columns(1 if compact else 2, gap="medium")
    for n, feat in enumerate(picked):
        lo, hi, _ = config.INPUT_RANGES[feat]
        step = 1.0 if feat == "academic_performance" else 0.1
        current = round(min(max(float(features[feat]), float(lo)), float(hi)), 1)
        value = cols[n % len(cols)].slider(i18n.feature(feat, L), float(lo), float(hi), current, step,
                                           key=f"wi_val_{key}_{feat}", help=T("xai_try_now", v=_num(feat, current)))
        if value != current:
            changes[feat] = value
    r = xai.what_if(rf, meta, features, ui.weights(), [("try", changes)]).loc["try"]
    moved = bool(changes)
    if compact:
        if not moved:
            st.caption(T("factor_try_hint"))
            return
        best = i18n.alt(r["best"], L) + (f" ({T('xai_changed')})" if r["best_changed"] else "")
        st.html(
            "<div class='spk-whatif'>"
            f"<p><span>{T('xai_pred_col')}</span><strong>{r['prediction']:.2f}</strong> <em>{r['delta_prediction']:+.2f}</em></p>"
            f"<p><span>{T('xai_prio_col')}</span><strong>{r['priority']:.3f}</strong> <em>{r['delta_priority']:+.3f}</em></p>"
            f"<p><span>{T('xai_best_col')}</span><strong>{html.escape(best)}</strong></p></div>")
        return
    m = st.columns(3, gap="small")
    m[0].metric(T("xai_pred_col"), f"{r['prediction']:.2f}", f"{r['delta_prediction']:+.2f}" if moved else None,
                delta_color="inverse", border=True)
    m[1].metric(T("xai_prio_col"), f"{r['priority']:.3f}", f"{r['delta_priority']:+.3f}" if moved else None,
                delta_color="inverse", border=True)
    m[2].metric(T("xai_best_col"), i18n.alt(r["best"], L), T("xai_changed") if r["best_changed"] else None,
                delta_color="off", border=True)


def factors_html(expl) -> str:
    """The factors that move this student's prediction most, as a short list (app zone)."""
    L = ui.lang()
    rows = []
    for direction, effects in (("up", expl.raising(3)), ("down", expl.lowering(2))):
        for f, v in effects.items():
            rows.append(
                f"<div class='spk-factor is-{direction}'><span class='spk-factor-name'>{html.escape(i18n.feature(f, L))}</span>"
                f"<span class='spk-factor-value'>{html.escape(explain.value_text(f, expl.features[f]))}</span>"
                f"<span class='spk-factor-effect'>{v:+.2f}</span></div>")
    if not rows:
        return f"<p class='spk-factor-none'>{html.escape(T('xai_flat'))}</p>"
    return f"<div class='spk-factors'>{''.join(rows)}</div>"


def factor_card(features: dict, key: str):
    """App-zone xAI: the main factors behind the prediction, and a what-if slider."""
    expl = ui.shap_explanation(features)
    c1, c2 = st.columns([1.15, 1], gap="medium")
    with c1.container(border=True, key=f"card_factors_{key}", height="stretch"):
        st.markdown(f"**{T('factor_title')}**")
        st.caption(T("factor_lead", base=expl.base_value, pred=expl.prediction, n=len(ui.xai_background())))
        st.html(factors_html(expl))
    with c2.container(border=True, key=f"card_whatif_{key}", height="stretch"):
        st.markdown(f"**{T('xai_tab_whatif')}**")
        st.caption(T("factor_try_lead"))
        what_if_try(features, key, compact=True)


def xai_panel(a, features: dict, key: str):
    """The explainable-AI card: RF prediction (Shapley), RF -> SMART chain, and what-if scenarios."""
    L = ui.lang()
    expl = ui.shap_explanation(features)
    link = xai.smart_link(a)
    st.caption(T("xai_lead"))
    with st.container(border=True, key=f"card_xai_{key}"):
        t1, t2, t3 = st.tabs([T("xai_tab_pred"), T("xai_tab_chain"), T("xai_tab_whatif")])
        with t1:
            st.markdown("\n".join(f"- {line}" for line in explain.shap_narrative(expl, None, L)))
            ui.show(plots.shap_waterfall(expl, L))
            st.caption(T("xai_method", n=len(ui.xai_background())))
        with t2:
            st.html(chain_html(a, expl))
            st.markdown(T("xai_link", c=link["contribution"], alt=i18n.alt(link["alternative"], L),
                          score=link["score"], share=link["share"]))
            ui.show(plots.contribution_bars(a.contributions, L))
            st.caption(T("xai_chain_help"))
        with t3:
            what_if_view(features, key)


def compare_models(features: dict, current):
    """Both model iterations side by side for one student: prediction, priority, recommendation."""
    L = ui.lang()
    models = ui.available_models()
    if len(models) < 2:
        return
    results = {}
    for kind in models:
        if kind == ui.model_key():
            results[kind] = current
        else:
            rf_k, meta_k = ui.load_model(kind)
            results[kind] = recommend.assess(rf_k, meta_k, features, ui.weights(), ui.reference_quantiles(kind))
    st.caption(T("cmp_lead"))
    rows = []
    for kind in ("real", "kaggle"):
        r = results[kind]
        name = T(f"model_short_{kind}") + (f" ({T('cmp_in_use')})" if kind == ui.model_key() else "")
        rows.append({T("cmp_model"): name, T("cmp_pred"): f"{r.rf_score:.2f} / 10", T("cmp_pct"): f"{r.rf_percentile:.0f}",
                     T("cmp_prio"): f"{r.priority:.3f}", T("cmp_best"): i18n.alt(r.best, L),
                     T("cmp_safety"): "✔" if r.safety else "–"})
    st.table(pd.DataFrame(rows).set_index(T("cmp_model")))
    a, b = results["real"].best, results["kaggle"].best
    st.caption(T("cmp_same") if a == b else T("cmp_diff", a=i18n.alt(a, L), b=i18n.alt(b, L)))




def sensitivity_grid(a):
    """One student: the top recommendation when each criterion weight moves by -20..+20 %."""
    L = ui.lang()
    st.caption(T("res_sens_help"))
    sens = a.sensitivity
    grid = sens.pivot(index="criterion", columns="delta", values="best").reindex(config.CRITERIA)
    changed = sens.pivot(index="criterion", columns="delta", values="changed").reindex(config.CRITERIA)
    grid = grid.map(lambda x: i18n.alt(x, L))
    grid.index = [i18n.feature(c, L) for c in grid.index]
    grid.columns = [f"{d:+.0%}" for d in grid.columns]
    changed.index, changed.columns = grid.index, grid.columns
    st.table(grid.style.apply(lambda _: changed.map(
        lambda c: "background-color: #FBEAD2" if c else "").to_numpy(), axis=None))
    k = int(sens["changed"].sum())
    if k == 0:
        st.success(T("res_sens_stable", k=len(sens), n=len(sens)), icon=":material/check_circle:")
    else:
        crit = sens.loc[sens["changed"], "criterion"].value_counts().index[0]
        st.warning(T("res_sens_changes", k=k, n=len(sens), crit=i18n.feature(crit, L)), icon=":material/info:")


def ranking_bars(a) -> str:
    L = ui.lang()
    return ui.bars([(i18n.alt(alt, L), float(s), f"{s:.3f}") for alt, s in a.ranking.items()])
