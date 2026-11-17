"""Synthetic end-to-end: export -> prepare -> retrain experiment -> assess."""
import pandas as pd
import pytest

from spk import config, data, gform, model, recommend, retrain
import make_synthetic_gform


def test_real_retrain_end_to_end(monkeypatch):
    monkeypatch.setattr(retrain, "STRATEGIES", {k: retrain.STRATEGIES[k]
                                                for k in ("S0_kaggle", "S1_real", "S2_combined_w10", "S3_warm_200")})
    export = make_synthetic_gform.generate(n=80, seed=11)
    prepared = gform.prepare(pd.read_csv(pd.io.common.StringIO(export.to_csv(index=False)), dtype=str))
    base, base_meta = model.load_base()
    final, meta, summary = retrain.run(prepared.data, data.load_retrain_rows(), base, base_meta,
                                       prepared.report, log=lambda *_: None, strata=prepared.form_version)
    assert summary["selected"] in retrain.STRATEGIES
    # both questionnaire versions reach the holdout, and the extended model ran despite empty extras
    assert set(summary["holdout_by_form_version"]) == {"original", "revised"}
    assert retrain.REPORT_ONLY in summary["strategies"]
    assert summary["quality"]["rows_by_form_version"]["revised"] > 0
    assert set(meta["reference_quantiles"]) == {"rf_anxiety_score", "smart_score"}
    assert "R0001" not in str(summary)          # no row identifiers in the committed summary
    a = recommend.assess(final, meta, prepared.data.iloc[0][config.FEATURES],
                         config.WEIGHTS_B, meta["reference_quantiles"])
    assert a.best in config.ALTERNATIVES
