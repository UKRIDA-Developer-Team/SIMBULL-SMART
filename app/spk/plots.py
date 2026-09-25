"""Notebook charts as functions that return a Figure (for st.pyplot)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import config


def feature_importance(model, features=config.FEATURES):
    imp = pd.Series(model.feature_importances_, index=features).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    imp.plot(kind="barh", ax=ax)
    ax.set_xlabel("Importance")
    ax.set_title("Feature Importance - RF (predicting anxiety_score)")
    fig.tight_layout()
    return fig


def actual_vs_predicted(y_true, y_pred):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.3, s=10)
    lo, hi = min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())
    ax.plot([lo, hi], [lo, hi], "r--", lw=2)
    ax.set_xlabel("Actual anxiety_score")
    ax.set_ylabel("Predicted anxiety_score")
    ax.set_title("Actual vs Predicted (RF Regressor)")
    fig.tight_layout()
    return fig


def criteria_histograms(df_criteria):
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    for ax, col in zip(axes.flat, config.CRITERIA):
        ax.hist(df_criteria[col], bins=20)
        ax.set_title(col.replace("_", " "))
        ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def score_histogram(scores, title="SMART Score Distribution"):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(scores, bins=30)
    ax.set_title(title)
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Students")
    ax.grid(alpha=0.3)
    return fig


def correlation_heatmap(df):
    corr = df[config.CRITERIA + ["smart_score"]].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True, ax=ax)
    ax.set_title("Correlation Between Criteria and SMART Score")
    fig.tight_layout()
    return fig


def utility_radar(result, df_utility, n=100):
    ordered = result.sort_values("smart_score", ascending=False)
    mid = len(ordered) // 2 - n // 2
    groups = {
        f"Top {n}": ordered.head(n),
        f"Middle {n}": ordered.iloc[mid:mid + n],
        f"Bottom {n}": ordered.tail(n),
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
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1)
    ax.set_title("SMART Utility Profile", pad=30)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    return fig


def recommendation_by_alternative(result, title):
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    axes = axes.flat
    for ax, alt in zip(axes, config.ALTERNATIVES):
        subset = result.loc[result["Best_Recommendation"] == alt, "Recommendation_Score"]
        ax.hist(subset, bins=20, color="steelblue")
        ax.set_title(f"{alt} (n={len(subset)})")
        ax.grid(alpha=0.3)
    axes[-1].axis("off")
    fig.suptitle(title)
    fig.supxlabel("Recommendation Score")
    fig.supylabel("Students")
    fig.tight_layout()
    return fig


def top_heatmap(result, n=20):
    top = result.nsmallest(n, "rank")[config.ALTERNATIVES]
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.heatmap(top, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax)
    ax.set_title(f"Recommendation Scores for Top {n} Students")
    ax.set_xlabel("Alternative")
    ax.set_ylabel("Student ID")
    fig.tight_layout()
    return fig


def model_comparison(results: dict):
    comparison = pd.DataFrame(
        {name: r["Best_Recommendation"].value_counts() for name, r in results.items()}
    ).reindex(config.ALTERNATIVES).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(9, 5))
    comparison.plot(kind="bar", ax=ax)
    ax.set_title("Comparison of Recommendation Weight Profiles")
    ax.set_xlabel("Recommendation")
    ax.set_ylabel("Number of Students")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig, comparison


def single_student_bars(alt_scores: pd.Series):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    alt_scores.sort_values().plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Recommendation Score")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig
