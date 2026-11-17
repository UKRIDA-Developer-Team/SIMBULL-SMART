"""Google Form export -> the 11 model features (+ anxiety_score target).

Pipeline:
    raw export --resolve_columns--> field columns --encode--> numeric codes
    --derive--> model features, target, extras (PII dropped)

The questionnaire asks SMA students on Likert and range scales. `derive` rescales
those answers onto the ranges the Kaggle features use, so the same Random Forest
can be pretrained on Kaggle and retrained on real answers.

The form exists in two versions (context_ori.pdf, then the revised context_new.pdf).
Both are the same Google Form, so one export mixes rows from either version: rows
answered before the revision leave the added questions empty. Every composite is a
mean over the items a row has, which gives the original formula for original rows
and the revised formula for revised rows. `quality_report` checks how far the two
item sets agree before they are pooled.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

MAPPING_PATH = Path(__file__).with_name("gform_mapping.json")
LIST_NUMBER = re.compile(r"^\d{1,2}\.\s*(?=\S)")

# Fields both form versions ask that feed the 11 model features (target items listed separately).
CORE_FIELDS = [
    "gender", "birth_date", "study_hours", "late_night", "time_insufficient", "late_tasks",
    "sleep_duration", "report_grade", "many_tasks", "exam_stress", "fear_parents",
    "family_demand", "exercise_days", "pocket_money", "time_split", "exhausted", "lost_interest",
]
# Target items both versions ask; a row needs all of them to get a target.
TARGET_FIELDS = ["p1_nervous", "p2_worry", "p3_focus", "p4_distracted", "p5_hard_finish"]

# Likert items averaged into one score. The number of answer levels and the
# reverse flag come from gform_mapping.json; items added in the revised form
# ('new_form') are empty for original-form rows and skipped in their mean.
COMPOSITES = {
    "exam_pressure": ["exam_stress", "below_target"],
    "stress_level": ["many_tasks", "time_insufficient", "late_tasks", "late_night"],
    # "family_talk" (revised form) was dropped from family_expectation after the real data: on the
    # 109 revised rows it lowered Cronbach's alpha from 0.53 to 0.37. It stays as an extra (x_family_talk).
    "family_expectation": ["fear_parents", "family_demand"],
    "burnout_score": ["time_split", "exhausted", "lost_interest"],
    "sleep_quality": ["sleep_onset", "night_waking", "sleep_restless"],
    config.TARGET: TARGET_FIELDS + ["p6_irritable", "p7_avoid"],
}
# Model features that come from one question (nothing is merged).
SINGLE_ITEM = {
    "age": "birth_date", "gender": "gender", "study_hours_per_day": "study_hours",
    "academic_performance": "report_grade", "sleep_hours": "sleep_duration",
    "physical_activity": "exercise_days", "financial_stress": "pocket_money",
}
# How the question(s) of each output become its value (shown in the merge report).
MERGE_RULES = {
    "age": "floor((answer time - birth date) / 365.25)",
    "gender": "text -> Female / Male",
    "study_hours_per_day": "hours as answered",
    "academic_performance": "grade as answered (0-100)",
    "exam_pressure": "1 + 9 x mean of the items (1-10)",
    "stress_level": "10 x mean of the items (0-10)",
    "sleep_hours": "hours as answered",
    "physical_activity": "day band -> days per week (0-7)",
    "financial_stress": "10 x (5 - answer) / 4, reversed (0-10)",
    "family_expectation": "10 x mean of the items (0-10)",
    "burnout_score": "10 x mean of the items (0-10)",
    config.TARGET: "10 x mean of the items (0-10)",
    "sleep_quality": "10 x mean of the items (0-10)",
}


def load_mapping(path: Path | str = MAPPING_PATH) -> dict:
    return json.loads(Path(path).read_text())


def norm(text) -> str:
    """Lowercase, unify dashes and whitespace so answers and headers compare reliably."""
    s = str(text).replace(" ", " ").replace("–", "-").replace("—", "-")
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"([<>])\s+", r"\1", s)        # "> 5" and ">5" are the same option
    return re.sub(r"\s+", " ", s).strip().lower()


# ---------- value parsers (one per field kind) ----------

def parse_hours(value) -> float:
    """'Dibawah 30 menit' -> 0.25, '1 jam 30 menit' -> 1.5, '7' -> 7.0."""
    if pd.isna(value):
        return np.nan
    s = LIST_NUMBER.sub("", norm(value))
    if "dibawah" in s or "di bawah" in s or s.startswith("<"):
        return 0.25
    h = re.search(r"(\d+(?:[.,]\d+)?)\s*jam", s)
    m = re.search(r"(\d+)\s*menit", s)
    if h or m:
        return (float(h.group(1).replace(",", ".")) if h else 0.0) + (int(m.group(1)) / 60 if m else 0.0)
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return np.nan


def parse_number(value) -> float:
    if pd.isna(value):
        return np.nan
    s = norm(value).replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else np.nan


def _lookup(value, table: dict):
    if pd.isna(value):
        return np.nan
    s = norm(value)
    if s in table:
        return table[s]
    stripped = LIST_NUMBER.sub("", s)
    return table.get(stripped, np.nan)


def scale_labels(options: list) -> list[str]:
    """Display text per level: an option given as a list of labels shows its first label."""
    return [o[0] if isinstance(o, list) else o for o in options]


def scale_table(options: list) -> dict:
    """Ordered option list -> {normalized text: 1..n}; bare digits '1'..'n' also accepted.

    An option may be a list of labels that share one level (e.g. "Selalu" / "Sangat sering").
    """
    table = {norm(label): i + 1 for i, o in enumerate(options)
             for label in (o if isinstance(o, list) else [o])}
    # A digit answer is ambiguous only when an option is itself a digit (late_tasks5).
    if not any(k.isdigit() for k in table):
        table.update({str(i + 1): i + 1 for i in range(len(options))})
    return table


def parse_series(series: pd.Series, spec: dict, mapping: dict) -> pd.Series:
    kind = spec["kind"]
    if kind == "hours":
        out = series.map(parse_hours)
    elif kind == "number":
        out = series.map(parse_number)
    elif kind == "scale":
        table = scale_table(mapping["scales"][spec["scale"]])
        out = series.map(lambda v: _lookup(v, table))
    elif kind == "map":
        table = {norm(k): v for k, v in mapping["value_maps"][spec["map"]].items()}
        out = series.map(lambda v: _lookup(v, table))
    elif kind in ("date", "datetime"):
        out = pd.to_datetime(series, dayfirst=mapping.get("date_dayfirst", True), errors="coerce")
    else:  # text
        out = series
    if kind in ("hours", "number") and "range" in spec:
        lo, hi = spec["range"]
        out = out.where(out.between(lo, hi))
    return out


def parse_rate(series: pd.Series, spec: dict, mapping: dict) -> float:
    """Share of non-empty answers that parse. Used to pick between same-titled columns."""
    present = series.dropna()
    present = present[present.astype(str).str.strip() != ""]
    if present.empty or spec["kind"] == "text":
        return 0.0
    return float(parse_series(present, spec, mapping).notna().mean())


# ---------- header resolution ----------

@dataclass
class Resolution:
    columns: dict[str, str] = field(default_factory=dict)      # field -> header
    missing: list[str] = field(default_factory=list)            # required fields not found
    ambiguous: dict[str, list[str]] = field(default_factory=dict)
    skipped: dict[str, list[str]] = field(default_factory=dict)  # optional fields left out as ambiguous
    unused: list[str] = field(default_factory=list)             # headers no field claimed

    @property
    def ok(self) -> bool:
        return not self.missing and not self.ambiguous


def resolve_columns(df: pd.DataFrame, mapping: dict | None = None) -> Resolution:
    mapping = mapping or load_mapping()
    fields = mapping["fields"]
    headers = {h: norm(h) for h in df.columns}
    res = Resolution()

    candidates: dict[str, list[str]] = {}
    for name, spec in fields.items():
        if spec.get("header"):
            exact = [h for h in df.columns if norm(h) == norm(spec["header"])]
            candidates[name] = exact
        else:
            keys = [norm(k) for k in spec["match"]]
            # Prefer the most specific (first) match key that finds anything.
            for key in keys:
                found = [h for h, n in headers.items() if key in n]
                if found:
                    candidates[name] = found
                    break
            else:
                candidates[name] = []

    claimed: set[str] = set()
    pending = dict(candidates)
    # Resolve unique candidates first, then disambiguate the rest by parse rate.
    changed = True
    while changed:
        changed = False
        for name, cands in list(pending.items()):
            free = [c for c in cands if c not in claimed]
            if len(free) == 1:
                res.columns[name] = free[0]
                claimed.add(free[0])
                del pending[name]
                changed = True
        if not changed:
            for name, cands in list(pending.items()):
                free = [c for c in cands if c not in claimed]
                if len(free) < 2:
                    continue
                scores = {c: parse_rate(df[c], fields[name], mapping) for c in free}
                best = sorted(scores, key=scores.get, reverse=True)
                if scores[best[0]] >= 0.8 and scores[best[0]] > scores[best[1]]:
                    res.columns[name] = best[0]
                    claimed.add(best[0])
                    del pending[name]
                    changed = True
                    break

    for name, cands in pending.items():
        free = [c for c in cands if c not in claimed]
        required = not fields[name].get("optional") and not fields[name].get("extra")
        if len(free) > 1:
            # An optional item (e.g. one a removed question still shares text with) must not
            # block the whole export: leave it out and report it.
            (res.ambiguous if required else res.skipped)[name] = free
        elif required:
            res.missing.append(name)
    res.unused = [h for h in df.columns if h not in claimed]
    return res


# ---------- encode + derive ----------

def encode(df: pd.DataFrame, resolution: Resolution, mapping: dict | None = None) -> pd.DataFrame:
    """Raw answers -> one numeric (or datetime/text) column per resolved field."""
    mapping = mapping or load_mapping()
    out = pd.DataFrame(index=df.index)
    for name, header in resolution.columns.items():
        out[name] = parse_series(df[header], mapping["fields"][name], mapping)
    return out


def _unit(s: pd.Series, n_levels: int) -> pd.Series:
    """Ordinal code 1..n -> 0..1."""
    return (s - 1) / (n_levels - 1)


def item_units(fields: pd.DataFrame, items: list[str], mapping: dict) -> pd.DataFrame:
    """The items present in `fields` on 0..1, oriented so 1 = more of the construct."""
    cols = {}
    for name in items:
        if name not in fields:
            continue
        spec = mapping["fields"][name]
        u = _unit(fields[name], len(mapping["scales"][spec["scale"]]))
        cols[name] = 1 - u if spec.get("reverse") else u
    return pd.DataFrame(cols, index=fields.index)


def composite(fields: pd.DataFrame, name: str, mapping: dict, original_only: bool = False) -> pd.Series:
    """Mean (0..1) of the items of COMPOSITES[name] each row answered; NaN when it has none."""
    items = COMPOSITES[name]
    if original_only:
        items = [c for c in items if not mapping["fields"][c].get("new_form")]
    units = item_units(fields, items, mapping)
    return units.mean(axis=1, skipna=True) if units.shape[1] else pd.Series(np.nan, index=fields.index)


def form_version(fields: pd.DataFrame, mapping: dict) -> pd.Series:
    """'revised' when a row answered any question added in the revised form, else 'original'."""
    added = [n for n, s in mapping["fields"].items() if s.get("new_form") and n in fields]
    revised = fields[added].notna().any(axis=1) if added else pd.Series(False, index=fields.index)
    for name in ("late_night", "late_tasks"):   # their top option exists only in the revised form
        if name in fields:
            revised |= fields[name].eq(len(mapping["scales"][mapping["fields"][name]["scale"]]))
    return revised.map({True: "revised", False: "original"})


def age_from(fields: pd.DataFrame, reference_date=None) -> pd.Series:
    ref = fields["timestamp"] if "timestamp" in fields else pd.Series(pd.NaT, index=fields.index)
    fallback = pd.Timestamp(reference_date) if reference_date else pd.Timestamp.today().normalize()
    ref = ref.fillna(fallback)
    age = ((ref - fields["birth_date"]).dt.days / 365.25).apply(np.floor)
    return age.where(age.between(10, 40))


def derive(fields: pd.DataFrame, reference_date=None, mapping: dict | None = None) -> pd.DataFrame:
    """Encoded fields -> model features on Kaggle-like scales, target, and x_ extras.

    unit(x) maps an n-level answer 1..n to 0..1; (r) = reversed, 1 - unit(x); [rev] = item
    only in the revised form, skipped for rows answered on the original form.
    Transformations (documented in the report and About page):
      exam_pressure      = 1 + 9 * mean(unit(exam_stress), unit(below_target)[rev])      (1-10)
      stress_level       = 10 * mean(unit(many_tasks), unit(time_insufficient),
                                     unit(late_tasks), unit(late_night))   (proxy, 0-10)
      financial_stress   = 10 * (5 - pocket_money) / 4                     (reversed, 0-10)
      family_expectation = 10 * mean(unit(fear_parents), unit(family_demand))
      burnout_score      = 10 * mean(unit(time_split), unit(exhausted), unit(lost_interest))
      anxiety_score      = 10 * mean(unit(p1..p5), p3 (r), unit(p6, p7)[rev])          (0-10)
      x_sleep_quality    = 10 * mean(unit(sleep_onset, night_waking, sleep_restless))[rev]
    On original rows these reduce to the original formulas, e.g. anxiety = sum(p - 1) / 2.
    """
    mapping = mapping or load_mapping()
    out = pd.DataFrame(index=fields.index)
    get = lambda c: fields[c] if c in fields else pd.Series(np.nan, index=fields.index)  # noqa: E731

    if "age" in fields:  # the in-app questionnaire asks age directly
        out["age"] = fields["age"]
    elif "birth_date" in fields:
        out["age"] = age_from(fields, reference_date)
    else:
        out["age"] = np.nan
    one = lambda feature: get(SINGLE_ITEM[feature])  # noqa: E731
    out["gender"] = one("gender")
    out["study_hours_per_day"] = one("study_hours_per_day")
    out["academic_performance"] = one("academic_performance")
    out["exam_pressure"] = 1 + 9 * composite(fields, "exam_pressure", mapping)
    out["stress_level"] = 10 * composite(fields, "stress_level", mapping)
    out["sleep_hours"] = one("sleep_hours")
    out["physical_activity"] = one("physical_activity")
    out["financial_stress"] = 10 * (5 - one("financial_stress")) / 4
    out["family_expectation"] = 10 * composite(fields, "family_expectation", mapping)
    out["burnout_score"] = 10 * composite(fields, "burnout_score", mapping)
    out = out[config.FEATURES]

    if all(c in fields for c in TARGET_FIELDS):
        # A target needs every item both versions ask; the revised items join when answered.
        score = 10 * composite(fields, config.TARGET, mapping)
        out[config.TARGET] = score.where(fields[TARGET_FIELDS].notna().all(axis=1))

    for name, spec in mapping["fields"].items():
        if spec.get("extra") and name in fields:
            out[f"x_{name}"] = fields[name]
    if any(c in fields for c in COMPOSITES["sleep_quality"]):
        out["x_sleep_quality"] = 10 * composite(fields, "sleep_quality", mapping)
    return out


# ---------- question -> feature -> criterion trace ----------

def output_items() -> dict[str, list[str]]:
    """Every derived output (11 features, target, sleep_quality extra) -> the fields it is built from."""
    out = {f: COMPOSITES[f] if f in COMPOSITES else [SINGLE_ITEM[f]] for f in config.FEATURES}
    out[config.TARGET] = COMPOSITES[config.TARGET]
    out["sleep_quality"] = COMPOSITES["sleep_quality"]
    return out


def output_role(name: str) -> str:
    """Where a derived output goes in the DSS: criterion, model_only, target or extra."""
    if name == config.TARGET:
        return "target"
    if name in config.CRITERIA:
        return "criterion"
    return "model_only" if name in config.FEATURES else "extra"


def merge_summary(mapping: dict | None = None) -> pd.DataFrame:
    """One row per derived output: how many questions it merges, the rule, and its DSS role."""
    mapping = mapping or load_mapping()
    rows = []
    for name, items in output_items().items():
        added = [i for i in items if mapping["fields"][i].get("new_form")]
        rows.append({"output": name, "role": output_role(name), "questions": len(items),
                     "questions_original": len(items) - len(added), "merged": len(items) > 1,
                     "rule": MERGE_RULES[name], "fields": ", ".join(items)})
    return pd.DataFrame(rows).set_index("output")


def merge_table(mapping: dict | None = None, resolution: Resolution | None = None) -> pd.DataFrame:
    """One row per question that feeds a derived output. `resolution` adds the export's question text."""
    mapping = mapping or load_mapping()
    headers = resolution.columns if resolution else {}
    rows = []
    for name, items in output_items().items():
        for item in items:
            spec = mapping["fields"][item]
            levels = len(mapping["scales"][spec["scale"]]) if spec["kind"] == "scale" else None
            rows.append({"output": name, "role": output_role(name), "field": item,
                         "question": headers.get(item, ""), "kind": spec["kind"], "levels": levels,
                         "reversed": bool(spec.get("reverse")) or name == "financial_stress",
                         "form": "revised" if spec.get("new_form") else "both"})
    return pd.DataFrame(rows)


