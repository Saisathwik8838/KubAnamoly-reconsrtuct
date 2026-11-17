"""
Offline Model Evaluation Script
Reproduces Table VII and offline performance metrics reported in:
"Reconstruction and Experimental Evaluation of a Falco-Based Container Anomaly Detection Framework Inspired by KubAnomaly"
Section VIII-A, Table VII.
"""
from pathlib import Path
import csv
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
MODELS_DIR = ROOT / "models"

FILES = [
    "cmdinjection.csv",
    "DVWA_Normal.csv",
    "DVWA_SQLInjection1.csv",
    "DVWA_SQLInjection2.csv",
    "DVWA_SQLInjection3.csv",
    "sqlinject.csv",
    "wordPressNormalandAttack/NormalV1.1.csv",
    "SqlandCommand/AttackV1.1.csv",
    "SqlandCommand/InsiderSql.csv",
    "SqlandCommand/NormalV1.2.csv",
    "brutforce/AttackV1.1.csv",
    "brutforce/InsiderV1.1.csv"
]

def load_data():
    X, y = [], []
    for rel in FILES:
        p = DATA / rel
        if not p.exists():
            continue
        with p.open(newline="", encoding="utf-8-sig") as f:
            for i, row in enumerate(csv.reader(f)):
                if i > 0 and len(row) >= 38:
                    try:
                        feats = [float(v) for v in row[1:37]]
                        label = [int(v.strip()) for v in row[37:]].index(1)
                        X.append(feats)
                        y.append(label)
                    except (ValueError, IndexError):
                        continue
    X = Normalizer().fit_transform(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=int)
    return X, y

def evaluate_classifier(name, y_true, y_pred, y_probs=None):
    acc = accuracy_score(y_true, y_pred) * 100
    prec = precision_score(y_true, y_pred, pos_label=1) * 100
    rec = recall_score(y_true, y_pred, pos_label=1) * 100
    f1 = f1_score(y_true, y_pred, pos_label=1) * 100
    auc_val = roc_auc_score(y_true, y_probs if y_probs is not None else y_pred) * 100
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0
    fnr = (fn / (fn + tp)) * 100 if (fn + tp) > 0 else 0
    
    return {
        "Accuracy (%)": f"{acc:.2f}",
        "Precision (%)": f"{prec:.2f}",
        "Recall (%)": f"{rec:.2f}",
        "F1-score (%)": f"{f1:.2f}",
        "ROC-AUC (%)": f"{auc_val:.2f}",
        "FPR (%)": f"{fpr:.2f}",
        "FNR (%)": f"{fnr:.2f}",
        "TP": tp, "FP": fp, "TN": tn, "FN": fn
    }

def main():
    print(f"Loading datasets from {DATA}...")
    X, y = load_data()
    print(f"Total dataset samples: {len(X)}")
    
    # Paper uses 80:20 split with random_state=1 (Eq. 4)
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=1
    )
    print(f"Held-out test split: {len(X_test)} samples ({sum(y_test==0)} Normal, {sum(y_test==1)} Attack)")

    results = {}

    # 1. SVM
    svm_path = MODELS_DIR / "kubanomaly_svm.joblib"
    if svm_path.exists():
        svm = joblib.load(svm_path)
        preds = svm.predict(X_test)
        scores = svm.decision_function(X_test) if hasattr(svm, "decision_function") else preds
        results["SVM"] = evaluate_classifier("SVM", y_test, preds, scores)
    else:
        print("SVM model not found in models/kubanomaly_svm.joblib")

    # 2. DNN and CNN (if TensorFlow installed)
    try:
        from tensorflow.keras.models import load_model
        dnn_path = MODELS_DIR / "kubanomaly_dnn.keras"
        if dnn_path.exists():
            dnn = load_model(dnn_path)
            probs = dnn.predict(X_test)
            preds = np.argmax(probs, axis=1)
            results["DNN"] = evaluate_classifier("DNN", y_test, preds, probs[:, 1])

        cnn_path = MODELS_DIR / "kubanomaly_cnn.keras"
        if cnn_path.exists():
            cnn = load_model(cnn_path)
            probs = cnn.predict(X_test[..., None])
            preds = np.argmax(probs, axis=1)
            results["CNN"] = evaluate_classifier("CNN", y_test, preds, probs[:, 1])
    except ImportError:
        pass

    if results:
        print("\n" + "=" * 60)
        print("TABLE VII: OFFLINE MODEL PERFORMANCE ON THE HELD-OUT SPLIT")
        print("=" * 60)
        headers = ["Metric"] + list(results.keys())
        print(f"{headers[0]:<16} " + " ".join(f"{h:>10}" for h in headers[1:]))
        print("-" * 60)
        metrics = ["Accuracy (%)", "Precision (%)", "Recall (%)", "F1-score (%)", "ROC-AUC (%)", "FPR (%)", "FNR (%)"]
        for m in metrics:
            row = [m] + [results[model][m] for model in results]
            print(f"{row[0]:<16} " + " ".join(f"{v:>10}" for v in row[1:]))
        print("=" * 60)
    else:
        print("No trained models found in models/ directory. Run scripts/train_models.py first.")

if __name__ == "__main__":
    main()
