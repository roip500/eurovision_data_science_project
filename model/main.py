from __future__ import annotations
"""
eurovision_pipeline.py

Single entrypoint that runs: preprocess → train/evaluate, with ONE --top-k setting
that propagates through the entire process.
"""

from pathlib import Path
import argparse

from preprocess import prepare_dataset
from train import (
    load_data, build_X_y_groups, build_lr_pipeline, build_hgb_pipeline, evaluate_models_cv
)


def main():
    p = argparse.ArgumentParser(description="End-to-end Eurovision pipeline (preprocess → train/eval) with Top-K control.")
    p.add_argument("--input", type=Path, help="Raw CSV path.",default='datasets/final_merged_1.csv')
    p.add_argument("--out-dir", type=Path, default=Path("model/artifacts"), help="Output directory.")
    p.add_argument("--top-k", type=int, default=2, help="Create and evaluate label TopK = 1[place<=K].")
    p.add_argument("--cv-splits", type=int, default=5, help="GroupKFold splits by year.")
    p.add_argument("--run", choices=["lr", "hgb", "both"], default="both", help="Which model(s) to run.")
    p.add_argument("--ensemble", action="store_true", default=True, help="Also compute simple mean ensemble.")
    p.add_argument("--tfidf-max-features", type=int, default=10000, help="TF-IDF vocab size for LR.")
    args = p.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_clean = out_dir / "esc_clean.parquet"
    out_meta = out_dir / "esc_features_meta.json"

    # 1) Preprocess with the given K
    _, meta = prepare_dataset(
        input_path=args.input,
        out_clean_path=out_clean,
        out_meta_path=out_meta,
        top_k=args.top_k,
        two_pass=True,
        skip_lyrics=False,
        join_keys=["year","country","song"],
    )
    print(f"[pipeline] Preprocessing done. Label={meta['label']}")

    # 2) Train/Eval (use K from meta to ensure total consistency)
    df, meta2 = load_data(out_clean, out_meta)
    X, y, groups, ids, used_k = build_X_y_groups(df, meta2, top_k_override=None)

    num_features = meta2["numeric_features"]
    cat_features = meta2["categorical_features"]
    text_feature = meta2.get("text_feature")

    pipes = {}
    if args.run in ("lr","both"):
        pipes["lr_text_tab"] = build_lr_pipeline(
            num_features, cat_features, text_feature, tfidf_max_features=args.tfidf_max_features
        )
    if args.run in ("hgb","both"):
        pipes["hgb_tabular"] = build_hgb_pipeline(num_features, cat_features)

    results = evaluate_models_cv(
        X, y, groups, ids, pipes,
        n_splits=args.cv_splits, hits_k=used_k,
        ensemble=args.ensemble, out_dir=out_dir
    )

    print("\n=== Aggregate CV metrics ===")
    for name, m in results["metrics_agg"].items():
        print(
            f"{name:12s}  AUROC={m['AUROC_mean']:.3f} | AP={m['AP_mean']:.3f} | "
            f"F1+= {m['F1_pos_mean']:.3f} | Hits@{used_k}={m[f'Hits@{used_k}_mean']:.2f} (folds={m['folds']})"
        )
    print("[pipeline] Done.")

if __name__ == "__main__":
    main()
