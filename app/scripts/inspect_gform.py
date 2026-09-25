"""Check a Google Form export against spk/gform_mapping.json before training.

    python scripts/inspect_gform.py data/private/gform_raw.csv

Prints which column each field resolved to, fields that are missing or
ambiguous, columns nothing uses, answers that could not be parsed, and a
summary of the derived model features. Nothing is written unless --clean is set,
and the clean file keeps no personal columns.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spk import config, gform  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("export", help="Google Form export (.csv or .xlsx)")
    p.add_argument("--clean", help="write the anonymous, derived frame to this CSV")
    args = p.parse_args()

    raw = gform.read_export(args.export)
    mapping = gform.load_mapping()
    res = gform.resolve_columns(raw, mapping)
    print(f"Rows: {len(raw)}  Columns: {raw.shape[1]}\n")

    print("Resolved fields:")
    for name in mapping["fields"]:
        spec = mapping["fields"][name]
        tag = "PII " if spec.get("pii") else ("TGT " if spec.get("target") else ("xtra" if spec.get("extra") else "core"))
        header = res.columns.get(name, "-")
        print(f"  [{tag}] {name:18s} <- {header}")

    if res.missing:
        print("\nMISSING required fields (set 'header' for them in spk/gform_mapping.json):")
        for name in res.missing:
            print(f"  {name}: match={mapping['fields'][name]['match']}")
    if res.ambiguous:
        print("\nAMBIGUOUS fields (several columns fit; set 'header'):")
        for name, cands in res.ambiguous.items():
            print(f"  {name}: {cands}")
    if res.unused:
        print("\nColumns no field uses:")
        for h in res.unused:
            print(f"  {h}")

    if not res.ok:
        sys.exit(1)

    prepared = gform.prepare(raw, mapping)
    print("\nQuality report:")
    print(json.dumps(prepared.report, indent=2, ensure_ascii=False, default=str))
    cols = config.FEATURES + ([config.TARGET] if config.TARGET in prepared.data else [])
    print("\nDerived model features:")
    print(prepared.data[cols].describe().T[["count", "mean", "min", "max"]].round(2).to_string())

    if args.clean:
        prepared.data.to_csv(args.clean)
        print(f"\nClean (no PII) -> {args.clean}")


if __name__ == "__main__":
    main()
