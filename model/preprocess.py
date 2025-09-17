from __future__ import annotations
"""
eurovision_preprocess.py

Preprocesses the raw Eurovision CSV into a clean Parquet dataset and a JSON
"features meta" describing which columns to use. Crucially, this script creates
a binary label TopK = 1[place <= K] controlled by --top-k, and stores both the
label name and the K value into the meta so downstream steps stay consistent.

Main responsibilities:
- Load CSV efficiently (two-pass to avoid loading lyrics twice).
- Remove rows without a known final placing.
- Create the TopK label based on --top-k.
- Drop leakage columns (anything that contains final/jury/televote “points” etc).
- Merge and normalize lyrics columns into a single 'lyrics_text' string.
- Engineer non-leaky features (within-year stats, country history, flags, lyrics stats).
- Identify numeric/categorical/text features, coerce & lightly impute.
- Save cleaned dataset (Parquet) and meta (JSON).
"""

import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# -----------------------
# Configuration defaults
# -----------------------
PREF_NUMERIC = ["bpm", "dancers", "running_order", "year"]
PREF_CATEGORICAL = ["country", "main_language", "tone", "broadcaster"]
STD_LYRICS_COL = "lyrics_text"
JOIN_KEYS_DEFAULT = ["year", "country", "song"]
LEAK_PATTERNS = [
    "jury", "televote", "points", "place_contest", "total_points",
    "grandfinal", "semi", "rank", "scoreboard"
]

# Minimal sentiment lexicon (tiny on purpose; avoids extra dependencies)
_POS_WORDS = {
    "love","lovely","beautiful","dream","dreams","dreaming","shine","light","lights",
    "smile","smiles","happy","happiness","hope","hopes","free","freedom","perfect",
    "strong","stronger","together","win","winner","victory","magic","miracle","peace"
}
_NEG_WORDS = {
    "cry","cries","tears","alone","lonely","dark","darkness","sad","sadness","pain",
    "hurt","hurts","broken","break","lost","loss","fear","afraid","fall","fallen",
    "goodbye","good-bye","good-byes","war","fight","fighting","die","dying"
}
_BIG5_ALIASES = {"fr","france","de","germany","it","italy","es","spain","uk","gb","united kingdom","great britain","england"}


