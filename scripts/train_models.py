from pathlib import Path
import csv,numpy as np,joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score,classification_report
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"Data"
FILES=["cmdinjection.csv","DVWA_Normal.csv","DVWA_SQLInjection1.csv","DVWA_SQLInjection2.csv","DVWA_SQLInjection3.csv","sqlinject.csv","wordPressNormalandAttack/NormalV1.1.csv","SqlandCommand/AttackV1.1.csv","SqlandCommand/InsiderSql.csv","SqlandCommand/NormalV1.2.csv","brutforce/AttackV1.1.csv","brutforce/InsiderV1.1.csv"]
def main():
    X=[]; y=[]
    for rel in FILES:
        with (DATA/rel).open(newline="",encoding="utf-8-sig") as f:
            for i,row in enumerate(csv.reader(f)):
                if i: X.append([float(v) for v in row[1:37]]); y.append([int(v) for v in row[37:]].index(1))
    X=Normalizer().fit_transform(np.asarray(X)); y=np.asarray(y)
    a,b,c,d=train_test_split(X,y,test_size=.2,random_state=1)
    model=SVC(kernel="rbf"); model.fit(a,c); pred=model.predict(b)
    print("SVM accuracy",accuracy_score(d,pred)); print(classification_report(d,pred))
    (ROOT/"models").mkdir(exist_ok=True); joblib.dump(model,ROOT/"models/kubanomaly_svm.joblib")
    try:
        import tensorflow as tf
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Input,Dense,Dropout,Conv1D,Flatten
        yc=tf.keras.utils.to_categorical(c,2)
        dnn=Sequential([Input(shape=(36,)),Dense(128,activation="elu"),Dropout(.3),Dense(64,activation="elu"),Dropout(.2),Dense(2,activation="softmax")])
        dnn.compile(optimizer="adam",loss="categorical_crossentropy",metrics=["accuracy"]); dnn.fit(a,yc,validation_split=.1,epochs=30,batch_size=128); dnn.save(ROOT/"models/kubanomaly_dnn.keras")
        cnn=Sequential([Input(shape=(36,1)),Conv1D(32,3,activation="relu"),Flatten(),Dense(64,activation="relu"),Dropout(.2),Dense(2,activation="softmax")])
        cnn.compile(optimizer="adam",loss="categorical_crossentropy",metrics=["accuracy"]); cnn.fit(a[...,None],yc,validation_split=.1,epochs=30,batch_size=128); cnn.save(ROOT/"models/kubanomaly_cnn.keras")
    except ImportError: print("TensorFlow missing; only SVM trained.")
if __name__=="__main__": main()
