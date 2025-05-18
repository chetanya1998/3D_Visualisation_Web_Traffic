import pandas as pd
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import joblib

# Paths
LOG_FILE = Path(__file__).parent / "access.log"
MODEL_DIR = Path(__file__).parent.parent / "backend" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Load logs and parse JSON lines
def load_log_data():
    if not LOG_FILE.exists():
        raise FileNotFoundError("access.log not found.")
    
    with open(LOG_FILE) as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines if line.strip()]

def extract_features(data):
    return pd.DataFrame([{
        "url_len": len(entry.get("url", "")),
        "dwell_ms": entry.get("dwell_ms", 0),
        "has_bot_ua": 1 if "bot" in entry.get("user_agent", "").lower() else 0,
        "label": 1 if entry.get("true_label", "") != "human" else 0
    } for entry in data])

def train_and_save_models(df):
    X = df[["url_len", "dwell_ms", "has_bot_ua"]]
    y = df["label"]

    # Check for at least two classes
    if len(set(y)) < 2:
        print(f"❌ Not enough classes in data to train models. Found: {set(y)}")
        return

    # 1. Random Forest
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X, y)
    joblib.dump(rf, MODEL_DIR / "traffic_rf.pkl")

    # 2. XGBoost
    xgb = XGBClassifier(n_estimators=50, use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X, y)
    joblib.dump(xgb, MODEL_DIR / "traffic_xgb.pkl")

    # 3. Logistic Regression
    lr = LogisticRegression(max_iter=200)
    lr.fit(X, y)
    joblib.dump(lr, MODEL_DIR / "traffic_logistic.pkl")

    # 4. Isolation Forest (unsupervised)
    iso = IsolationForest(contamination=0.2, random_state=42)
    iso.fit(X)
    joblib.dump(iso, MODEL_DIR / "traffic_iso.pkl")

    print("✅ Models saved to:", MODEL_DIR)

if __name__ == "__main__":
    print("📥 Loading log data...")
    raw = load_log_data()
    df = extract_features(raw)
    print(f"📊 {len(df)} samples loaded for training")
    train_and_save_models(df)
