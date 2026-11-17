from pathlib import Path
import csv
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

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

def load_dataset():
    X = []
    y = []
    for rel in FILES:
        csv_path = DATA / rel
        if not csv_path.exists():
            print(f"Warning: {csv_path} not found.")
            continue
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            for i, row in enumerate(csv.reader(f)):
                if i > 0 and len(row) >= 38:
                    try:
                        features = [float(v) for v in row[1:37]]
                        label = [int(v.strip()) for v in row[37:]].index(1)
                        X.append(features)
                        y.append(label)
                    except (ValueError, IndexError):
                        continue
    X = Normalizer().fit_transform(np.asarray(X, dtype=float))
    y = np.asarray(y, dtype=int)
    return X, y

def main():
    MODELS_DIR.mkdir(exist_ok=True)
    print("Loading datasets from", DATA)
    X, y = load_dataset()
    print(f"Total samples loaded: {len(X)} with {X.shape[1]} features.")
    
    # 80:20 train-test split, random state 1 (matching paper Eq. 4)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=1
    )
    print(f"Train split: {len(X_train)} samples, Test split: {len(X_test)} samples.")
    
    # 1. Support Vector Machine (RBF kernel, C=1.0)
    print("\n--- Training SVM (RBF kernel, C=1) ---")
    svm_model = SVC(kernel="rbf", C=1.0)
    svm_model.fit(X_train, y_train)
    svm_preds = svm_model.predict(X_test)
    print("SVM Accuracy:", accuracy_score(y_test, svm_preds))
    print(classification_report(y_test, svm_preds, target_names=["Normal", "Attack"]))
    joblib.dump(svm_model, MODELS_DIR / "kubanomaly_svm.joblib")
    print("Saved SVM model to models/kubanomaly_svm.joblib")

    # Neural models with TensorFlow/Keras
    try:
        import tensorflow as tf
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Input, Dense, Dropout, Conv1D, Flatten, MaxPooling1D
        
        y_train_cat = tf.keras.utils.to_categorical(y_train, 2)
        y_test_cat = tf.keras.utils.to_categorical(y_test, 2)

        # 2. Deep Neural Network (DNN: 64, 32, 16 units, ELU, Dropout, Softmax - Sec VI-H)
        print("\n--- Training DNN (64-32-16 ELU - Sec VI-H) ---")
        dnn = Sequential([
            Input(shape=(36,)),
            Dense(64, activation="elu"),
            Dropout(0.3),
            Dense(32, activation="elu"),
            Dropout(0.2),
            Dense(16, activation="elu"),
            Dense(2, activation="softmax")
        ])
        dnn.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        dnn.fit(X_train, y_train_cat, validation_split=0.1, epochs=30, batch_size=128, verbose=1)
        dnn.save(MODELS_DIR / "kubanomaly_dnn.keras")
        print("Saved DNN model to models/kubanomaly_dnn.keras")

        # 3. Convolutional Neural Network (1D CNN - Sec VI-I)
        print("\n--- Training CNN (Conv1D 16/32, MaxPool, Dense 64 - Sec VI-I) ---")
        cnn = Sequential([
            Input(shape=(36, 1)),
            Conv1D(16, 5, activation="relu", padding="same"),
            MaxPooling1D(2),
            Dropout(0.2),
            Conv1D(32, 5, activation="relu", padding="same"),
            Flatten(),
            Dense(64, activation="relu"),
            Dropout(0.2),
            Dense(2, activation="softmax")
        ])
        cnn.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        cnn.fit(X_train[..., None], y_train_cat, validation_split=0.1, epochs=30, batch_size=128, verbose=1)
        cnn.save(MODELS_DIR / "kubanomaly_cnn.keras")
        print("Saved CNN model to models/kubanomaly_cnn.keras")

    except ImportError:
        print("TensorFlow not installed. Only SVM trained and saved.")

if __name__ == "__main__":
    main()
