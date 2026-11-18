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


def narrative(assessment, lang: str = i18n.DEFAULT, group: str | None = None) -> list[str]:
    """group names the comparison group of the priority percentile (ui.reference_group())."""
    ranked = assessment.ranking
    best, second = ranked.index[0], ranked.index[1]
    gap = float(ranked.iloc[0] - ranked.iloc[1])
    values, util = assessment.criteria, assessment.utility
    # A criterion reads as a problem ("short sleep") only when its utility is in the upper half.
    drivers = ", ".join(
        i18n.driver(c, float(values[c]), lang) if util[c] >= 0.5 else f"{_lower_first(i18n.feature(c, lang))} {float(values[c]):.1f}"
        for c in top_drivers(assessment.contributions, best))
    lines = [
        i18n.t("narr_best", lang, alt=i18n.alt(best, lang), score=float(ranked.iloc[0])),
        i18n.t("narr_drivers", lang, drivers=drivers),
        i18n.t("narr_gap", lang, alt2=i18n.alt(second, lang), gap=gap),
    ]
    if gap < 0.02:
        lines.append(i18n.t("narr_gap_small", lang, alt2=i18n.alt(second, lang)))
    lines.append(i18n.t("narr_priority", lang, score=assessment.priority, p=assessment.priority_percentile,
                        group=group or i18n.t("ref_group_generic", lang)))
    return lines


# ---------------------------------------------------------------- RF stage (xAI)

def _effect_items(effects, values, lang: str) -> str:
    return ", ".join(f"{_lower_first(i18n.feature(f, lang))} {value_text(f, values[f])} ({v:+.2f})"
                     for f, v in effects.items())


def value_text(feature: str, value) -> str:
    if feature == "gender":
        return str(value)
    return f"{float(value):.0f}" if feature in ("age", "academic_performance") else f"{float(value):.1f}"


def shap_narrative(expl, link: dict | None = None, lang: str = i18n.DEFAULT) -> list[str]:
    """Plain-language reading of a Shapley explanation (see xai.shapley_values), plus how the
    prediction feeds the SMART result when `link` (xai.smart_link) is given."""
    up, down = expl.raising(), expl.lowering()
    lines = [
        i18n.t("xai_pred_line", lang, pred=expl.prediction, base=expl.base_value,
               diff=expl.prediction - expl.base_value),
        i18n.t("xai_up", lang, items=_effect_items(up, expl.features, lang)) if len(up)
        else i18n.t("xai_flat", lang),
    ]
    if len(down):
        lines.append(i18n.t("xai_down", lang, items=_effect_items(down, expl.features, lang)))
    if link:
        lines.append(i18n.t("xai_link", lang, c=link["contribution"], alt=i18n.alt(link["alternative"], lang),
                            score=link["score"], share=link["share"]))
    return lines
