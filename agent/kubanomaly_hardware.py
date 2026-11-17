#!/usr/bin/env python3
import argparse,subprocess,json,time,requests
from datetime import datetime,timezone
def collect():
    raw=subprocess.check_output(["docker","stats","--no-stream","--format","{{json .}}"],text=True)
    out=[]
    for line in raw.splitlines():
        try:
            x=json.loads(line); out.append({"container":x.get("Name"),"cpu_percent":x.get("CPUPerc"),"memory_usage":x.get("MemUsage"),"memory_percent":x.get("MemPerc"),"network_io":x.get("NetIO"),"block_io":x.get("BlockIO"),"pids":x.get("PIDs")})
        except json.JSONDecodeError: pass
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--center",default="http://127.0.0.1:8003"); p.add_argument("--interval",type=int,default=10); a=p.parse_args()
    while True:
        try:
            m=collect(); r=requests.post(a.center.rstrip("/")+"/hardware",json={"metrics":m,"collected_at":datetime.now(timezone.utc).isoformat()},timeout=15); print(r.status_code,r.text)
        except Exception as e: print("Hardware collection failed:",e)
        time.sleep(a.interval)
if __name__=="__main__": main()
