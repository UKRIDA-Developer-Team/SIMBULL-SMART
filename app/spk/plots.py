"""Notebook charts (and new ones) as functions that return a Figure (for st.pyplot).

Every function takes `lang` so titles and labels follow the UI language. All charts share
one quiet style (see STYLE) that matches the app theme in .streamlit/config.toml.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from . import config, i18n  # noqa: E402

# ---- palette (validated for colour-vision deficiency, see the app README) ----
INK, MUTED, FAINT = "#1D2725", "#5D6A67", "#8A9491"
LINE, SURFACE = "#E5E2DA", "#FFFFFF"
PRIMARY, PRIMARY_SOFT, NEUTRAL = "#1E6B5C", "#A9C7BF", "#C9C4B8"

# One fixed colour per intervention, used everywhere an intervention is coloured.
ALT_COLORS = dict(zip(config.ALTERNATIVES, ["#3F6FD1", "#1B9E77", "#E08A1E", "#D6456B", "#7B5BD6"]))
# Eight criteria, in CRITERIA order (adjacent pairs checked for stacked bars).
CRIT_COLORS = dict(zip(config.CRITERIA, ["#2A78D6", "#EB6834", "#1BAF7A", "#EDA100",
                                         "#E87BA4", "#008300", "#6250D6", "#E34948"]))
SEQ = LinearSegmentedColormap.from_list("spk_seq", ["#F4F8F7", "#B9D6CE", "#5E9E8F", "#1E6B5C", "#0E3D34"])
WARM = LinearSegmentedColormap.from_list("spk_warm", ["#FCF6EC", "#F3D3A1", "#E08A1E", "#9A5A0B"])
DIVERGING = LinearSegmentedColormap.from_list("spk_div", ["#2A78D6", "#F2F1EE", "#EB6834"])

STYLE = {
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": LINE, "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 14,
    "axes.titlecolor": INK, "axes.labelsize": 9.5, "axes.labelpad": 8,
    "xtick.major.size": 0, "ytick.major.size": 0, "xtick.major.pad": 6, "ytick.major.pad": 6,
    "grid.color": "#EFEDE7", "grid.linewidth": 0.8,
    "legend.frameon": False, "legend.fontsize": 9,
    "figure.titlesize": 12, "figure.titleweight": "bold",
}
plt.rcParams.update(STYLE)
GAP = dict(edgecolor=SURFACE, linewidth=1.5)    # thin surface gap between adjacent fills

_T = {
    "importance": {"id": "Kepentingan fitur (Random Forest)", "en": "Feature importance (Random Forest)"},
    "importance_x": {"id": "Kepentingan (Gini)", "en": "Importance (Gini)"},
    "actual": {"id": "Skor kecemasan aktual", "en": "Actual anxiety score"},
    "predicted": {"id": "Skor kecemasan prediksi", "en": "Predicted anxiety score"},
    "avp": {"id": "Aktual vs prediksi", "en": "Actual vs predicted"},
    "residual": {"id": "Sebaran galat (aktual - prediksi)", "en": "Residuals (actual - predicted)"},
    "smart_dist": {"id": "Sebaran skor prioritas SMART", "en": "SMART priority score distribution"},
    "n_students": {"id": "Jumlah siswa", "en": "Number of students"},
    "corr": {"id": "Korelasi kriteria dan skor SMART", "en": "Correlation between criteria and SMART score"},
    "radar": {"id": "Profil utilitas SMART", "en": "SMART utility profile"},
    "top": {"id": "Atas", "en": "Top"}, "mid": {"id": "Tengah", "en": "Middle"}, "bottom": {"id": "Bawah", "en": "Bottom"},
    "reco_dist": {"id": "Sebaran skor rekomendasi per alternatif", "en": "Recommendation score by alternative"},
    "reco_score": {"id": "Skor rekomendasi", "en": "Recommendation score"},
    "top_heat": {"id": "Skor rekomendasi {n} siswa prioritas teratas", "en": "Recommendation scores of the top {n} priority students"},
    "student": {"id": "ID siswa", "en": "Student ID"},
    "freq_util": {"id": "Frekuensi rekomendasi dan rata-rata skor", "en": "Recommendation frequency and average score"},
    "times": {"id": "Jumlah direkomendasikan", "en": "Times recommended"},
    "avg": {"id": "Rata-rata skor alternatif", "en": "Average alternative score"},
    "contrib_x": {"id": "Skor SMART (jumlah bobot × utilitas)", "en": "SMART score (sum of weight × utility)"},
    "sens_pop": {"id": "Porsi siswa yang rekomendasinya berubah", "en": "Share of students whose recommendation changes"},
    "weight_change": {"id": "Perubahan bobot", "en": "Weight change"},
    "mae_by": {"id": "MAE per gender (data uji)", "en": "MAE by gender (test set)"},
    "mix_by": {"id": "Sebaran rekomendasi per gender", "en": "Recommendation mix by gender"},
    "mix": {"id": "Sebaran rekomendasi", "en": "Recommendation mix"},
    "share": {"id": "Proporsi", "en": "Share"},
    "algo": {"id": "MAE validasi silang 5-fold (lebih rendah lebih baik)", "en": "5-fold CV MAE (lower is better)"},
    "strategies": {"id": "MAE validasi silang pada data riil", "en": "CV MAE on real data"},
    "weights": {"id": "Bobot kriteria per alternatif", "en": "Criterion weights per alternative"},
    "shap": {"id": "Mengapa prediksinya {pred:.2f}? (nilai Shapley)", "en": "Why the prediction is {pred:.2f} (Shapley values)"},
    "shap_x": {"id": "Prediksi skor kecemasan (0-10)", "en": "Predicted anxiety score (0-10)"},
    "shap_base": {"id": "rata-rata siswa pembanding", "en": "average reference student"},
    "shap_pred": {"id": "prediksi siswa ini", "en": "this student's prediction"},
    "shap_other": {"id": "{k} fitur lain", "en": "{k} other features"},
    "gini": {"id": "Gini (struktur pohon)", "en": "Gini (tree structure)"},
    "perm": {"id": "Permutasi (kenaikan MAE)", "en": "Permutation (MAE increase)"},
    "perm_title": {"id": "Dua cara mengukur kepentingan fitur", "en": "Two ways to measure feature importance"},
    "pdp_title": {"id": "Ketergantungan parsial (PDP, garis tebal) dan ICE (garis tipis per siswa)",
                  "en": "Partial dependence (PDP, thick line) and ICE (thin line per student)"},
    "pdp_y": {"id": "Prediksi kecemasan", "en": "Predicted anxiety"},
    "target_corr": {"id": "Korelasi dengan skor kecemasan (Pearson r)", "en": "Correlation with the anxiety score (Pearson r)"},
}

RAISE, LOWER = "#EB6834", "#2A78D6"     # same ends as DIVERGING: orange pushes anxiety up, blue down


def _t(key, lang, **kw):
    text = _T[key].get(lang, _T[key]["id"])
    return text.format(**kw) if kw else text


def _feat(names, lang):
    return [i18n.feature(n, lang) for n in names]


def _value_grid(ax, axis="y"):
    """Light solid gridlines on the value axis only, drawn behind the marks."""
    ax.grid(axis=axis, color=STYLE["grid.color"], linewidth=0.8)
    ax.set_axisbelow(True)


def feature_importance(model, features=config.FEATURES, lang="id"):
    imp = pd.Series(model.feature_importances_, index=_feat(features, lang)).sort_values()
    fig, ax = plt.subplots(figsize=(12, 4.4))
    ax.barh(imp.index, imp.values, color=PRIMARY, height=0.62)
    for y, v in enumerate(imp.values):
        ax.text(v, y, f"  {v:.3f}", va="center", fontsize=8.5, color=MUTED)
    ax.set_xlabel(_t("importance_x", lang))
    ax.set_title(_t("importance", lang))
    ax.spines["left"].set_visible(False)
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig


def actual_vs_predicted(y_true, y_pred, lang="id"):
    fig, ax = plt.subplots(figsize=(6, 5.4))
    ax.scatter(y_true, y_pred, alpha=0.22, s=9, color=PRIMARY, linewidths=0)
    lo, hi = min(np.min(y_true), np.min(y_pred)), max(np.max(y_true), np.max(y_pred))
    ax.plot([lo, hi], [lo, hi], color=FAINT, lw=1.2, ls=(0, (4, 3)))   # the ideal y = x line
    ax.set_xlabel(_t("actual", lang))
    ax.set_ylabel(_t("predicted", lang))
    ax.set_title(_t("avp", lang))
    _value_grid(ax, "both")
    fig.tight_layout()
    return fig


def residuals(y_true, y_pred, lang="id"):
    fig, ax = plt.subplots(figsize=(6, 5.4))
    ax.hist(np.asarray(y_true) - np.asarray(y_pred), bins=40, color=PRIMARY, **GAP)
    ax.axvline(0, color=INK, lw=1)
    ax.set_title(_t("residual", lang))
    ax.set_ylabel(_t("n_students", lang))
    _value_grid(ax)
    fig.tight_layout()
    return fig


def criteria_histograms(df_criteria, lang="id"):
    fig, axes = plt.subplots(2, 4, figsize=(12, 5.4))
    for ax, col in zip(axes.flat, config.CRITERIA):
        ax.hist(df_criteria[col], bins=20, color=PRIMARY, edgecolor=SURFACE, linewidth=0.8)
        ax.set_title(i18n.feature(col, lang), fontsize=10, pad=8)
        ax.tick_params(labelsize=8)
        _value_grid(ax)
    fig.tight_layout(h_pad=2.5, w_pad=2)
    return fig


def quantile_boxes(stats: dict, cols, lang="id"):
    """Box plots rebuilt from stored quantiles (no individual rows needed)."""
    boxes = [{"label": i18n.feature(c, lang) if c in i18n.FEATURES else c.removeprefix("x_"),
              "med": s["q50"], "q1": s["q25"], "q3": s["q75"], "whislo": s["q05"], "whishi": s["q95"],
              "mean": s["mean"], "fliers": []}
             for c, s in stats.items() if c in cols]
    fig, ax = plt.subplots(figsize=(11, 0.45 * len(boxes) + 1.2))
    if boxes:
        ax.bxp(boxes, orientation="horizontal", showmeans=True, patch_artist=True,
               boxprops=dict(facecolor="#DCEAE6", edgecolor=PRIMARY, linewidth=1),
               medianprops=dict(color=PRIMARY, linewidth=1.6),
               whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
               meanprops=dict(marker="^", markerfacecolor=INK, markeredgecolor=INK, markersize=5))
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig


def score_histogram(scores, lang="id"):
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    ax.hist(scores, bins=30, color=PRIMARY, **GAP)
    ax.set_title(_t("smart_dist", lang))
    ax.set_xlabel(i18n.feature("smart_score", lang))
    ax.set_ylabel(_t("n_students", lang))
    _value_grid(ax)
    fig.tight_layout()
    return fig


def correlation_heatmap(df, lang="id"):
    cols = config.CRITERIA + ["smart_score"]
    corr = df[cols].corr()
    corr.index = corr.columns = _feat(cols, lang)
    fig, ax = plt.subplots(figsize=(7.5, 6.6))
    sns.heatmap(corr, annot=True, cmap=DIVERGING, fmt=".2f", square=True, ax=ax, vmin=-1, vmax=1,
                linewidths=1.5, linecolor=SURFACE, annot_kws={"size": 8}, cbar_kws={"shrink": 0.7})
    ax.set_title(_t("corr", lang))
    fig.tight_layout()
    return fig


def matrix_heatmap(matrix: pd.DataFrame, title: str, fmt=".2f", cmap=SEQ, center=None):
    fig, ax = plt.subplots(figsize=(0.62 * matrix.shape[1] + 3.2, 0.45 * matrix.shape[0] + 1.6))
    sns.heatmap(matrix, annot=True, fmt=fmt, cmap=cmap, center=center, ax=ax, annot_kws={"size": 8},
                linewidths=1.5, linecolor=SURFACE, cbar_kws={"shrink": 0.8})
    ax.set_title(title)
    fig.tight_layout()
    return fig


def utility_radar(result, df_utility, n=100, lang="id"):
    ordered = result.sort_values("smart_score", ascending=False)
    n = min(n, max(1, len(ordered) // 3))
    mid = len(ordered) // 2 - n // 2
    groups = {
        f"{_t('top', lang)} {n}": (ordered.head(n), PRIMARY),
        f"{_t('mid', lang)} {n}": (ordered.iloc[mid:mid + n], "#5E9E8F"),
        f"{_t('bottom', lang)} {n}": (ordered.tail(n), "#A7B2AF"),
    }
    labels = config.CRITERIA
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 6.4), subplot_kw=dict(polar=True))
    for label, (group, color) in groups.items():
        values = df_utility.loc[group.index, labels].mean().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, color=color, label=label)
        ax.fill(angles, values, color=color, alpha=0.10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(_feat(labels, lang), fontsize=8.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels([])
    ax.spines["polar"].set_color(LINE)
    ax.grid(color=STYLE["grid.color"])
    ax.set_title(_t("radar", lang), pad=26)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12))
    fig.tight_layout()
    return fig


def recommendation_by_alternative(result, lang="id", suffix=""):
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.8), sharex=True)
    axes = axes.flat
    for ax, alt in zip(axes, config.ALTERNATIVES):
        subset = result.loc[result["Best_Recommendation"] == alt, "Recommendation_Score"]
        ax.hist(subset, bins=20, color=ALT_COLORS[alt], edgecolor=SURFACE, linewidth=0.8)
        ax.set_title(f"{i18n.alt(alt, lang)}  (n={len(subset)})", fontsize=10.5, pad=10)
        _value_grid(ax)
    axes[-1].axis("off")
    fig.suptitle(_t("reco_dist", lang) + suffix, x=0.01, ha="left")
    fig.supxlabel(_t("reco_score", lang), fontsize=9.5, color=MUTED)
    fig.supylabel(_t("n_students", lang), fontsize=9.5, color=MUTED)
    fig.tight_layout()
    return fig


def top_heatmap(result, n=20, lang="id"):
    top = result.nsmallest(n, "rank")[config.ALTERNATIVES]
    top.columns = [i18n.alt(a, lang) for a in top.columns]
    fig, ax = plt.subplots(figsize=(6.5, 0.32 * len(top) + 1.6))
    sns.heatmap(top, annot=True, cmap=SEQ, fmt=".2f", ax=ax, annot_kws={"size": 8},
                linewidths=1.5, linecolor=SURFACE, cbar_kws={"shrink": 0.8})
    ax.set_title(_t("top_heat", lang, n=len(top)))
    ax.set_xlabel("")
    ax.set_ylabel(_t("student", lang))
    fig.tight_layout()
    return fig


def frequency_vs_utility(result, alt_scores, lang="id"):
    """Notebook cell 96: how often each alternative wins, and its average score (two panels, one axis each)."""
    wins = result["Best_Recommendation"].value_counts().reindex(config.ALTERNATIVES).fillna(0)
    avg = alt_scores[config.ALTERNATIVES].mean()
    labels = [i18n.alt(a, lang) for a in config.ALTERNATIVES]
    colors = [ALT_COLORS[a] for a in config.ALTERNATIVES]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.bar(labels, wins.values, color=colors, width=0.62)
    for i, v in enumerate(wins.values):
        ax1.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax1.set_title(_t("times", lang))
    ax2.bar(labels, avg.values, color=colors, width=0.62)
    for i, v in enumerate(avg.values):
        ax2.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax2.set_title(_t("avg", lang))
    for ax in (ax1, ax2):
        ax.tick_params(axis="x", labelsize=8.5)
        _value_grid(ax)
    fig.suptitle(_t("freq_util", lang), x=0.01, ha="left")
    fig.tight_layout()
    return fig


def contribution_bars(contrib: pd.DataFrame, lang="id"):
    """Stacked horizontal bars: each alternative's score split by criterion (weight x utility)."""
    order = contrib.sum(axis=1).sort_values().index
    fig, ax = plt.subplots(figsize=(11, 4.2))
    left = np.zeros(len(order))
    for c in config.CRITERIA:
        vals = contrib.loc[order, c].to_numpy()
        ax.barh([i18n.alt(a, lang) for a in order], vals, left=left, color=CRIT_COLORS[c], height=0.6,
                label=i18n.feature(c, lang), **GAP)
        left += vals
    for y, total in enumerate(left):
        ax.text(total + 0.008, y, f"{total:.3f}", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, max(1.0, left.max() + 0.1))
    ax.set_xlabel(_t("contrib_x", lang))
    ax.spines["left"].set_visible(False)
    ax.legend(fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig


def weights_heatmap(weights_dict: dict, lang="id"):
    w = pd.DataFrame(weights_dict).reindex(config.CRITERIA)[config.ALTERNATIVES]
    w.index = _feat(w.index, lang)
    w.columns = [i18n.alt(a, lang) for a in w.columns]
    return matrix_heatmap(w, _t("weights", lang))


def population_sensitivity(table: pd.DataFrame, lang="id"):
    t = table.copy()
    t.index = _feat(t.index, lang)
    t.columns = [f"{d:+.0%}" for d in t.columns]
    fig = matrix_heatmap(t, _t("sens_pop", lang), fmt=".1%", cmap=WARM)
    fig.axes[0].set_xlabel(_t("weight_change", lang))
    return fig


def fairness_mae(frame: pd.DataFrame, lang="id"):
    """frame index = gender, columns mae (and n)."""
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.bar(frame.index.astype(str), frame["mae"], color=PRIMARY, width=0.55)
    for i, (m, n) in enumerate(zip(frame["mae"], frame["n"])):
        ax.text(i, m, f"{m:.3f}\n(n={n})", ha="center", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_title(_t("mae_by", lang))
    ax.set_ylim(0, frame["mae"].max() * 1.3)
    _value_grid(ax)
    fig.tight_layout()
    return fig


def recommendation_mix_by_group(result: pd.DataFrame, group: pd.Series, lang="id"):
    mix = pd.crosstab(group, result["Best_Recommendation"], normalize="index").reindex(
        columns=config.ALTERNATIVES).fillna(0)
    fig, ax = plt.subplots(figsize=(11, 3.4))
    left = np.zeros(len(mix))
    for alt in config.ALTERNATIVES:
        ax.barh(mix.index.astype(str), mix[alt], left=left, color=ALT_COLORS[alt], label=i18n.alt(alt, lang),
                height=0.6, **GAP)
        left += mix[alt].to_numpy()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel(_t("share", lang))
    ax.set_title(_t("mix_by", lang))
    ax.spines["left"].set_visible(False)
    ax.legend(fontsize=8.5, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.3))
    fig.tight_layout()
    return fig


def metric_bars(values: dict, title_key: str, highlight: str | None = None, lang="id"):
    s = pd.Series(values).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 0.42 * len(s) + 1.4))
    colors = [PRIMARY if k == highlight else NEUTRAL for k in s.index]
    ax.barh(s.index, s.values, color=colors, height=0.6)
    for y, v in enumerate(s.values):
        ax.text(v, y, f"  {v:.3f}", va="center", fontsize=8.5, color=MUTED)
    ax.set_title(_t(title_key, lang))
    ax.spines["left"].set_visible(False)
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig


