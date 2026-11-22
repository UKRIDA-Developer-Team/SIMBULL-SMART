"""Report-zone helpers: numbered chapters with sections, captioned tables and figures, prev/next links.

Every page in app_pages/report/ starts with ch = Chapter(n, sections), calls ch.section(key) before
each part, ch.table / ch.figure for numbered exhibits, and ends with ch.end().
"""
import html

import streamlit as st

import ui
from spk import config, model, xai

T = ui.T


def tr(id_text: str, en_text: str) -> str:
    """Short inline text in the reader's language (captions that are used once)."""
    return id_text if ui.lang() == "id" else en_text


class Chapter:
    def __init__(self, n: int, sections: list[tuple[str, str]], settings: bool = True):
        self.n = n
        self.sections = sections
        self.figures = 0
        self.tables = 0
        self._header(settings)

    # ---------- chapter frame ----------
    def _header(self, settings: bool):
        st.html(f"<p class='spk-eyebrow'>{html.escape(T('report_eyebrow', n=self.n))}</p>")
        st.title(T(f"ch{self.n}_title"), anchor=False)
        st.html(f"<p class='spk-lead'>{html.escape(T(f'ch{self.n}_lead'))}</p>")
        with st.container(horizontal=True, vertical_alignment="center", gap="small", key="ch_meta"):
            if self.sections:
                items = "".join(f"<li><a href='#{self._anchor(i)}'><span class='spk-toc-n'>{self.n}.{i}</span>"
                                f"{html.escape(t)}</a></li>"
                                for i, (_, t) in enumerate(self.sections, start=1))
                st.html(f"<nav class='spk-toc'><p class='spk-toc-title'>{T('report_toc')}</p>"
                        f"<ol>{items}</ol></nav>")
            if settings:
                st.space("stretch")
                ui.model_picker()
        st.html("<hr class='spk-rule'>")

    def _anchor(self, i: int) -> str:
        return f"s{self.n}-{i}"

    def section(self, key: str, lead: str | None = None):
        i = next(i for i, (k, _) in enumerate(self.sections, start=1) if k == key)
        title = self.sections[i - 1][1]
        st.subheader(f"{self.n}.{i}  {title}", anchor=self._anchor(i))
        if lead:
            st.html(f"<p class='spk-para'>{html.escape(lead)}</p>")

    def end(self):
        pages = ui.ZONES["report"]
        idx = self.n - 1
        st.html("<hr class='spk-rule'>")
        with st.container(horizontal=True, gap="small", key="ch_pager"):
            if idx > 0:
                key, path, label, _ = pages[idx - 1]
                st.page_link(path, label=f"← {T(label)}")
            st.space("stretch")
            if idx < len(pages) - 1:
                key, path, label, _ = pages[idx + 1]
                st.page_link(path, label=f"{T(label)} →")
        ui.footer()

    # ---------- numbered exhibits ----------
    def caption(self, kind: str, text: str):
        if kind == "fig":
            self.figures += 1
            label = f"{T('report_fig')} {self.n}.{self.figures}"
        else:
            self.tables += 1
            label = f"{T('report_tab')} {self.n}.{self.tables}"
        st.html(f"<p class='spk-cap spk-cap-{kind}'><strong>{label}</strong> · {html.escape(text)}</p>")

    def figure(self, fig, text: str, compact: bool = False):
        """A Matplotlib figure with its caption below."""
        ui.show(fig, compact=compact)
        self.caption("fig", text)

    def table(self, frame, text: str, note: str | None = None):
        """A table with its caption above (report convention) and an optional source note below."""
        self.caption("tab", text)
        st.table(frame)
        if note:
            st.caption(note)


# ---------- cached data shared by several chapters ----------

@st.cache_data(show_spinner=False)
def base_test_predictions():
    """The Kaggle base model on the Kaggle test set (what the Kaggle success criteria judge)."""
    base, _ = ui.load_base()
    X_test, y_test = ui.kaggle_test_set()
    return X_test, y_test, model.predict(base, X_test)


def population():
    """The reference population scored with the active model: (result, utility)."""
    return ui.score(ui.load_reference()[config.FEATURES], True)


def pdp_curves(features: tuple):
    return _pdp_curves(features, ui.model_key())


@st.cache_data(show_spinner=False)
def _pdp_curves(features: tuple, kind: str):
    rf, _ = ui.load_model(kind)
    X_test, _, _ = base_test_predictions()
    sample = X_test.sample(min(400, len(X_test)), random_state=config.RANDOM_STATE)
    return [xai.partial_dependence(rf, sample, f) for f in features]


def metric_row(items: list[tuple]):
    """Metric tiles: (label, value) or (label, value, help text shown behind a (?))."""
    cols = st.columns(len(items), gap="small")
    for col, (label, value, *help_text) in zip(cols, items):
        col.metric(label, value, border=True, help=help_text[0] if help_text else None)
