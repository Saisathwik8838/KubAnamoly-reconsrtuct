# KubAnomaly reconstructed prototype

This is a best-effort reconstruction from retained project notes, NOT a byte-for-byte recovery of the deleted laptop directory. It does not contain the original trained `.keras`/`.joblib` artifacts or exact private environment settings.

## Architecture
Ubuntu VM: Falco JSON -> Python agent -> FastAPI Center on host:8003 -> feature mapping -> SVM/DNN/CNN -> JSONL history. A separate collector sends Docker stats to `/hardware`.

## Host setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=analyzer uvicorn app.main:app --app-dir analyzer --host 0.0.0.0 --port 8003
```
Swagger: http://localhost:8003/docs

## Model artifacts
Put these in `models/`:
- `kubanomaly_svm.joblib`
- `kubanomaly_dnn.keras`
- `kubanomaly_cnn.keras`

They are not included because the actual binaries were not recoverable. API starts without them, but prediction returns HTTP 503 until models are supplied.

## Ubuntu VM
Install Docker and Falco, configure Falco to write JSON to `/var/log/falco/events.json`, then:
```bash
python3 -m venv ~/kubanomaly-venv
source ~/kubanomaly-venv/bin/activate
pip install requests
python agent/kubanomaly_agent.py --log /var/log/falco/events.json --center http://HOST_IP:8003
python agent/kubanomaly_hardware.py --center http://HOST_IP:8003
```

The 36-feature event mapping is a heuristic reconstruction based on retained logs and paper notes, not a verified copy of the original Center implementation. The previous live benign workload produced false positives; offline metrics must not be presented as live accuracy.
