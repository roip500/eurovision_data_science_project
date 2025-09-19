from __future__ import annotations
"""
eurovision_pipeline.py

Single entrypoint: preprocess → train/eval, with one --top-k that propagates.
Saves CV metrics/preds and (optionally) final .joblib models in artifacts/<K>/.
"""

from pathlib import Path
import argparse

from preprocess import prepare_dataset
from train import (
    load_data,
    build_X_y_groups,
    build_lr_pipeline,
    build_hgb_pipeline,
    evaluate_models_cv,
    fit_and_save_final,   # <-- ensure this exists in train.py
)

def main():
    p = argparse.ArgumentParser(description="End-to-end Eurovision pipeline (preprocess → train/eval) with Top-K control.")
    p.add_argument("--input", type=Path, default=Path("datasets/final_merged.csv"), help="Raw CSV path.")
    p.add_argument("--top-k", type=int, default=2, help="Create label TopK = 1[place <= K].")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="Output directory (defaults to model/artifacts/<K>).")
    p.add_argument("--cv-splits", type=int, default=5, help="GroupKFold splits by year.")
    p.add_argument("--run", choices=["lr", "hgb", "both"], default="both", help="Which model(s) to run.")
    p.add_argument("--ensemble", action="store_true", default=True,
                   help="Also compute/save simple mean ensemble if both models are present.")
    p.add_argument("--tfidf-max-features", type=int, default=10000, help="TF-IDF vocab size for LR.")
    p.add_argument("--fit-final", action="store_true", default=False,
                   help="Fit final model(s) on all data and save .joblib to artifacts/<K>/")
    args = p.parse_args()

    # Resolve output dir (match backend expectation)
    out_dir = args.out_dir or Path(f"model/artifacts/{args.top_k}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_clean = out_dir / "esc_clean.parquet"
    out_meta  = out_dir / "esc_features_meta.json"

    # 1) Preprocess with the given K
    _, meta = prepare_dataset(
        input_path=args.input,
        out_clean_path=out_clean,
        out_meta_path=out_meta,
        top_k=args.top_k,
        two_pass=True,
        skip_lyrics=False,
        join_keys=["year", "country", "song"],
    )
    print(f"[pipeline] Preprocessing done. Label={meta['label']}")

    # 2) Train/Eval (use K from meta to ensure consistency)
    df, meta2 = load_data(out_clean, out_meta)
    X, y, groups, ids, used_k = build_X_y_groups(df, meta2, top_k_override=None)

    num_features = meta2["numeric_features"]
    cat_features = meta2["categorical_features"]
    text_feature = meta2.get("text_feature")

    pipes = {}
    if args.run in ("lr", "both"):
        pipes["lr"] = build_lr_pipeline(
            num_features, cat_features, text_feature, tfidf_max_features=args.tfidf_max_features
        )
    if args.run in ("hgb", "both"):
        pipes["hgb"] = build_hgb_pipeline(num_features, cat_features)

    results = evaluate_models_cv(
        X, y, groups, ids, pipes,
        n_splits=args.cv_splits,
        hits_k=used_k,          # make sure train.evaluate_models_cv accepts this
        ensemble=args.ensemble,
        out_dir=out_dir,        # writes cv_metrics.json & cv_predictions.csv into artifacts/<K>/
    )

    print("\n=== Aggregate CV metrics ===")
    for name, m in results["metrics_agg"].items():
        hits_key = f"Hits@{used_k}_mean"
        print(f"{name:12s}  AUROC={m['AUROC_mean']:.3f} | AP={m['AP_mean']:.3f} | "
              f"F1+= {m['F1_pos_mean']:.3f} | {hits_key}={m[hits_key]:.2f} (folds={m['folds']})")

    # 3) (Optional) Fit-final & save .joblib for the backend
    if args.fit_final:
        fit_and_save_final(X, y, pipes, out_dir, ensemble=args.ensemble)
        print(f"[pipeline] Saved final model(s) to: {out_dir.resolve()}")

    print("[pipeline] Done.")

if __name__ == "__main__":
    main()