# -----------------------
# Fast CSV helpers
# -----------------------
def read_csv_fast(path: Path, usecols: Optional[List[str]] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """Try fast PyArrow CSV; fall back to pandas C-engine if unavailable."""
    try:
        return pd.read_csv(path, engine="pyarrow", usecols=usecols, nrows=nrows)
    except Exception:
        return pd.read_csv(path, usecols=usecols, nrows=nrows, low_memory=False)

def list_csv_columns(path: Path) -> List[str]:
    """List column names without loading the whole file."""
    return list(read_csv_fast(path, nrows=0).columns)

def split_meta_vs_lyrics_cols(columns: List[str]) -> Tuple[List[str], List[str]]:
    """Split 'lyrics' columns from other metadata columns by name."""
    lyrics_cols = [c for c in columns if "lyrics" in c.lower()]
    meta_cols = [c for c in columns if c not in lyrics_cols]
    return meta_cols, lyrics_cols


# -----------------------
# Lyrics extraction
# -----------------------
def _looks_like_json(s: str) -> bool:
    s = str(s).strip()
    return (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}"))

def _safe_parse_maybe_json(x):
    """Parse a JSON/Python-like string to a Python object if possible; else return as-is."""
    if pd.isna(x):
        return x
    if isinstance(x, (list, dict)):
        return x
    s = str(x)
    if _looks_like_json(s):
        try:
            return json.loads(s)
        except Exception:
            try:
                return ast.literal_eval(s)
            except Exception:
                return x
    return x

def extract_lyrics_text_from_row(row: pd.Series, prefer_lang: str = "English") -> str:
    """
    Build a single text string from any available lyrics columns:
    1) Prefer a dedicated English column (lyrics_english / lyrics_en)
    2) Else, if a 'lyrics' column contains [{languages, content}], prefer English; else choose the longest.
    3) Else, take the longest textual lyrics column.
    """
    for cand in ["lyrics_english", "lyrics_en"]:
        if cand in row.index and isinstance(row[cand], str) and row[cand].strip():
            return row[cand]

    for cand in [c for c in row.index if "lyrics" in c.lower()]:
        val = _safe_parse_maybe_json(row[cand])
        if isinstance(val, list):
            eng = ""
            longest = ""
            for item in val:
                if not isinstance(item, dict):
                    continue
                content = (item.get("content") or "").strip()
                langs = item.get("languages", []) or []
                if any(isinstance(l, str) and prefer_lang.lower() in l.lower() for l in langs):
                    if len(content) > len(eng):
                        eng = content
                if len(content) > len(longest):
                    longest = content
            return eng if eng else longest
        elif isinstance(val, str) and val.strip():
            return val

    text_cands = [c for c in row.index if "lyrics" in c.lower()]
    texts = [str(row[c]) for c in text_cands if isinstance(row[c], str) and row[c].strip()]
    return max(texts, key=len) if texts else ""


# -----------------------
# Label, filtering & de-leakage
# -----------------------
def create_label_and_filter_finalists(df: pd.DataFrame, k: int) -> Tuple[pd.DataFrame, str]:
    """Keep rows with known 'place' and create TopK = 1[place <= K]. Return df and label name."""
    if "place" not in df.columns:
        raise KeyError("Expected a 'place' column to build the TopK label.")
    before = df.shape[0]
    df = df[~df["place"].isna()].copy()
    print(f"[finalists] kept rows with 'place': {df.shape[0]} (dropped {before - df.shape[0]})")

    df["place"] = pd.to_numeric(df["place"], errors="coerce")
    label_col = f"Top{int(k)}"
    df[label_col] = (df["place"].notna() & (df["place"] <= int(k))).astype(int)
    return df, label_col

def dedupe_entries(df: pd.DataFrame, keys: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Deduplicate by provided keys (e.g., year-country-song), keeping the best (lowest) place."""
    keys_present = [k for k in keys if k in df.columns]
    if len(keys_present) >= 2:
        df_sorted = df.sort_values(by=["place"] + keys_present, na_position="last", kind="mergesort")
        before = df_sorted.shape[0]
        df_out = df_sorted.drop_duplicates(subset=keys_present, keep="first").copy()
        print(f"[dedupe] on {keys_present}: {before} → {df_out.shape[0]} rows")
        return df_out, keys_present
    before = df.shape[0]
    df_out = df.drop_duplicates().copy()
    print(f"[dedupe] no standard keys; dropped exact dups: {before} → {df_out.shape[0]} rows")
    return df_out, []

def drop_leakage_columns(df: pd.DataFrame, patterns: List[str], protect: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Drop columns whose names suggest post-outcome info (points, televote etc.)."""
    leak_cols = [c for c in df.columns if any(p in c.lower() for p in patterns)]
    leak_cols = [c for c in leak_cols if c not in set(protect)]
    if leak_cols:
        df = df.drop(columns=leak_cols, errors="ignore").copy()
        print(f"[de-leak] dropped {len(leak_cols)} columns (e.g., {leak_cols[:8]}...)")
    else:
        print("[de-leak] none matched")
    return df, leak_cols


# -----------------------
# Feature engineering (non-leaky)
# -----------------------
def _to_lower_str(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower()

def add_within_year_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Add within-year stats such as normalized running order and BPM z-score."""
    engineered: List[str] = []
    if "year" not in df.columns:
        return df, engineered

    for col in ["running_order", "bpm", "year"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["n_finalists"] = df.groupby("year")["country"].transform("size")
    engineered.append("n_finalists")

    if "running_order" in df.columns:
        denom = df["n_finalists"].replace({0: np.nan})
        df["running_order_norm"] = df["running_order"] / denom
        df["late_slot_flag"] = (df["running_order_norm"] > 2/3).astype(int)
        engineered += ["running_order_norm", "late_slot_flag"]

        ro_mean = df.groupby("year")["running_order"].transform("mean")
        ro_std = df.groupby("year")["running_order"].transform("std").replace(0, np.nan)
        df["running_order_z_year"] = (df["running_order"] - ro_mean) / ro_std
        engineered.append("running_order_z_year")

    if "bpm" in df.columns:
        bpm_mean = df.groupby("year")["bpm"].transform("mean")
        bpm_std = df.groupby("year")["bpm"].transform("std").replace(0, np.nan)
        df["bpm_z_year"] = (df["bpm"] - bpm_mean) / bpm_std
        engineered.append("bpm_z_year")

    return df, engineered

def add_country_history_features(df: pd.DataFrame, window: int = 5, label_col: str = "Top3") -> Tuple[pd.DataFrame, List[str]]:
    """Add prior performance features shifted in time to avoid leakage."""
    engineered: List[str] = []
    if not {"country","year",label_col}.issubset(df.columns):
        return df, engineered

    df = df.sort_values(["country","year"]).copy()

    df["TopK_prev5"] = (
        df.groupby("country")[label_col]
          .transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
    )
    engineered.append("TopK_prev5")

    if "place" in df.columns:
        df["place"] = pd.to_numeric(df["place"], errors="coerce")
        df["place_prev1"] = df.groupby("country")["place"].shift(1)
        df["place_prev3_med"] = (
            df.groupby("country")["place"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).median())
        )
        df["place_prev1_minus_med3"] = df["place_prev1"] - df["place_prev3_med"]
        engineered += ["place_prev1","place_prev3_med","place_prev1_minus_med3"]

    return df, engineered

def add_flag_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Add Big-5 and host flags."""
    engineered: List[str] = []
    if "country" in df.columns:
        c = _to_lower_str(df["country"])
        df["is_big5"] = c.isin(_BIG5_ALIASES).astype(int)
        engineered.append("is_big5")

    host_col = next((c for c in ["host_country","host","hostCountry"] if c in df.columns), None)
    if host_col:
        df["is_host"] = (_to_lower_str(df["country"]) == _to_lower_str(df[host_col])).astype(int)
    else:
        df["is_host"] = 0
        print("[info] No host-country column found; 'is_host' set to 0 for all rows.")
    engineered.append("is_host")
    return df, engineered

_word_re = re.compile(r"[a-zA-Z]+")
def _basic_lyrics_stats(text: str):
    """Compute simple token and sentiment counts from lyrics_text."""
    s = str(text).lower()
    toks = _word_re.findall(s)
    n_tok = len(toks)
    if n_tok == 0:
        return 0, 0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0
    n_uniq = len(set(toks))
    ttr = n_uniq / n_tok
    uni_counts = Counter(toks)
    uni_top_share = max(uni_counts.values()) / n_tok
    bigrams = list(zip(toks, toks[1:]))
    n_bi = len(bigrams)
    bi_top_share = (Counter(bigrams).most_common(1)[0][1] / n_bi) if n_bi else 0.0
    pos_cnt = sum(1 for t in toks if t in _POS_WORDS)
    neg_cnt = sum(1 for t in toks if t in _NEG_WORDS)
    pos_rate = pos_cnt / n_tok
    neg_rate = neg_cnt / n_tok
    pos_minus_neg = pos_rate - neg_rate
    return n_tok, n_uniq, ttr, uni_top_share, bi_top_share, pos_cnt, neg_cnt, pos_rate, neg_rate, pos_minus_neg

def add_lyrics_stats(df: pd.DataFrame, col: str = STD_LYRICS_COL) -> Tuple[pd.DataFrame, List[str]]:
    """Add simple lyrics richness and sentiment proxy features."""
    engineered: List[str] = []
    if col not in df.columns:
        return df, engineered
    stats = df[col].apply(_basic_lyrics_stats)
    (df["lyrics_tok"],
     df["lyrics_uniq"],
     df["lyrics_ttr"],
     df["lyrics_uni_top_share"],
     df["lyrics_bi_top_share"],
     df["sent_pos_cnt"],
     df["sent_neg_cnt"],
     df["sent_pos_rate"],
     df["sent_neg_rate"],
     df["sent_pos_minus_neg"]) = zip(*stats)
    engineered += [
        "lyrics_tok","lyrics_uniq","lyrics_ttr","lyrics_uni_top_share","lyrics_bi_top_share",
        "sent_pos_cnt","sent_neg_cnt","sent_pos_rate","sent_neg_rate","sent_pos_minus_neg"
    ]
    return df, engineered


# -----------------------
# Feature lists & cleaning
# -----------------------
def identify_feature_lists(
    df: pd.DataFrame,
    label_col: str,
    pref_numeric: List[str] = PREF_NUMERIC,
    pref_categorical: List[str] = PREF_CATEGORICAL,
    text_col: str = STD_LYRICS_COL,
) -> Tuple[List[str], List[str], Optional[str], List[str]]:
    """Choose numeric/categorical/text features available in the data."""
    numeric_present = [c for c in pref_numeric if c in df.columns]
    categorical_present = [c for c in pref_categorical if c in df.columns]
    auto_numeric = [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in set(numeric_present + ["place", label_col])
    ]
    text_feature = text_col if (text_col in df.columns and (df[text_col].str.len() > 0).any()) else None
    print(f"[features] numeric: {len(numeric_present)+len(auto_numeric)} "
          f"(pref={len(numeric_present)}, auto={len(auto_numeric)}) | "
          f"categorical: {len(categorical_present)} | text: {bool(text_feature)}")
    return numeric_present + auto_numeric, categorical_present, text_feature, auto_numeric

def sanitize_numeric_features(df: pd.DataFrame, numeric_features: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Coerce candidate numeric columns to numeric; drop columns with no numeric values at all."""
    good = []
    for c in list(numeric_features):
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        non_numeric = len(df[c]) - s.notna().sum()
        if non_numeric > 0:
            print(f"[warn] '{c}': coerced {non_numeric} non-numeric values to NaN")
        if s.notna().sum() == 0:
            print(f"[drop] '{c}': no numeric values after coercion — removing from numeric_features")
            continue
        df[c] = s
        good.append(c)
    return df, good

def light_impute(df: pd.DataFrame, numeric_features: List[str], categorical_features: List[str]) -> pd.DataFrame:
    """Median-impute numeric features; fill NA categoricals with 'Unknown'."""
    for c in numeric_features:
        med = df[c].median(skipna=True)
        if pd.isna(med):
            med = 0.0
            print(f"[impute] '{c}': median is NaN, imputing 0.0")
        df[c] = df[c].fillna(med)
    for c in categorical_features:
        if c in df.columns and df[c].isna().any():
            df[c] = df[c].fillna("Unknown")
    return df

def save_artifacts(df: pd.DataFrame, features_meta: Dict, out_clean: Path, out_meta: Path) -> None:
    """Write cleaned Parquet and meta JSON to disk."""
    out_clean.parent.mkdir(parents=True, exist_ok=True)
    out_meta.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_clean, index=False)
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(features_meta, f, indent=2, ensure_ascii=False)
    print(f"[save] cleaned parquet → {out_clean}")
    print(f"[save] features meta → {out_meta}")


# -----------------------
# Orchestrator
# -----------------------
def prepare_dataset(
    input_path: Path,
    out_clean_path: Path,
    out_meta_path: Path,
    top_k: int = 3,
    two_pass: bool = True,
    skip_lyrics: bool = False,
    join_keys: List[str] = JOIN_KEYS_DEFAULT,
    leak_patterns: List[str] = LEAK_PATTERNS,
) -> Tuple[pd.DataFrame, Dict]:
    """
    End-to-end preprocessing with feature engineering and a TopK label.
    """
    all_cols = list_csv_columns(input_path)
    meta_cols, lyrics_cols = split_meta_vs_lyrics_cols(all_cols)

    if two_pass:
        print(f"[two-pass] meta columns: {len(meta_cols)}, lyrics columns: {len(lyrics_cols)}")
        df_meta = read_csv_fast(input_path, usecols=meta_cols)
    else:
        print("[one-pass] loading all columns at once")
        df_meta = read_csv_fast(input_path)

    # Label/filter, dedupe, de-leak on meta
    df, label_col = create_label_and_filter_finalists(df_meta, k=top_k)
    df, used_keys = dedupe_entries(df, keys=join_keys)
    df, dropped_leaks = drop_leakage_columns(df, patterns=leak_patterns, protect=["place", label_col])

    # Lyrics merge + unified text
    merged_lyrics_cols = []
    if not skip_lyrics:
        if two_pass:
            load_cols = sorted(set((lyrics_cols or []) + used_keys))
            if load_cols:
                df_lyrics = read_csv_fast(input_path, usecols=load_cols)
                for k in used_keys:
                    if k in df.columns and k in df_lyrics.columns and df[k].dtype != df_lyrics[k].dtype:
                        df_lyrics[k] = df_lyrics[k].astype(df[k].dtype, errors="ignore")
                df = df.merge(df_lyrics, on=used_keys, how="left", suffixes=("", "_lyr"))
                merged_lyrics_cols = [c for c in df.columns if "lyrics" in c.lower()]
                print(f"[two-pass] merged lyrics cols: {len(merged_lyrics_cols)}")
        df[STD_LYRICS_COL] = df.apply(extract_lyrics_text_from_row, axis=1).fillna("").astype(str)
        print(f"[lyrics] '{STD_LYRICS_COL}' non-empty rows: {(df[STD_LYRICS_COL].str.len() > 0).sum()}/{len(df)}")
    else:
        print("[lyrics] skipping lyrics as requested")
        df[STD_LYRICS_COL] = ""

    # Engineered features
    engineered_cols: List[str] = []
    df, feats = add_within_year_features(df); engineered_cols += feats
    df, feats = add_country_history_features(df, window=5, label_col=label_col); engineered_cols += feats
    df, feats = add_flag_features(df); engineered_cols += feats
    df, feats = add_lyrics_stats(df, col=STD_LYRICS_COL); engineered_cols += feats
    print(f"[engineer] added {len(engineered_cols)} features: {engineered_cols[:8]}{'...' if len(engineered_cols)>8 else ''}")

    # Feature lists + cleaning
    numeric_features, categorical_features, text_feature, _ = identify_feature_lists(df, label_col=label_col)
    df, numeric_features = sanitize_numeric_features(df, numeric_features)
    df = light_impute(df, numeric_features, categorical_features)

    features_meta = {
        "label": label_col,
        "top_k": int(top_k),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "text_feature": text_feature,
        "dedupe_keys_used": used_keys,
        "leak_patterns": leak_patterns,
        "leak_cols_dropped": dropped_leaks,
        "rows_after_clean": int(df.shape[0]),
        "cols_after_clean": int(df.shape[1]),
        "two_pass": bool(two_pass),
        "merged_lyrics_cols_count": int(len(merged_lyrics_cols)),
        "engineered_features": engineered_cols,
    }

    save_artifacts(df, features_meta, out_clean_path, out_meta_path)
    return df, features_meta


# -----------------------
# CLI
# -----------------------
def main():
    import argparse
    p = argparse.ArgumentParser(description="Preprocess Eurovision CSV into a clean dataset with a TopK label.")
    p.add_argument("--input", type=Path, required=True, help="Path to raw combined CSV.")
    p.add_argument("--out-clean", type=Path, default=Path("datasets/esc_clean.parquet"))
    p.add_argument("--out-meta", type=Path, default=Path("datasets/esc_features_meta.json"))
    p.add_argument("--top-k", type=int, default=3, help="Create label TopK = 1[place <= K].")
    p.add_argument("--no-two-pass", dest="two_pass", action="store_false", help="Disable two-pass CSV loading.")
    p.add_argument("--skip-lyrics", action="store_true", help="Skip reading/merging lyrics.")
    p.add_argument("--join-keys", type=str, default="year,country,song", help="Comma-separated join keys for lyrics merge.")
    args = p.parse_args()

    join_keys = [s.strip() for s in args.join_keys.split(",") if s.strip()]
    df, meta = prepare_dataset(
        input_path=args.input,
        out_clean_path=args.out_clean,
        out_meta_path=args.out_meta,
        top_k=args.top_k,
        two_pass=args.two_pass,
        skip_lyrics=args.skip_lyrics,
        join_keys=join_keys,
    )
    print(f"[done] label={meta['label']} top_k={meta['top_k']} rows={meta['rows_after_clean']}")

if __name__ == "__main__":
    main()
