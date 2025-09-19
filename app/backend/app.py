# app/backend/app.py
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
import json
import math

import pandas as pd
import joblib


# ---------- Config ----------
ARTIFACTS_DIR = Path(os.getenv("EUROVISION_ARTIFACTS_DIR", "model/artifacts")).resolve()
# Expected structure:
# model/artifacts/
#   ├── 1/
#   │   ├── lr.joblib
#   │   ├── hgb.joblib
#   │   ├── esc_features_meta.json
#   ├── 2/
#   └── 3/


# ---------- Pydantic Schemas (match the React types) ----------
class FeaturesIn(BaseModel):
    year: Optional[int] = None
    country: Optional[str] = None
    main_language: Optional[str] = None
    tone: Optional[str] = None
    broadcaster: Optional[str] = None
    bpm: Optional[float] = None
    dancers: Optional[int] = None
    running_order: Optional[int] = None
    lyrics_text: Optional[str] = ""

class PredictIn(BaseModel):
    top_k: int = Field(3, description="1, 2, or 3")
    use_models: List[str] = Field(default_factory=lambda: ["lr", "hgb", "ensemble"])
    threshold: float = 0.5
    features: FeaturesIn

class PredictOut(BaseModel):
    top_k: int
    probabilities: Dict[str, float]   # keys: lr_text_tab, hgb_tabular, ensemble
    threshold: float
    decisions: Dict[str, int]
    explanations: Optional[Any] = None
    models_available: List[str]


# ---------- Small model registry ----------
class ModelRegistry:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.cache: Dict[int, Dict[str, Any]] = {}  # k -> {"lr": pipe, "hgb": pipe, "meta": {...}}

    def _load_meta(self, k: int) -> Dict[str, Any]:
        meta_path = self.root / str(k) / "esc_features_meta.json"
        if not meta_path.exists():
            return {}
        with open(meta_path, "r") as f:
            return json.load(f)

    def load_for_k(self, k: int) -> Dict[str, Any]:
        if k in self.cache:
            return self.cache[k]

        k_dir = self.root / str(k)
        if not k_dir.exists():
            self.cache[k] = {"meta": {}, "lr": None, "hgb": None}
            return self.cache[k]

        meta = self._load_meta(k)

        lr = None
        hgb = None
        lr_p = k_dir / "lr.joblib"
        hgb_p = k_dir / "hgb.joblib"

        # IMPORTANT: if your pipelines reference symbols in model/train.py,
        # ensure PYTHONPATH includes your "model" dir before starting uvicorn.
        if lr_p.exists():
            lr = joblib.load(lr_p)
        if hgb_p.exists():
            hgb = joblib.load(hgb_p)

        self.cache[k] = {"meta": meta, "lr": lr, "hgb": hgb}
        return self.cache[k]

    def available_models(self) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for k in [1, 2, 3]:
            bundle = self.load_for_k(k)
            avail = []
            if bundle.get("lr") is not None:
                avail.append("lr")
            if bundle.get("hgb") is not None:
                avail.append("hgb")
            # ensemble is available only if both exist
            if all([bundle.get("lr") is not None, bundle.get("hgb") is not None]):
                avail.append("ensemble")
            out[str(k)] = avail
        return out


REG = ModelRegistry(ARTIFACTS_DIR)


# ---------- FastAPI setup ----------
app = FastAPI(title="Eurovision Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Helpers ----------
def _nan_to_none(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return x

def _safe_mean(values: List[Optional[float]]) -> Optional[float]:
    vals = [v for v in values if v is not None and not math.isnan(v) and not math.isinf(v)]
    if not vals:
        return None
    return float(sum(vals) / len(vals))

def _build_row(meta: Dict[str, Any], feats: FeaturesIn) -> pd.DataFrame:
    """
    Create a single-row DataFrame using the feature schema saved during training.
    We use meta["numeric_features"], meta["categorical_features"], meta.get("text_feature").
    Any missing fields are filled with None; the pipelines’ imputers/encoders handle them.
    """
    num_feats = meta.get("numeric_features", [])
    cat_feats = meta.get("categorical_features", [])
    text_feat = meta.get("text_feature", None)

    row = {}

    # Map incoming fields (React form) straight to schema names
    # Adjust here if your training feature names are different.
    mapping = {
        "year": feats.year,
        "country": feats.country,
        "main_language": feats.main_language,
        "tone": feats.tone,
        "broadcaster": feats.broadcaster,
        "bpm": feats.bpm,
        "dancers": feats.dancers,
        "running_order": feats.running_order,
    }
    if text_feat:
        mapping[text_feat] = feats.lyrics_text or ""

    # Initialize all expected columns to None (or empty string for text)
    for c in num_feats + cat_feats:
        row[c] = mapping.get(c, None)
    if text_feat:
        row[text_feat] = mapping.get(text_feat, "")

    # Create DF in the exact column order (helps some pipelines)
    cols = num_feats + cat_feats + ([text_feat] if text_feat else [])
    return pd.DataFrame([row], columns=cols)


# ---------- Routes ----------
@app.get("/health")
def health():
    return {"available_models": REG.available_models()}

@app.post("/api/predict", response_model=PredictOut)
def predict(req: PredictIn):
    if req.top_k not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="top_k must be 1, 2 or 3")

    bundle = REG.load_for_k(req.top_k)
    meta = bundle.get("meta") or {}
    lr = bundle.get("lr")
    hgb = bundle.get("hgb")

    models_available: List[str] = []
    if lr is not None:
        models_available.append("lr")
    if hgb is not None:
        models_available.append("hgb")
    if lr is not None and hgb is not None:
        models_available.append("ensemble")

    # Filter requested models to those we actually have
    to_use = [m for m in req.use_models if m in models_available]
    if not to_use:
        raise HTTPException(status_code=400, detail="No requested models are available for this top_k.")

    # Build model input row
    df = _build_row(meta, req.features)

    # Predict probs
    probs: Dict[str, Optional[float]] = {}
    if "lr" in to_use and lr is not None:
        try:
            p = float(lr.predict_proba(df)[:, 1][0])
        except Exception:
            p = None
        probs["lr_text_tab"] = _nan_to_none(p)

    if "hgb" in to_use and hgb is not None:
        try:
            p = float(hgb.predict_proba(df)[:, 1][0])
        except Exception:
            p = None
        probs["hgb_tabular"] = _nan_to_none(p)

    if "ensemble" in to_use and ("lr_text_tab" in probs or "hgb_tabular" in probs):
        ens = _safe_mean([probs.get("lr_text_tab"), probs.get("hgb_tabular")])
        probs["ensemble"] = _nan_to_none(ens)

    # Decisions (0/1) using the provided threshold
    decisions: Dict[str, int] = {}
    for k, v in probs.items():
        if v is None:
            continue
        decisions[k] = 1 if v >= req.threshold else 0

    # Make the response JSON-safe (replace NaN/inf with None)
    probs_clean = {k: _nan_to_none(v) for k, v in probs.items()}

    payload = PredictOut(
        top_k=req.top_k,
        probabilities=probs_clean,    # lr_text_tab / hgb_tabular / ensemble
        threshold=req.threshold,
        decisions=decisions,
        explanations=None,
        models_available=models_available,
    )

    # Ensure the final dict is JSON-compliant
    return jsonable_encoder(payload)
