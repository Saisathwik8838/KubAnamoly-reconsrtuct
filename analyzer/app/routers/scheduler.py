from fastapi import APIRouter
from pathlib import Path
from datetime import datetime,timezone
import json
router=APIRouter()
ROOT=Path(__file__).resolve().parents[4]; HISTORY=ROOT/"detection_history.jsonl"
def append_history(record):
    row={**record,"recorded_at":datetime.now(timezone.utc).isoformat()}
    with HISTORY.open("a",encoding="utf-8") as f: f.write(json.dumps(row,default=str)+"\n")
@router.get("/scheduler/status")
def status():
    n=sum(1 for x in HISTORY.open(encoding="utf-8") if x.strip()) if HISTORY.exists() else 0
    return {"status":"success","history_records":n,"history_file":str(HISTORY)}
@router.get("/scheduler/history")
def history(limit:int=100):
    rows=[json.loads(x) for x in HISTORY.open(encoding="utf-8") if x.strip()] if HISTORY.exists() else []
    return {"status":"success","total":len(rows),"history":rows[-max(1,min(limit,1000)):][::-1]}