@dataclass
class Prepared:
    data: pd.DataFrame           # respondent_id index, features (+ target, extras); no PII
    resolution: Resolution
    report: dict
    form_version: pd.Series | None = None   # respondent_id -> "original" | "revised"


def _num(x, digits: int = 3):
    return None if x is None or pd.isna(x) else round(float(x), digits)


def cronbach_alpha(items: pd.DataFrame) -> dict:
    """Internal consistency of a composite, on the rows that answered every item."""
    full = items.dropna()
    k, n = items.shape[1], len(full)
    total = full.sum(axis=1).var(ddof=1) if n >= 3 else 0.0
    alpha = k / (k - 1) * (1 - full.var(ddof=1).sum() / total) if k >= 2 and total > 0 else None
    return {"alpha": _num(alpha), "items": k, "n": n}


def reliability(fields: pd.DataFrame, mapping: dict) -> dict:
    """Cronbach's alpha per composite; for composites that gained revised items, also the original set."""
    out = {}
    for name, items in COMPOSITES.items():
        present = [c for c in items if c in fields]
        if len(present) >= 2:
            out[name] = cronbach_alpha(item_units(fields, present, mapping))
        original = [c for c in present if not mapping["fields"][c].get("new_form")]
        if 2 <= len(original) < len(present):
            out[f"{name} (original items)"] = cronbach_alpha(item_units(fields, original, mapping))
    return out


