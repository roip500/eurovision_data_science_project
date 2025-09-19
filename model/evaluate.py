from __future__ import annotations
"""
eurovision_eval.py

Standalone evaluator that reads cv_predictions.csv + meta and recomputes metrics
for a chosen model column (lr_text_tab, hgb_tabular, or ensemble). It uses K from
meta by default, or a user-specified --top-k override.

Usage example:
    python eurovision_eval.py --preds artifacts/cv_predictions.csv \
        --meta artifacts/esc_features_meta.json --model ensemble
"""

import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score


def evaluate_from_predictions(preds_csv: Path, meta_json: Path, model: str, top_k: int | None = None) -> Dict:
    """
    Compute AUROC, AP, F1@0.5, and Hits@K per-year and on average from saved predictions.
    """
    preds = pd.read_csv(preds_csv)
    with open(meta_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    k = int(top_k if top_k is not None else meta.get("top_k", 3))
    proba_col = f"proba_{model}"
    required = {"year", "y_true", proba_col}
    missing = required - set(preds.columns)
    if missing:
        raise KeyError(f"Missing columns in preds: {missing}")

    y_true = preds["y_true"].to_numpy()
    y_proba = preds[proba_col].to_numpy()
    years = preds["year"].to_numpy()

    # Standard metrics
    try:
        auroc = float(roc_auc_score(y_true, y_proba))
    except ValueError:
        auroc = float("nan")
    ap = float(average_precision_score(y_true, y_proba))
    f1p = float(f1_score(y_true, (y_proba >= 0.5).astype(int), pos_label=1))

    # Hits@K per year
    per_year = []
    df_tmp = pd.DataFrame({"year": years, "y_true": y_true, "proba": y_proba})
    for yr, grp in df_tmp.groupby("year"):
        grp = grp.sort_values("proba", ascending=False)
        kk = min(k, len(grp))
        hits = int(grp.head(kk)["y_true"].sum())
        per_year.append({"year": int(yr), "hits": hits, "k": int(kk)})
    hits_mean = float(np.mean([r["hits"] for r in per_year])) if per_year else 0.0

    out = {
        "model": model,
        "top_k": k,
        "AUROC": auroc,
        "AP": ap,
        "F1_pos": f1p,
        f"Hits@{k}_mean": hits_mean,
        "per_year": per_year,
        "n_rows": int(len(preds)),
    }
    return out


def main():
    import argparse
    p = argparse.ArgumentParser(description="Evaluate saved CV predictions for a chosen model column.")
    p.add_argument("--preds", type=Path, default=Path("artifacts/3/cv_predictions.csv"))
    p.add_argument("--meta", type=Path, default=Path("artifacts/3/esc_features_meta.json"))
    p.add_argument("--model", choices=["lr_text_tab", "hgb_tabular", "ensemble"], default="ensemble")
    p.add_argument("--top-k", type=int, default=None, help="Override K for Hits@K; default is meta['top_k'].")
    args = p.parse_args()

    res = evaluate_from_predictions(args.preds, args.meta, args.model, top_k=args.top_k)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
