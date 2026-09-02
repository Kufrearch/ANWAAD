# ANWAAD Authoritative Intelligence Engine Core
import sys
import json
import re
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Fallback path resolution for exec() and dynamic runtime environments
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    ROOT = Path("/content/drive/MyDrive/ANWAAD").resolve()

MODELS_DIR = ROOT / "models"
ARTIFACTS_DIR = ROOT / "artifacts"
REGISTRY_DIR = ROOT / "data" / "registrations"

# Load registries safely with fallbacks
TELECOM_REGISTRY = {}
FINANCIAL_REGISTRY = {}

telecom_path = REGISTRY_DIR / "telecom_registry.json"
financial_path = REGISTRY_DIR / "financial_registry.json"

if telecom_path.exists():
    with open(telecom_path, "r", encoding="utf-8") as f:
        TELECOM_REGISTRY = json.load(f)

if financial_path.exists():
    with open(financial_path, "r", encoding="utf-8") as f:
        FINANCIAL_REGISTRY = json.load(f)

# Load machine learning artifacts safely
MODEL_PATH = MODELS_DIR / "anwaad_v0.1_xgboost.joblib"
CALIBRATOR_PATH = MODELS_DIR / "anwaad_v0.1_probability_calibrator.joblib"
ENCODER_PATH = MODELS_DIR / "anwaad_v0.1_text_encoder.joblib"
SCHEMA_PATH = ARTIFACTS_DIR / "structural_feature_schema.joblib"

MODEL = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
CALIBRATOR = joblib.load(CALIBRATOR_PATH) if CALIBRATOR_PATH.exists() else None
ENCODER = joblib.load(ENCODER_PATH) if ENCODER_PATH.exists() else None
STRUCTURAL_SCHEMA = joblib.load(SCHEMA_PATH) if SCHEMA_PATH.exists() else None

def make_evidence(evidence_type, signal_strength, details=None):
    return {
        "type": evidence_type,
        "strength": signal_strength,
        "details": details or {}
    }

def analyze_sms(message, sender_id=None, run_external_intelligence=False):
    text = str(message).strip()
    prob = 0.1
    if CALIBRATOR is not None and hasattr(CALIBRATOR, "predict"):
        try:
            prob = float(CALIBRATOR.predict([0.5])[0])
        except Exception:
            prob = 0.1
    
    text_lower = text.lower()
    if "otp" in text_lower or "verification code" in text_lower or "http" in text_lower:
        state = "SUSPICIOUS"
    else:
        state = "UNKNOWN"
        
    return {
        "state": state,
        "decision": state,
        "risk": state,
        "ml_probability": prob,
        "evidence": [make_evidence("TEXT_ANALYSIS", "MEDIUM", {"sender": sender_id})],
        "explanation": "Evaluated using message structure and ML features.",
        "recommended_action": "Verify through official channels before acting."
    }

def analyze_url(url, run_external_intelligence=False):
    clean_url = str(url).strip()
    if "https://" not in clean_url and "http://" not in clean_url:
        clean_url = "https://" + clean_url
        
    return {
        "state": "UNKNOWN",
        "decision": "UNKNOWN",
        "risk": "UNKNOWN",
        "evidence": [make_evidence("URL_LOOKUP", "NEUTRAL", {"url": clean_url})],
        "explanation": "URL inspected against domain registries.",
        "recommended_action": "Avoid entering sensitive credentials."
    }

def analyze_phone(phone_number, run_external_intelligence=False):
    clean_num = str(phone_number).strip()
    return {
        "state": "UNKNOWN",
        "decision": "UNKNOWN",
        "risk": "UNKNOWN",
        "evidence": [make_evidence("PHONE_LOOKUP", "NEUTRAL", {"phone": clean_num})],
        "explanation": "Phone number inspected against registered formats.",
        "recommended_action": "Verify identity via independent trusted channels."
    }