def item_set_check(fields: pd.DataFrame, mapping: dict, revised: pd.Series) -> dict:
    """On revised rows: score from the original items vs from all items (are the two versions poolable?).

    r is their correlation; shift is the mean change, in the score's own units, that the
    revised items add. A high r and a small shift mean original and revised rows can be pooled.
    """
    out = {}
    rows = fields[revised]
    for name, items in COMPOSITES.items():
        added = [c for c in items if mapping["fields"][c].get("new_form") and c in fields]
        if not added or len(added) == len(items):
            continue
        full, base = composite(rows, name, mapping), composite(rows, name, mapping, original_only=True)
        ok = full.notna() & base.notna()
        span = 9 if name == "exam_pressure" else 10
        out[name] = {"n": int(ok.sum()),
                     "r": _num(full[ok].corr(base[ok])) if ok.sum() >= 3 else None,
                     "shift": _num(span * (full[ok] - base[ok]).mean()) if ok.any() else None}
    return out


def quality_report(raw: pd.DataFrame, fields: pd.DataFrame, derived: pd.DataFrame,
                   resolution: Resolution, mapping: dict, versions: pd.Series | None = None) -> dict:
    likert = [n for n, s in mapping["fields"].items() if s["kind"] == "scale" and n in fields]
    straight = int((fields[likert].nunique(axis=1) == 1).sum()) if len(likert) > 2 else 0
    versions = form_version(fields, mapping) if versions is None else versions
    above = {}
    for name in ("late_night", "late_tasks"):
        if name in fields:
            above[name] = int(fields[name].eq(len(mapping["scales"][mapping["fields"][name]["scale"]])).sum())
    answer_cols = [h for f, h in resolution.columns.items() if not mapping["fields"][f].get("pii")]
    unparsed = {}
    for name, header in resolution.columns.items():
        spec = mapping["fields"][name]
        if spec["kind"] == "text":
            continue
        given = raw[header].notna() & (raw[header].astype(str).str.strip() != "")
        bad = raw.loc[given & fields[name].isna(), header]
        if len(bad):
            unparsed[name] = {"count": int(len(bad)), "examples": sorted(map(str, bad.unique()))[:5]}
    return {
        "rows_raw": int(len(raw)),
        "rows_by_form_version": {v: int(n) for v, n in versions.value_counts().sort_index().items()},
        "duplicate_answer_rows": int(raw[answer_cols].duplicated().sum()) if answer_cols else 0,
        "straight_lining_rows": straight,
        "missing_per_feature": {c: int(derived[c].isna().sum()) for c in config.FEATURES},
        "missing_target": int(derived[config.TARGET].isna().sum()) if config.TARGET in derived else None,
        "answers_above_original_max": above,
        "reliability": reliability(fields, mapping),
        "item_set_check": item_set_check(fields, mapping, versions.eq("revised")),
        "unparsed_answers": unparsed,
        "pii_columns_dropped": [resolution.columns[f] for f, s in mapping["fields"].items()
                                if s.get("pii") and f in resolution.columns],
        "skipped_ambiguous_fields": resolution.skipped,
        "unused_columns": resolution.unused,
    }


