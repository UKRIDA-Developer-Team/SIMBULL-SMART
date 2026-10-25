"""Landing page: what the app does, how it works, the five kinds of support, and a way in."""
import html

import streamlit as st

import ui
from spk import config, i18n

rf, meta = ui.load_active()
L = ui.lang()
T = ui.T


def go(view: str):
    st.session_state["reco_view"] = view
    st.switch_page("app_pages/recommendation.py")


# ---------------------------------------------------------------- hero
left, right = st.columns([1.3, 1], gap="large", vertical_alignment="center")
with left:
    ui.page_header(T("home_title"), T("home_lead"), T("home_eyebrow"))
    st.space("small")
    with st.container(horizontal=True, gap="small"):
        if st.button(T("home_cta"), type="primary", icon=":material/arrow_forward:", icon_position="right"):
            go("single")
        if st.button(T("home_cta_batch"), icon=":material/group:"):
            go("batch")
    st.caption(T("home_facts", n=f"{meta.get('n_rows', 0):,}", k=len(config.CRITERIA)))

with right:
    # A static preview of what a result looks like, so first-time users know what they will get.
    st.html(f"""
<div class="spk-preview" aria-hidden="true">
  <p class="spk-preview-kicker">{T('home_preview')}</p>
  <div class="spk-preview-head">
    <span class="spk-icon spk-icon-tile">{ui.ALT_ICONS['Sleep']}</span>
    <div>
      <p class="spk-preview-label">{T('res_best')}</p>
      <p class="spk-preview-alt">{html.escape(i18n.alt('Sleep', L))}</p>
    </div>
  </div>
  <div class="spk-preview-row">
    <span>{T('home_preview_anx')}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-primary" style="width:66%"></div></div>
    <strong>6.6</strong>
  </div>
  <div class="spk-preview-row">
    <span>{T('home_preview_prio')}</span>
    <div class="spk-bar-track"><div class="spk-bar-fill is-primary" style="width:78%"></div></div>
    <strong>{T('prio_high')}</strong>
  </div>
</div>""")

# ---------------------------------------------------------------- how it works
st.space("large")
ui.section(T("home_how"))
steps = st.columns(3, gap="medium")
for i, col in enumerate(steps, start=1):
    with col.container(border=True, key=f"card_step{i}", height="stretch"):
        st.html(f"<span class='spk-step'>{i}</span>")
        st.markdown(f"**{T(f'home_step{i}_t')}**")
        st.caption(T(f"home_step{i}_d"))

# ---------------------------------------------------------------- the five kinds of support
st.space("medium")
ui.section(T("home_alts"), T("home_alts_lead"))
alt_cols = st.columns(len(config.ALTERNATIVES), gap="small")
for col, alt in zip(alt_cols, config.ALTERNATIVES):
    with col.container(border=True, key=f"card_alt_{alt}", height="stretch"):
        st.html(f"<span class='spk-icon spk-icon-tile'>{ui.ALT_ICONS[alt]}</span>")
        st.markdown(f"**{i18n.alt(alt, L)}**")
        st.caption(i18n.alt_desc(alt, L))

# ---------------------------------------------------------------- who and what to keep in mind
st.space("medium")
c1, c2 = st.columns(2, gap="medium")
with c1.container(border=True, key="card_users", height="stretch"):
    st.markdown(f"**{T('home_users_t')}**")
    st.markdown(T("home_users_d"))
with c2.container(border=True, key="card_care", height="stretch"):
    st.markdown(f"**{T('home_care_t')}**")
    st.markdown("\n".join(f"- {T(f'home_care_{i}')}" for i in (1, 2, 3)))

ui.footer()
