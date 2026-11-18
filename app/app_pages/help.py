"""App zone, help: how to use the app, how to read a result, privacy and limits."""
import html

import streamlit as st

import ui
from spk import config

L = ui.lang()
T = ui.T

ui.page_header(T("help_title"), T("help_lead"))
st.space("small")

# ---------------------------------------------------------------- how to use
ui.section(T("help_use_t"))
c1, c2 = st.columns(2, gap="medium")
for col, key, page in ((c1, "one", "student"), (c2, "class", "class")):
    with col.container(border=True, key=f"card_help_{key}", height="stretch"):
        st.markdown(f"**{T(f'help_{key}_t')}**")
        st.markdown("\n".join(f"{i}. {T(f'help_{key}_{i}')}" for i in range(1, 5)))
        st.page_link(ui.PAGE_FILE[page], label=T(f"nav_{page}"), icon=":material/arrow_forward:")

# ---------------------------------------------------------------- reading a result
st.space("medium")
ui.section(T("help_read_t"), T("help_read_d"))
with st.container(border=True, key="card_help_read"):
    rows = "".join(
        f"<div class='spk-def'><p class='spk-def-term'>{html.escape(T(f'help_read_{k}_t'))}</p>"
        f"<p class='spk-def-desc'>{html.escape(T(f'help_read_{k}_d', p=100 - config.SAFETY_PERCENTILE))}</p></div>"
        for k in ("best", "anx", "prio", "safety"))
    st.html(f"<div class='spk-defs'>{rows}</div>")

# ---------------------------------------------------------------- who, privacy, limits
st.space("medium")
c1, c2 = st.columns(2, gap="medium")
with c1.container(border=True, key="card_users", height="stretch"):
    st.markdown(f"**{T('home_users_t')}**")
    st.markdown(T("home_users_d"))
with c2.container(border=True, key="card_care", height="stretch"):
    st.markdown(f"**{T('home_care_t')}**")
    st.markdown("\n".join(f"- {T(f'home_care_{i}')}" for i in (1, 2, 3)))

st.space("small")
st.caption(T("help_contact", contact=config.REFERRAL_CONTACT[L]))
ui.footer()
