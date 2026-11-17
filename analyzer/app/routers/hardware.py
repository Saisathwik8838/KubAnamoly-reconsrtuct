from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from datetime import datetime,timezone
router=APIRouter(); latest=None
class Payload(BaseModel):
    metrics:list[dict[str,Any]]
    collected_at:str|None=None
@router.post("/hardware")
def receive(p:Payload):
    global latest
    latest={"status":"success","collected_at":p.collected_at or datetime.now(timezone.utc).isoformat(),"metrics":p.metrics}
    return {"status":"success","containers_received":len(p.metrics)}
@router.get("/hardware")
def get_hardware(): return {"status":"success","latest":latest}
@router.get("/hardware/latest")
def get_latest(): return latest or {"status":"empty","message":"No hardware metrics received yet"}