def recommendation_mix(result: pd.DataFrame, lang="id"):
    counts = result["Best_Recommendation"].value_counts().reindex(config.ALTERNATIVES).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    ax.bar([i18n.alt(a, lang) for a in counts.index], counts.values,
           color=[ALT_COLORS[a] for a in counts.index], width=0.62)
    for i, v in enumerate(counts.values):
        ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9, color=MUTED)
    ax.set_title(_t("mix", lang))
    ax.set_ylabel(_t("n_students", lang))
    _value_grid(ax)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- xAI

def _fmt_value(feature: str, value) -> str:
    if feature == "gender":
        return str(value)
    return f"{float(value):.0f}" if feature in ("age", "academic_performance") else f"{float(value):.1f}"


def shap_waterfall(expl, lang="id", k: int = 7):
    """Waterfall from the average reference student (base value) to this student's prediction.

    Largest effects at the top; effects beyond the top k are merged into one bar at the bottom.
    """
    ordered = expl.ordered()
    top, rest = ordered.iloc[:k], ordered.iloc[k:]
    labels = [f"{i18n.feature(f, lang)} = {_fmt_value(f, expl.features[f])}" for f in top.index]
    values = list(top.values)
    if len(rest):
        labels.append(_t("shap_other", lang, k=len(rest)))
        values.append(float(rest.sum()))
    # draw bottom-up: the merged bar first, the largest effect last (top)
    labels, values = labels[::-1], values[::-1]
    fig, ax = plt.subplots(figsize=(11, 0.5 * len(values) + 1.9))
    start = expl.base_value
    for y, (label, v) in enumerate(zip(labels, values)):
        color = RAISE if v >= 0 else LOWER
        ax.barh(y, v, left=start, color=color, height=0.62)
        end = start + v
        ax.text(max(start, end), y, f"  {v:+.2f}", va="center", ha="left", fontsize=9, color=INK)
        if y < len(values) - 1:   # thin connector to the next bar
            ax.plot([end, end], [y + 0.31, y + 0.69], color=FAINT, lw=0.8)
        start = end
    ax.set_yticks(range(len(labels)), labels)
    lo = min(expl.base_value, expl.prediction, *(expl.base_value + np.cumsum(values)))
    hi = max(expl.base_value, expl.prediction, *(expl.base_value + np.cumsum(values)))
    pad = max(0.4, 0.12 * (hi - lo))
    ax.set_xlim(max(0, lo - pad), min(10.5, hi + pad * 1.6))
    ax.set_ylim(-0.8, len(values) - 0.2)
    for x, key, va, ypos in ((expl.base_value, "shap_base", "top", -0.75), (expl.prediction, "shap_pred", "bottom", len(values) - 0.25)):
        ax.axvline(x, color=FAINT, lw=1, ls=(0, (4, 3)), zorder=0)
        ax.text(x, ypos, f" {_t(key, lang)}: {x:.2f}", fontsize=8.5, color=MUTED, va=va, ha="left")
    ax.set_xlabel(_t("shap_x", lang))
    ax.set_title(_t("shap", lang, pred=expl.prediction))
    ax.spines["left"].set_visible(False)
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig


