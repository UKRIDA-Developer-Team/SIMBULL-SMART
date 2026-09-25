# SPK SMART – Streamlit app

This app is the deployable version of `code/Copy of EskulSPK2026_SMART_Final.ipynb`. It predicts a student's `anxiety_score` with a Random Forest. It then uses the SMART method to rank how urgently each student needs attention and to recommend an intervention (Sleep, Exercise, Study, Counseling or Relaxation).

## Layout

```
app/
├── streamlit_app.py          # UI: single student / batch ranking / model tabs
├── spk/
│   ├── config.py             # features, criteria, benefit/cost types, weight profiles A/B/C
│   ├── data.py               # Kaggle download + sampling, gender encoding, CSV validation
│   ├── model.py              # RF train/evaluate/save/load
│   ├── smart.py              # utility normalization, SMART score, rank, recommendation
│   └── plots.py              # notebook charts as functions returning a Figure
├── scripts/train.py          # offline: builds data/ and models/
├── data/dataset.csv          # 20k-row sample (committed)
├── models/                   # rf_anxiety_model.joblib + metadata JSON (committed)
├── requirements.txt          # runtime deps (Streamlit Cloud installs this)
├── requirements-train.txt    # + kagglehub, for scripts/train.py only
└── .streamlit/config.toml
```

## Notebook to module map

| Notebook section | Where it lives now |
|---|---|
| Mount Drive, `kagglehub` download, 2% sample | `spk/data.py::download_sample`, `scripts/train.py` |
| `LabelEncoder` on gender | `config.GENDER_MAP` (fixed mapping `Female=0, Male=1, Other=2`) |
| ML (RF) train + metrics + `joblib.dump` | `spk/model.py`, `scripts/train.py` |
| SMART utility, score, rank | `spk/smart.py` |
| Weight A / B / C, recommendations | `config.WEIGHTS_*`, `smart.alternative_scores`, `smart.best_alternative` |
| Visualisations | `spk/plots.py` |

## Run locally

```bash
cd app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-train.txt
python scripts/train.py            # downloads about 131 MB from Kaggle, writes data/ + models/
streamlit run streamlit_app.py
```

If you already have `dataset.csv` from Google Drive, run `python scripts/train.py --csv path/to/dataset.csv` to skip the download.

## Deploy to Streamlit Community Cloud

1. Commit `app/data/dataset.csv` and `app/models/*` (about 6 MB and 5 MB). The Cloud does not run training.
2. Push the repo to GitHub.
3. On share.streamlit.io, click New app, then pick the repo, branch `main`, and main file `app/streamlit_app.py`.
4. Under Advanced settings, pick Python 3.12 or newer. The app needs no secrets.

## Things that changed vs the notebook

- **Retrain with the pinned versions.** Joblib pickles are tied to the scikit-learn version, so the Colab `.joblib` may fail to load on the Cloud. `scripts/train.py` rebuilds the model with the versions in `requirements.txt`. The metrics match the notebook: MAE 0.7668, RMSE 0.9546, R² 0.6136.
- **Reference bounds for SMART.** The notebook normalizes with the min and max of the whole dataset. A single student has no such range, so training saves the dataset bounds in the metadata (`smart_bounds`). The single-student view uses those bounds. The batch view can use either the bounds or the min/max of the batch itself.
- **Weight C** gives equal weights, so all alternatives tie and `idxmax` always returns "Sleep". The app keeps it as a control and shows a warning.
- **Notebook bug:** cell 62 uses `criteria_plot`, which is never defined. `plots.correlation_heatmap` uses `CRITERIA` instead.
- **Student IDs** are `STU00001…` in row order, as in the notebook.
