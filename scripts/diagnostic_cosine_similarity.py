"""
Feature Similarity Diagnostic Script
Implements Section VII-D (Eq. 12) & Section VIII-E (Table X) from:
"Reconstruction and Experimental Evaluation of a Falco-Based Container Anomaly Detection Framework Inspired by KubAnomaly"

Calculates cosine similarity between a live or test feature vector and normal training samples (DVWA_Normal.csv):
cos(x, y) = (x . y) / (||x||_2 * ||y||_2)
"""
from pathlib import Path
import csv
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
NORMAL_CSV = DATA / "DVWA_Normal.csv"

FEATURES = [
    "udp","select","bin","run","poll","media","sys","dev","etc","usr",
    "root","host","brk","boot","mkdir","write","connect","tcp","clone_API","proc",
    "read","var","network_http","File_IO","kill_API","accept","home","munmap","mnt","opt",
    "rename","srv","mmap","chdir_API","network_connection","execve_API"
]

def load_normal_samples():
    if not NORMAL_CSV.exists():
        raise FileNotFoundError(f"{NORMAL_CSV} not found.")
    samples = []
    with NORMAL_CSV.open(newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.reader(f)):
            if i > 0 and len(row) >= 38:
                try:
                    # check if row is labeled Normal (col 37 == 1)
                    if int(row[37].strip()) == 1:
                        vec = [float(v) for v in row[1:37]]
                        samples.append(vec)
                except (ValueError, IndexError):
                    continue
    return np.asarray(samples, dtype=float)

def cosine_similarity(x, Y):
    norm_x = np.linalg.norm(x)
    if norm_x == 0:
        return np.zeros(len(Y))
    x_unit = x / norm_x
    
    norm_Y = np.linalg.norm(Y, axis=1, keepdims=True)
    norm_Y[norm_Y == 0] = 1.0
    Y_unit = Y / norm_Y
    
    return np.dot(Y_unit, x_unit)

def main():
    print(f"Loading normal samples from {NORMAL_CSV}...")
    Y_normal = load_normal_samples()
    print(f"Loaded {len(Y_normal)} normal samples.")

    # 1. Print Table X: Selected Feature Means in DVWA_Normal.csv
    print("\n" + "=" * 50)
    print("TABLE X: SELECTED FEATURE MEANS IN DVWA_NORMAL.CSV")
    print("=" * 50)
    selected_features = ["select", "poll", "etc", "tcp", "var", "network_http", "File_IO", "network_connection"]
    means = np.mean(Y_normal, axis=0)
    for feat in selected_features:
        idx = FEATURES.index(feat)
        print(f"{feat:<22} {means[idx]:>10.2f}")
    print("=" * 50)

    # 2. Example: Synthetic live file-activity vector described in Section VIII-B & VIII-D
    # (dev, brk, clone_API, File_IO, mmap, execve_API)
    live_vector = np.zeros(36, dtype=float)
    live_vector[FEATURES.index("dev")] = 12.0
    live_vector[FEATURES.index("brk")] = 4.0
    live_vector[FEATURES.index("clone_API")] = 8.0
    live_vector[FEATURES.index("File_IO")] = 35.0
    live_vector[FEATURES.index("mmap")] = 18.0
    live_vector[FEATURES.index("execve_API")] = 6.0

    print("\n--- Diagnostic on Sample Live File-Activity Vector ---")
    sims = cosine_similarity(live_vector, Y_normal)
    print(f"Max cosine similarity:  {np.max(sims):.4f} (Paper reports ~0.5133)")
    print(f"Mean cosine similarity: {np.mean(sims):.4f} (Paper reports ~0.2037)")
    print(f"Min cosine similarity:  {np.min(sims):.4f}")

if __name__ == "__main__":
    main()
