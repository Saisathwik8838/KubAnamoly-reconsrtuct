from pathlib import Path
import numpy as np, joblib
ROOT=Path(__file__).resolve().parents[3]
MODEL_DIR=ROOT/"models"
_models={}
def load_models():
    global _models
    _models={}
    p=MODEL_DIR/"kubanomaly_svm.joblib"
    if p.exists(): _models["svm"]=joblib.load(p)
    try:
        from tensorflow.keras.models import load_model
        for n in ("dnn","cnn"):
            p=MODEL_DIR/f"kubanomaly_{n}.keras"
            if p.exists(): _models[n]=load_model(p)
    except Exception: pass
    return list(_models)
def predict(vector):
    if not _models: load_models()
    if not _models: raise RuntimeError("No model artifacts. Add SVM/DNN/CNN files to models/.")
    x=np.asarray(vector,dtype=float).reshape(1,-1); norm=np.linalg.norm(x)
    if norm: x=x/norm
    out={}
    for name,m in _models.items():
        p=np.asarray(m.predict(x))
        if name=="svm":
            label=int(p.ravel()[0]); item={"prediction":"Attack" if label==1 else "Normal"}
            if hasattr(m,"decision_function"): item["attack_score"]=float(np.asarray(m.decision_function(x)).ravel()[0])
            out[name]=item
        else:
            probs=p.reshape(-1); i=int(np.argmax(probs))
            out[name]={"prediction":"Attack" if i==1 else "Normal","probabilities":{"normal":float(probs[0]),"attack":float(probs[1])}}
    return out
