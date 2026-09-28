"""Test the deployed model on NEW Google Form answers (collected after training).

    python scripts/evaluate.py --gform data/private/gform_new.csv

Compares the active model (real, if trained) with the Kaggle base model on the
new rows, overall and by gender. Prints aggregates only; nothing is saved
unless --out is given (keep that file under reports/private/).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from spk import config, gform, model  # noqa: E402


def evaluate(new: pd.DataFrame) -> dict:
    labeled = new.dropna(subset=[config.TARGET])
    out = {"rows": int(len(new)), "rows_with_target": int(len(labeled))}
    active, meta = model.load()
    base, base_meta = model.load_base()
    for label, (m, md) in {"active": (active, meta), "base_kaggle": (base, base_meta)}.items():
        X = gform.impute(labeled[config.FEATURES], md.get("impute_medians") or gform.feature_medians(labeled))
        pred = pd.Series(model.predict(m, X), index=labeled.index)
        res = {"model": md.get("strategy", "kaggle base"), **model.metrics(labeled[config.TARGET], pred)}
        by_gender = {}
        for g, idx in labeled.groupby("gender").groups.items():
            if len(idx) >= config.SUPPRESS_BELOW:
                by_gender[str(g)] = {"n": len(idx), **model.metrics(labeled.loc[idx, config.TARGET], pred.loc[idx])}
            else:
                by_gender[str(g)] = {"n": f"<{config.SUPPRESS_BELOW}"}
        res["by_gender"] = by_gender
        out[label] = res
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gform", required=True)
    p.add_argument("--out", help="write JSON result here (e.g. reports/private/eval_new.json)")
    args = p.parse_args()
    prepared = gform.prepare(gform.read_export(args.gform))
    if config.TARGET not in prepared.data:
        sys.exit("No Psikologis P01-P05 answers in this export, so there is nothing to score against.")
    result = evaluate(prepared.data)
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)


if __name__ == "__main__":
    main()