def importance_comparison(gini: pd.Series, perm: pd.DataFrame, lang="id"):
    """Side by side: Gini importance (from the trees) and permutation importance (from the errors)."""
    order = perm["mean"].sort_values().index
    labels = _feat(order, lang)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    g = gini.reindex(order)
    ax1.barh(labels, g.values, color=NEUTRAL, height=0.62)
    for y, v in enumerate(g.values):
        ax1.text(v, y, f"  {v:.3f}", va="center", fontsize=8.5, color=MUTED)
    ax1.set_title(_t("gini", lang), fontsize=10.5)
    p = perm.reindex(order)
    ax2.barh(labels, p["mean"].clip(lower=0), xerr=p["std"], color=PRIMARY, height=0.62,
             error_kw=dict(ecolor=MUTED, lw=0.8, capsize=2))
    for y, v in enumerate(p["mean"].values):
        ax2.text(max(v, 0), y, f"  {v:.3f}", va="center", fontsize=8.5, color=MUTED)
    ax2.set_title(_t("perm", lang), fontsize=10.5)
    for ax in (ax1, ax2):
        ax.spines["left"].set_visible(False)
        _value_grid(ax, "x")
        ax.set_xlim(0, ax.get_xlim()[1] * 1.15)
    fig.suptitle(_t("perm_title", lang), x=0.01, ha="left")
    fig.tight_layout()
    return fig


