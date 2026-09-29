"""Notebook charts (and new ones) as functions that return a Figure (for st.pyplot).

Every function takes `lang` so titles and labels follow the UI language.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from . import config, i18n  # noqa: E402

ALT_COLORS = dict(zip(config.ALTERNATIVES, ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974"]))
CRIT_COLORS = dict(zip(config.CRITERIA, sns.color_palette("Set2", len(config.CRITERIA))))

_T = {
    "importance": {"id": "Kepentingan fitur - RF (memprediksi skor kecemasan)", "en": "Feature importance - RF (predicting anxiety score)"},
    "importance_x": {"id": "Kepentingan (Gini)", "en": "Importance (Gini)"},
    "actual": {"id": "Skor kecemasan aktual", "en": "Actual anxiety score"},
    "predicted": {"id": "Skor kecemasan prediksi", "en": "Predicted anxiety score"},
    "avp": {"id": "Aktual vs prediksi (data uji)", "en": "Actual vs predicted (test set)"},
    "residual": {"id": "Sebaran galat (aktual - prediksi)", "en": "Residuals (actual - predicted)"},
    "smart_dist": {"id": "Sebaran skor prioritas SMART", "en": "SMART priority score distribution"},
    "n_students": {"id": "Jumlah siswa", "en": "Number of students"},
    "corr": {"id": "Korelasi kriteria dan skor SMART", "en": "Correlation between criteria and SMART score"},
    "radar": {"id": "Profil utilitas SMART", "en": "SMART utility profile"},
    "top": {"id": "Top", "en": "Top"}, "mid": {"id": "Tengah", "en": "Middle"}, "bottom": {"id": "Bawah", "en": "Bottom"},
    "reco_dist": {"id": "Sebaran skor rekomendasi per alternatif", "en": "Recommendation score by alternative"},
    "reco_score": {"id": "Skor rekomendasi", "en": "Recommendation score"},
    "top_heat": {"id": "Skor rekomendasi {n} siswa prioritas teratas", "en": "Recommendation scores of the top {n} priority students"},
    "student": {"id": "ID siswa", "en": "Student ID"},
    "profiles": {"id": "Perbandingan profil bobot", "en": "Comparison of weight profiles"},
    "freq_util": {"id": "Frekuensi rekomendasi vs rata-rata skor", "en": "Recommendation frequency vs average score"},
    "times": {"id": "Jumlah direkomendasikan", "en": "Times recommended"},
    "avg": {"id": "Rata-rata skor alternatif", "en": "Average alternative score"},
    "contrib_x": {"id": "Skor SMART (jumlah bobot × utilitas)", "en": "SMART score (sum of weight × utility)"},
    "sens_pop": {"id": "Porsi siswa yang rekomendasinya berubah", "en": "Share of students whose recommendation changes"},
    "weight_change": {"id": "Perubahan bobot", "en": "Weight change"},
    "mae_by": {"id": "MAE per gender (data uji)", "en": "MAE by gender (test set)"},
    "mix_by": {"id": "Sebaran rekomendasi per gender", "en": "Recommendation mix by gender"},
    "share": {"id": "Proporsi", "en": "Share"},
    "algo": {"id": "MAE validasi silang 5-fold (lebih rendah lebih baik)", "en": "5-fold CV MAE (lower is better)"},
    "strategies": {"id": "MAE validasi silang pada data riil", "en": "CV MAE on real data"},
    "weights": {"id": "Bobot kriteria per alternatif", "en": "Criterion weights per alternative"},
}


def _t(key, lang, **kw):
    text = _T[key].get(lang, _T[key]["id"])
    return text.format(**kw) if kw else text


def _feat(names, lang):
    return [i18n.feature(n, lang) for n in names]


def feature_importance(model, features=config.FEATURES, lang="id"):
    imp = pd.Series(model.feature_importances_, index=_feat(features, lang)).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    imp.plot(kind="barh", ax=ax, color="#4C72B0")
    ax.set_xlabel(_t("importance_x", lang))
    ax.set_title(_t("importance", lang))
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def actual_vs_predicted(y_true, y_pred, lang="id"):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.3, s=10)
    lo, hi = min(np.min(y_true), np.min(y_pred)), max(np.max(y_true), np.max(y_pred))
    ax.plot([lo, hi], [lo, hi], "r--", lw=2)
    ax.set_xlabel(_t("actual", lang))
    ax.set_ylabel(_t("predicted", lang))
    ax.set_title(_t("avp", lang))
    fig.tight_layout()
    return fig


def residuals(y_true, y_pred, lang="id"):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(np.asarray(y_true) - np.asarray(y_pred), bins=40, color="#8172B2")
    ax.axvline(0, color="k", lw=1)
    ax.set_title(_t("residual", lang))
    ax.set_ylabel(_t("n_students", lang))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def criteria_histograms(df_criteria, lang="id"):
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    for ax, col in zip(axes.flat, config.CRITERIA):
        ax.hist(df_criteria[col], bins=20, color=CRIT_COLORS[col])
        ax.set_title(i18n.feature(col, lang))
        ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def quantile_boxes(stats: dict, cols, lang="id"):
    """Box plots rebuilt from stored quantiles (no individual rows needed)."""
    boxes = [{"label": i18n.feature(c, lang) if c in i18n.FEATURES else c.removeprefix("x_"),
              "med": s["q50"], "q1": s["q25"], "q3": s["q75"], "whislo": s["q05"], "whishi": s["q95"],
              "mean": s["mean"], "fliers": []}
             for c, s in stats.items() if c in cols]
    fig, ax = plt.subplots(figsize=(9, 0.45 * len(boxes) + 1.2))
    if boxes:
        ax.bxp(boxes, vert=False, showmeans=True)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def score_histogram(scores, lang="id"):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores, bins=30, color="#4C72B0")
    ax.set_title(_t("smart_dist", lang))
    ax.set_xlabel(i18n.feature("smart_score", lang))
    ax.set_ylabel(_t("n_students", lang))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def correlation_heatmap(df, lang="id"):
    cols = config.CRITERIA + ["smart_score"]
    corr = df[cols].corr()
    corr.index = corr.columns = _feat(cols, lang)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True, ax=ax, vmin=-1, vmax=1)
    ax.set_title(_t("corr", lang))
    fig.tight_layout()
    return fig


def matrix_heatmap(matrix: pd.DataFrame, title: str, fmt=".2f", cmap="coolwarm", center=0):
    fig, ax = plt.subplots(figsize=(0.55 * matrix.shape[1] + 3, 0.45 * matrix.shape[0] + 1.5))
    sns.heatmap(matrix, annot=True, fmt=fmt, cmap=cmap, center=center, ax=ax, annot_kws={"size": 7})
    ax.set_title(title)
    fig.tight_layout()
    return fig


def utility_radar(result, df_utility, n=100, lang="id"):
    ordered = result.sort_values("smart_score", ascending=False)
    n = min(n, max(1, len(ordered) // 3))
    mid = len(ordered) // 2 - n // 2
    groups = {
        f"{_t('top', lang)} {n}": ordered.head(n),
        f"{_t('mid', lang)} {n}": ordered.iloc[mid:mid + n],
        f"{_t('bottom', lang)} {n}": ordered.tail(n),
    }
    labels = config.CRITERIA
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for label, group in groups.items():
        values = df_utility.loc[group.index, labels].mean().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=1, label=label)
        ax.fill(angles, values, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(_feat(labels, lang), fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_title(_t("radar", lang), pad=30)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    return fig


def recommendation_by_alternative(result, lang="id", suffix=""):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    axes = axes.flat
    for ax, alt in zip(axes, config.ALTERNATIVES):
        subset = result.loc[result["Best_Recommendation"] == alt, "Recommendation_Score"]
        ax.hist(subset, bins=20, color=ALT_COLORS[alt])
        ax.set_title(f"{i18n.alt(alt, lang)} (n={len(subset)})")
        ax.grid(alpha=0.3)
    axes[-1].axis("off")
    fig.suptitle(_t("reco_dist", lang) + suffix)
    fig.supxlabel(_t("reco_score", lang))
    fig.supylabel(_t("n_students", lang))
    fig.tight_layout()
    return fig


def top_heatmap(result, n=20, lang="id"):
    top = result.nsmallest(n, "rank")[config.ALTERNATIVES]
    top.columns = [i18n.alt(a, lang) for a in top.columns]
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(top) + 1.5))
    sns.heatmap(top, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax)
    ax.set_title(_t("top_heat", lang, n=len(top)))
    ax.set_xlabel("")
    ax.set_ylabel(_t("student", lang))
    fig.tight_layout()
    return fig


def model_comparison(results: dict, lang="id"):
    comparison = pd.DataFrame(
        {name: r["Best_Recommendation"].value_counts() for name, r in results.items()}
    ).reindex(config.ALTERNATIVES).fillna(0).astype(int)
    comparison.index = [i18n.alt(a, lang) for a in comparison.index]
    fig, ax = plt.subplots(figsize=(9, 5))
    comparison.plot(kind="bar", ax=ax, rot=0)
    ax.set_title(_t("profiles", lang))
    ax.set_ylabel(_t("n_students", lang))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig, comparison


def frequency_vs_utility(result, alt_scores, lang="id"):
    """Notebook cell 96: how often each alternative wins vs its average score."""
    wins = result["Best_Recommendation"].value_counts().reindex(config.ALTERNATIVES).fillna(0)
    avg = alt_scores[config.ALTERNATIVES].mean()
    labels = [i18n.alt(a, lang) for a in config.ALTERNATIVES]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(labels, wins.values, color="steelblue", alpha=0.7)
    ax1.set_ylabel(_t("times", lang), color="steelblue")
    ax2 = ax1.twinx()
    ax2.plot(labels, avg.values, color="darkorange", marker="o", linewidth=2)
    ax2.set_ylabel(_t("avg", lang), color="darkorange")
    ax1.set_title(_t("freq_util", lang))
    fig.tight_layout()
    return fig


def contribution_bars(contrib: pd.DataFrame, lang="id"):
    """Stacked horizontal bars: each alternative's score split by criterion (weight x utility)."""
    order = contrib.sum(axis=1).sort_values().index
    fig, ax = plt.subplots(figsize=(9, 3.8))
    left = np.zeros(len(order))
    for c in config.CRITERIA:
        vals = contrib.loc[order, c].to_numpy()
        ax.barh([i18n.alt(a, lang) for a in order], vals, left=left, color=CRIT_COLORS[c],
                label=i18n.feature(c, lang))
        left += vals
    for y, total in enumerate(left):
        ax.text(total + 0.005, y, f"{total:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, max(1.0, left.max() + 0.1))
    ax.set_xlabel(_t("contrib_x", lang))
    ax.legend(fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def weights_heatmap(weights_dict: dict, lang="id"):
    w = pd.DataFrame(weights_dict).reindex(config.CRITERIA)[config.ALTERNATIVES]
    w.index = _feat(w.index, lang)
    w.columns = [i18n.alt(a, lang) for a in w.columns]
    return matrix_heatmap(w, _t("weights", lang), cmap="Blues", center=None)


def population_sensitivity(table: pd.DataFrame, lang="id"):
    t = table.copy()
    t.index = _feat(t.index, lang)
    t.columns = [f"{d:+.0%}" for d in t.columns]
    fig = matrix_heatmap(t, _t("sens_pop", lang), fmt=".1%", cmap="Reds", center=None)
    fig.axes[0].set_xlabel(_t("weight_change", lang))
    return fig


def fairness_mae(frame: pd.DataFrame, lang="id"):
    """frame index = gender, columns mae (and n)."""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(frame.index.astype(str), frame["mae"], color=["#C44E52", "#4C72B0", "#55A868"][:len(frame)])
    for i, (m, n) in enumerate(zip(frame["mae"], frame["n"])):
        ax.text(i, m, f"{m:.3f}\n(n={n})", ha="center", va="bottom", fontsize=8)
    ax.set_title(_t("mae_by", lang))
    ax.set_ylim(0, frame["mae"].max() * 1.3)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def recommendation_mix_by_group(result: pd.DataFrame, group: pd.Series, lang="id"):
    mix = pd.crosstab(group, result["Best_Recommendation"], normalize="index").reindex(
        columns=config.ALTERNATIVES).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    left = np.zeros(len(mix))
    for alt in config.ALTERNATIVES:
        ax.barh(mix.index.astype(str), mix[alt], left=left, color=ALT_COLORS[alt], label=i18n.alt(alt, lang))
        left += mix[alt].to_numpy()
    ax.set_xlim(0, 1)
    ax.set_xlabel(_t("share", lang))
    ax.set_title(_t("mix_by", lang))
    ax.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.25), frameon=False)
    fig.tight_layout()
    return fig


def metric_bars(values: dict, title_key: str, highlight: str | None = None, lang="id"):
    s = pd.Series(values).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(s) + 1.2))
    colors = ["#C44E52" if k == highlight else "#4C72B0" for k in s.index]
    ax.barh(s.index, s.values, color=colors)
    for y, v in enumerate(s.values):
        ax.text(v, y, f" {v:.3f}", va="center", fontsize=8)
    ax.set_title(_t(title_key, lang))
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def recommendation_mix(result: pd.DataFrame, lang="id"):
    counts = result["Best_Recommendation"].value_counts().reindex(config.ALTERNATIVES).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar([i18n.alt(a, lang) for a in counts.index], counts.values,
           color=[ALT_COLORS[a] for a in counts.index])
    for i, v in enumerate(counts.values):
        ax.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
    ax.set_ylabel(_t("n_students", lang))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig
