import os
import joblib
import pandas as pd

# Path to models directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

# Load all models into memory (indexed by cube ID)
model_files = {
    0: "traffic_rf.pkl",        # E-Commerce
    1: "traffic_xgb.pkl",       # Education
    2: "traffic_logistic.pkl",  # Govt
    3: "traffic_iso.pkl"        # Finance
}

models = {}
for cube_id, filename in model_files.items():
    path = os.path.join(MODEL_DIR, filename)
    try:
        models[cube_id] = joblib.load(path)
        print(f"✅ Loaded model {filename} for cube {cube_id}")
    except Exception as e:
        print(f"⚠️ Could not load model {filename} for cube {cube_id}: {e}")

# Feature extractor
def extract_features(event: dict) -> pd.DataFrame:
    return pd.DataFrame([{
        "url_len": len(event.get("url", "")),
        "dwell_ms": event.get("dwell_ms", 0),
        "has_bot_ua": 1 if "bot" in event.get("user_agent", "").lower() else 0
    }])

# Classify event using appropriate model
def classify_event(event: dict, cube_id: int) -> str:
    model = models.get(cube_id % len(models))
    try:
        features = extract_features(event)
        # IsolationForest (unsupervised)
        if model.__class__.__name__ == "IsolationForest":
            pred = model.predict(features)[0]
            if pred == -1:
                # Anomaly: try to distinguish bot type
                ua = event.get("user_agent", "").lower()
                if "mimic" in ua:
                    return "mimic_bot"
                elif "stealth" in ua:
                    return "stealth_bot"
                elif "bot" in ua:
                    return "naive_bot"
                else:
                    return "bot"
            else:
                return "human"
        else:
            pred = model.predict(features)[0]
            if pred == 1:
                # Bot detected, try to distinguish type
                ua = event.get("user_agent", "").lower()
                if "mimic" in ua:
                    return "mimic_bot"
                elif "stealth" in ua:
                    return "stealth_bot"
                elif "bot" in ua:
                    return "naive_bot"
                else:
                    return "bot"
            else:
                return "human"
    except Exception as e:
        print(f"⚠️ Model prediction failed for cube {cube_id}: {e}")
        ua = event.get("user_agent", "").lower()
        if "mimic" in ua:
            return "mimic_bot"
        elif "stealth" in ua:
            return "stealth_bot"
        elif "bot" in ua:
            return "naive_bot"
        else:
            return "human"