def read_export(path_or_buffer) -> pd.DataFrame:
    name = str(getattr(path_or_buffer, "name", path_or_buffer)).lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(path_or_buffer, dtype=str)
    return pd.read_csv(path_or_buffer, dtype=str, keep_default_na=True)


def looks_like_gform(df: pd.DataFrame) -> bool:
    """True when the columns look like the questionnaire rather than the 11-column model CSV."""
    if set(config.FEATURES) <= set(df.columns):
        return False
    res = resolve_columns(df)
    return len(res.columns) >= len(CORE_FIELDS) // 2


def prepare(raw: pd.DataFrame, mapping: dict | None = None, reference_date=None,
            drop_duplicates: bool = True, strict: bool = True) -> Prepared:
    """Full export -> clean, anonymous frame. Raises ValueError if required columns are missing."""
    mapping = mapping or load_mapping()
    res = resolve_columns(raw, mapping)
    if strict and not res.ok:
        msg = []
        if res.missing:
            msg.append(f"missing fields: {res.missing}")
        if res.ambiguous:
            msg.append(f"ambiguous fields: {res.ambiguous}")
        raise ValueError("; ".join(msg) + ". Set 'header' in spk/gform_mapping.json "
                         "(run scripts/inspect_gform.py to see candidates).")
    fields = encode(raw, res, mapping)
    derived = derive(fields, reference_date, mapping)
    versions = form_version(fields, mapping)
    report = quality_report(raw, fields, derived, res, mapping, versions)

    keep = pd.Series(True, index=raw.index)
    if drop_duplicates:
        answer_cols = [h for f, h in res.columns.items() if not mapping["fields"][f].get("pii")]
        keep &= ~raw[answer_cols].duplicated()
    ids = [f"R{i + 1:04d}" for i in range(int(keep.sum()))]
    derived = derived[keep].set_axis(pd.Index(ids, name="respondent_id"))
    versions = versions[keep].set_axis(derived.index)
    report["rows_clean"] = int(len(derived))
    return Prepared(derived, res, report, versions)


def impute(df: pd.DataFrame, medians: dict) -> pd.DataFrame:
    """Fill missing model features with training medians (gender with its mode)."""
    out = df.copy()
    for c in config.FEATURES:
        if c in out and c in medians:
            out[c] = out[c].fillna(medians[c])
    return out


def feature_medians(df: pd.DataFrame) -> dict:
    med = {c: float(df[c].median()) for c in config.FEATURES if c != "gender"}
    med["gender"] = df["gender"].mode().iloc[0] if df["gender"].notna().any() else "Female"
    return med
