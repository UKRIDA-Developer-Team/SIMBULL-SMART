"""Google Form export -> the 11 model features (+ anxiety_score target).

Pipeline:
    raw export --resolve_columns--> field columns --encode--> numeric codes
    --derive--> model features, target, extras (PII dropped)

The questionnaire (context.pdf) asks SMA students on Likert and range scales.
`derive` rescales those answers onto the ranges the Kaggle features use, so the
same Random Forest can be pretrained on Kaggle and retrained on real answers.
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

# Fields that feed the 11 model features (target items listed separately).
CORE_FIELDS = [
    "gender", "birth_date", "study_hours", "late_night", "time_insufficient", "late_tasks",
    "sleep_duration", "report_grade", "many_tasks", "exam_stress", "fear_parents",
    "family_demand", "exercise_days", "pocket_money", "time_split", "exhausted", "lost_interest",
]
TARGET_FIELDS = ["p1_nervous", "p2_worry", "p3_focus", "p4_distracted", "p5_hard_finish"]


def load_mapping(path: Path | str = MAPPING_PATH) -> dict:
    return json.loads(Path(path).read_text())


def norm(text) -> str:
    """Lowercase, unify dashes and whitespace so answers and headers compare reliably."""
    s = str(text).replace(" ", " ").replace("–", "-").replace("—", "-")
    s = re.sub(r"\s*-\s*", "-", s)
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


def scale_table(options: list[str]) -> dict:
    """Ordered option list -> {normalized text: 1..n}; bare digits '1'..'n' also accepted."""
    table = {norm(o): i + 1 for i, o in enumerate(options)}
    # A digit answer is ambiguous only when an option is itself a digit (late_tasks4).
    if not any(norm(o).isdigit() for o in options):
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
        if len(free) > 1:
            res.ambiguous[name] = free
        elif not fields[name].get("optional") and not fields[name].get("extra"):
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


def _mean_unit(fields: pd.DataFrame, cols: dict[str, int]) -> pd.Series:
    parts = pd.concat([_unit(fields[c], n) for c, n in cols.items() if c in fields], axis=1)
    return parts.mean(axis=1, skipna=True)


def age_from(fields: pd.DataFrame, reference_date=None) -> pd.Series:
    ref = fields["timestamp"] if "timestamp" in fields else pd.Series(pd.NaT, index=fields.index)
    fallback = pd.Timestamp(reference_date) if reference_date else pd.Timestamp.today().normalize()
    ref = ref.fillna(fallback)
    age = ((ref - fields["birth_date"]).dt.days / 365.25).apply(np.floor)
    return age.where(age.between(10, 40))


def derive(fields: pd.DataFrame, reference_date=None) -> pd.DataFrame:
    """Encoded fields -> model features on Kaggle-like scales, target, and x_ extras.

    Transformations (documented in the report and About page):
      exam_pressure      = 1 + (exam_stress - 1) * 9/4                      (1-5 -> 1-10)
      stress_level       = 10 * mean(unit(many_tasks), unit(time_insufficient),
                                     unit(late_tasks), unit(late_night))    (proxy, 0-10)
      financial_stress   = 10 * (5 - pocket_money) / 4                      (reversed, 0-10)
      family_expectation = 10 * mean(unit(fear_parents), unit(family_demand))
      burnout_score      = 10 * mean(unit(time_split), unit(exhausted), unit(lost_interest))
      anxiety_score      = sum(p - 1, p3 reversed) / 2                      (0-20 -> 0-10)
    """
    out = pd.DataFrame(index=fields.index)
    get = lambda c: fields[c] if c in fields else pd.Series(np.nan, index=fields.index)  # noqa: E731

    if "age" in fields:  # the in-app questionnaire asks age directly
        out["age"] = fields["age"]
    else:
        out["age"] = age_from(fields, reference_date)
    out["gender"] = get("gender")
    out["study_hours_per_day"] = get("study_hours")
    out["academic_performance"] = get("report_grade")
    out["exam_pressure"] = 1 + (get("exam_stress") - 1) * 9 / 4
    out["stress_level"] = 10 * _mean_unit(fields, {
        "many_tasks": 5, "time_insufficient": 4, "late_tasks": 4, "late_night": 4})
    out["sleep_hours"] = get("sleep_duration")
    out["physical_activity"] = get("exercise_days")
    out["financial_stress"] = 10 * (5 - get("pocket_money")) / 4
    out["family_expectation"] = 10 * _mean_unit(fields, {"fear_parents": 5, "family_demand": 5})
    out["burnout_score"] = 10 * _mean_unit(fields, {"time_split": 5, "exhausted": 5, "lost_interest": 5})
    out = out[config.FEATURES]

    if all(c in fields for c in TARGET_FIELDS):
        items = [(5 - fields[c]) if c == "p3_focus" else (fields[c] - 1) for c in TARGET_FIELDS]
        out[config.TARGET] = pd.concat(items, axis=1).sum(axis=1, min_count=len(items)) / 2

    mapping = load_mapping()
    for name, spec in mapping["fields"].items():
        if spec.get("extra") and name in fields:
            out[f"x_{name}"] = fields[name]
    return out


@dataclass
class Prepared:
    data: pd.DataFrame           # respondent_id index, features (+ target, extras); no PII
    resolution: Resolution
    report: dict


def quality_report(raw: pd.DataFrame, fields: pd.DataFrame, derived: pd.DataFrame,
                   resolution: Resolution, mapping: dict) -> dict:
    likert = [n for n, s in mapping["fields"].items() if s["kind"] == "scale" and n in fields]
    straight = int((fields[likert].nunique(axis=1) == 1).sum()) if len(likert) > 2 else 0
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
        "duplicate_answer_rows": int(raw[answer_cols].duplicated().sum()) if answer_cols else 0,
        "straight_lining_rows": straight,
        "missing_per_feature": {c: int(derived[c].isna().sum()) for c in config.FEATURES},
        "missing_target": int(derived[config.TARGET].isna().sum()) if config.TARGET in derived else None,
        "unparsed_answers": unparsed,
        "pii_columns_dropped": [resolution.columns[f] for f, s in mapping["fields"].items()
                                if s.get("pii") and f in resolution.columns],
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
    derived = derive(fields, reference_date)
    report = quality_report(raw, fields, derived, res, mapping)

    keep = pd.Series(True, index=raw.index)
    if drop_duplicates:
        answer_cols = [h for f, h in res.columns.items() if not mapping["fields"][f].get("pii")]
        keep &= ~raw[answer_cols].duplicated()
    derived = derived[keep].reset_index(drop=True)
    derived.index = [f"R{i + 1:04d}" for i in range(len(derived))]
    derived.index.name = "respondent_id"
    report["rows_clean"] = int(len(derived))
    return Prepared(derived, res, report)


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
