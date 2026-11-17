#!/usr/bin/env python3
import argparse,json,time,requests
from datetime import datetime,timezone
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--log",default="/var/log/falco/events.json")
    p.add_argument("--center",default="http://127.0.0.1:8003")
    p.add_argument("--flush-every",type=float,default=10)
    a=p.parse_args(); print("KubAnomaly Agent connected to Center.")
    batch=[]; last=time.time()
    with open(a.log,encoding="utf-8") as f:
        f.seek(0,2)
        while True:
            line=f.readline()
            if line:
                try: batch.append(json.loads(line))
                except json.JSONDecodeError: pass
            else: time.sleep(.15)
            if batch and time.time()-last>=a.flush_every:
                body={"records":batch,"window_start":datetime.now(timezone.utc).isoformat(),"window_seconds":10}
                try:
                    r=requests.post(a.center.rstrip("/")+"/predict/logs",json=body,timeout=30)
                    print(json.dumps(r.json(),indent=2))
                except Exception as e: print("Center request failed:",e)
                batch=[]; last=time.time()
if __name__=="__main__": main()