def pdp_grid(curves: list[dict], lang="id"):
    """One panel per feature: ICE curves (thin) and their mean, the PDP (thick)."""
    n = len(curves)
    cols = min(n, 2)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(11, 3.4 * rows + 0.6), sharey=True, squeeze=False)
    for ax, c in zip(axes.flat, curves):
        for line in c["ice"]:
            ax.plot(c["grid"], line, color=PRIMARY_SOFT, lw=0.7, alpha=0.6)
        ax.plot(c["grid"], c["pdp"], color=PRIMARY, lw=2.6)
        ax.set_title(i18n.feature(c["feature"], lang), fontsize=10.5, pad=8)
        _value_grid(ax, "both")
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    for ax in axes[:, 0]:
        ax.set_ylabel(_t("pdp_y", lang))
    fig.suptitle(_t("pdp_title", lang), x=0.01, ha="left")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- data mining page

ROLE_COLORS = {"feature": PRIMARY, "leakage": "#D6456B", "weak": NEUTRAL, "not_applicable": NEUTRAL,
               "unused": NEUTRAL}


def target_correlation_bars(decisions: pd.DataFrame, role_labels: dict, lang="id"):
    """Pearson r of each column with the anxiety score, coloured by the Phase 2 decision."""
    d = decisions.dropna(subset=["r"]).sort_values("r")
    fig, ax = plt.subplots(figsize=(6.6, 0.26 * len(d) + 1.7))
    colors = [ROLE_COLORS.get(r, NEUTRAL) for r in d["role"]]
    ax.barh(d.index, d["r"], color=colors, height=0.66)
    for y, v in enumerate(d["r"]):
        ax.text(v, y, f" {v:.2f} ", va="center", ha="left" if v >= 0 else "right",
                fontsize=8.5, color=MUTED)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlim(-1.05, 1.05)
    ax.set_title(_t("target_corr", lang))
    ax.spines["left"].set_visible(False)
    roles = list(dict.fromkeys(d["role"][::-1]))      # legend in the order the bars appear, top first
    handles = [Patch(color=ROLE_COLORS.get(r, NEUTRAL), label=role_labels.get(r, r)) for r in roles]
    ax.legend(handles=handles, fontsize=8.5, ncol=2, loc="upper center", bbox_to_anchor=(0.4, -0.06))
    ax.tick_params(axis="y", labelsize=8.5)
    _value_grid(ax, "x")
    fig.tight_layout()
    return fig
