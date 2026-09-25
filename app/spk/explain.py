"""Why a recommendation came out on top: per-criterion contributions and a short narrative."""
import pandas as pd

from . import config, i18n


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:]


def contributions(u_row: pd.Series, weights_dict: dict) -> pd.DataFrame:
    """alternatives x criteria, cell = weight * utility (row sums = SMART alternative scores)."""
    return pd.DataFrame(
        {alt: {c: w.get(c, 0.0) * float(u_row[c]) for c in config.CRITERIA} for alt, w in weights_dict.items()}
    ).T[config.CRITERIA]


def top_drivers(contrib: pd.DataFrame, alternative: str, k: int = 3) -> list[str]:
    row = contrib.loc[alternative]
    return [c for c in row.sort_values(ascending=False).index[:k] if row[c] > 0]


def narrative(assessment, profile_label: str, lang: str = i18n.DEFAULT) -> list[str]:
    ranked = assessment.ranking
    best, second = ranked.index[0], ranked.index[1]
    gap = float(ranked.iloc[0] - ranked.iloc[1])
    values, util = assessment.criteria, assessment.utility
    # A criterion reads as a problem ("short sleep") only when its utility is in the upper half.
    drivers = ", ".join(
        i18n.driver(c, float(values[c]), lang) if util[c] >= 0.5 else f"{_lower_first(i18n.feature(c, lang))} {float(values[c]):.1f}"
        for c in top_drivers(assessment.contributions, best))
    lines = [
        i18n.t("narr_best", lang, alt=i18n.alt(best, lang), score=float(ranked.iloc[0]), profile=profile_label),
        i18n.t("narr_drivers", lang, drivers=drivers),
        i18n.t("narr_gap", lang, alt2=i18n.alt(second, lang), gap=gap),
    ]
    if gap < 0.02:
        lines.append(i18n.t("narr_gap_small", lang, alt2=i18n.alt(second, lang)))
    lines.append(i18n.t("narr_priority", lang, score=assessment.priority, p=assessment.priority_percentile))
    return lines
