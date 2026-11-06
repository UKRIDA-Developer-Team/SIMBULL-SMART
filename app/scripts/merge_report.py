"""Trace report: which questionnaire questions are merged into which model feature and DSS criterion.

    python scripts/merge_report.py data/private/gform_data.csv   # the real export (aggregates only)

Reads the export's headers and answers, follows spk/gform.py (COMPOSITES, SINGLE_ITEM, derive)
and writes reports/question_merge_report.md. The report holds question titles and aggregates,
never a respondent's answers.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spk import config, gform  # noqa: E402

ROLE_TEXT = {
    "criterion": "SMART criterion, and RF input",
    "model_only": "RF input only (reaches SMART inside `rf_anxiety_score`)",
    "target": "RF training target (what `rf_anxiety_score` predicts)",
    "extra": "Extra column (report only, not a criterion)",
}


def md_table(frame: pd.DataFrame) -> list[str]:
    cells = frame.astype(str).replace({"nan": "-", "None": "-", "<NA>": "-"})
    head = "| " + " | ".join(cells.columns) + " |"
    rule = "|" + "|".join("---" for _ in cells.columns) + "|"
    return [head, rule, *("| " + " | ".join(row) + " |" for row in cells.to_numpy())]


def criteria_table(summary: pd.DataFrame) -> pd.DataFrame:
    rows = [{"SMART criterion": "`rf_anxiety_score`", "Type": config.CRITERIA_TYPE["rf_anxiety_score"],
             "Comes from": "Random Forest prediction from all 11 model features",
             "Questions": int(summary.loc[config.FEATURES, "questions"].sum()),
             "Merged?": "yes (model output)"}]
    for c in config.CRITERIA[1:]:
        s = summary.loc[c]
        rows.append({"SMART criterion": f"`{c}`", "Type": config.CRITERIA_TYPE[c],
                     "Comes from": s["rule"], "Questions": int(s["questions"]),
                     "Merged?": f"yes, {s['questions']} questions" if s["merged"] else "no, 1 question"})
    return pd.DataFrame(rows)


def feature_table(summary: pd.DataFrame, derived: pd.DataFrame, reliability: dict) -> pd.DataFrame:
    rows = []
    for name, s in summary.iterrows():
        column = "x_sleep_quality" if name == "sleep_quality" else name
        values = pd.to_numeric(derived[column], errors="coerce") if column in derived and name != "gender" else None
        span = "-" if values is None or values.dropna().empty else f"{values.min():.4g} to {values.max():.4g}"
        alpha = reliability.get(name, {}).get("alpha")
        count = str(s["questions"]) if s["questions"] == s["questions_original"] else \
            f"{s['questions']} ({s['questions_original']} on the original form)"
        rows.append({"Derived output": f"`{column}`", "Role in the DSS": ROLE_TEXT[s["role"]],
                     "Questions": count, "Merge rule": s["rule"], "Range in this export": span,
                     "Cronbach alpha": "-" if alpha is None else f"{alpha:.2f}"})
    return pd.DataFrame(rows)


def question_table(table: pd.DataFrame) -> pd.DataFrame:
    def answer(row):
        if row["kind"] == "scale":
            return f"{int(row['levels'])}-level scale" + (", reversed" if row["reversed"] else "")
        return {"hours": "hours", "number": "number", "map": "choice -> value", "date": "date"}.get(row["kind"], row["kind"])

    return pd.DataFrame({
        "#": range(1, len(table) + 1),
        "Question in the export": table["question"].replace("", "(not in this export)").str.replace("|", "/"),
        "Field": "`" + table["field"] + "`",
        "Answer": table.apply(answer, axis=1),
        "Form": table["form"].map({"both": "both versions", "revised": "revised only"}),
        "Merged into": "`" + table["output"].replace({"sleep_quality": "x_sleep_quality"}) + "`",
    })


def build(export: Path) -> str:
    mapping = gform.load_mapping()
    raw = gform.read_export(export)
    prepared = gform.prepare(raw, mapping)
    report, res = prepared.report, prepared.resolution
    summary = gform.merge_summary(mapping)
    table = gform.merge_table(mapping, res)

    traced = set(table["field"])
    extras = [f for f, s in mapping["fields"].items() if s.get("extra") and f in res.columns]
    pii = [f for f, s in mapping["fields"].items() if s.get("pii") and f in res.columns and f not in traced]
    model_questions = int(summary.loc[config.FEATURES, "questions"].sum())
    merged = summary[summary["merged"]]
    versions = report["rows_by_form_version"]
    try:
        shown = export.resolve().relative_to(config.APP_DIR)
    except ValueError:
        shown = export.name
    private = config.PRIVATE_DATA_DIR.resolve() in export.resolve().parents
    source = "the real, confidential export; aggregates only" if private else "a questionnaire export"

    lines = [
        "# Question merge report: questionnaire -> model features -> SMART criteria",
        "",
        f"Source: `{shown}` ({source}), {report['rows_raw']} rows, "
        f"{raw.shape[1]} columns. Form versions: " + ", ".join(f"{k} {v}" for k, v in versions.items()) + ".",
        "Generated by `scripts/merge_report.py` from `spk/gform.py` and `spk/gform_mapping.json`.",
        "",
        "## Answer",
        "",
        "Yes. The questions are merged before the DSS uses them. `gform.derive` runs first and turns the "
        f"answers into the 11 model features; SMART (`smart.utility`) only sees those features and the "
        "Random Forest prediction, never a raw answer.",
        "",
        f"- {model_questions} questions feed the 11 model features. {len(merged.loc[merged.index.isin(config.FEATURES)])} "
        "features are merged from several questions; the other "
        f"{len(config.FEATURES) - len(merged.loc[merged.index.isin(config.FEATURES)])} use one question each.",
        f"- {len(gform.COMPOSITES[config.TARGET])} Psikologis questions are merged into the target `anxiety_score`. "
        "They are never model features, so the target does not leak into the prediction.",
        f"- Of the {len(config.CRITERIA)} SMART criteria, 2 are merged directly from several questions "
        "(`family_expectation`, `burnout_score`), 5 use one question each, and `rf_anxiety_score` is the "
        "model output built from all 11 features.",
        "- \"Saya mampu membicarakan kesulitan ... dengan keluarga\" (`family_talk`, revised form) is no longer "
        "merged into `family_expectation`: on the 109 revised rows it lowered Cronbach's alpha from 0.53 to 0.37. "
        "It is kept as an extra column.",
        "- `exam_pressure` and `stress_level` are merged features that are not SMART criteria. They reach the "
        "decision only inside `rf_anxiety_score`.",
        "- Merge rule: each Likert answer goes to 0-1 (reversed where marked), the items of one feature are "
        "averaged, and the mean is scaled to the Kaggle range. A row answered on the original form skips the "
        "revised-only items, so its mean uses the original items.",
        "",
        "## 1. SMART criteria and where they come from",
        "",
        *md_table(criteria_table(summary)),
        "",
        "Type: benefit = a higher value raises the priority; cost = a lower value raises the priority.",
        "",
        "## 2. Derived outputs: how many questions are merged into each",
        "",
        *md_table(feature_table(summary, prepared.data, report["reliability"])),
        "",
        "Cronbach alpha shows how well the merged items agree (computed on the rows that answered every "
        "item). It is empty for one-question outputs.",
        "",
        "## 3. Question by question",
        "",
        *md_table(question_table(table)),
        "",
        "The age feature also uses the answer time (`Timestamp`) as the reference date. The in-app "
        "questionnaire asks age directly.",
        "",
        "## 4. Revised form: does adding items change the merged score?",
        "",
        "Computed on the revised rows: the score from the original items against the score from all items.",
        "",
        *md_table(pd.DataFrame([{"Merged output": f"`{k}`", "Rows": v["n"], "Correlation r": v["r"],
                                 "Mean shift (score units)": v["shift"]}
                                for k, v in report["item_set_check"].items()])),
        "",
        "A high r and a small shift mean rows from both form versions can be pooled.",
        "",
        "## 5. Questions that are not merged and not criteria",
        "",
        f"- {len(extras)} extra questions are kept one by one as `x_` columns: "
        + ", ".join(f"`{e}`" for e in extras) + ". Only the report-only strategy S4 uses them.",
        f"- {len(pii)} personal columns are dropped after parsing: " + ", ".join(f"`{p}`" for p in pii) + ".",
        "- Columns no field uses: " + (", ".join(f"`{u}`" for u in res.unused) or "none") + ".",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("export", help="Google Form export (.csv or .xlsx), e.g. data/private/gform_data.csv")
    parser.add_argument("--out", default=str(config.APP_DIR / "reports" / "question_merge_report.md"))
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(Path(args.export)))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
