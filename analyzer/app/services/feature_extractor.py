from collections import Counter
FEATURES = ["udp","select","bin","run","poll","media","sys","dev","etc","usr","root","host","brk","boot","mkdir","write","connect","tcp","clone_API","proc","read","var","network_http","File_IO","kill_API","accept","home","munmap","mnt","opt","rename","srv","mmap","chdir_API","network_connection","execve_API"]
def val(d, *keys, default=""):
    for k in keys:
        if not isinstance(d,dict): return default
        d=d.get(k,{})
    return d if d is not None else default
def extract_features(records, container_id=None):
    counts=Counter(); mapped=0
    for r in records:
        fields=r.get("output_fields",{}) if isinstance(r,dict) else {}
        cid=fields.get("container.id","")
        if container_id and cid != container_id: continue
        evt=str(fields.get("evt.type",r.get("evt",{}).get("type","") if isinstance(r,dict) else "")).lower()
        fd=str(fields.get("fd.name","")).lower()
        groups={
          "poll":["poll","ppoll"],"select":["select","pselect6"],"brk":["brk"],
          "mmap":["mmap"],"mkdir":["mkdir","mkdirat"],"write":["write","writev","pwrite64"],
          "connect":["connect"],"accept":["accept","accept4"],"execve_API":["execve","execveat"],
          "File_IO":["open","openat","creat"],"clone_API":["clone","clone3","fork","vfork"],
          "read":["read","readv","pread64"],"munmap":["munmap"],"chdir_API":["chdir","fchdir"],
          "rename":["rename","renameat","renameat2"],"kill_API":["kill","tkill","tgkill"],
          "udp":["sendto","recvfrom","sendmsg","recvmsg"],"bin":["sendfile","splice"],
          "sys":["close","dup","dup2","dup3","fcntl"],"media":["ioctl"],"proc":["getpid","getppid","prctl"]}
        hit=False
        for feature, events in groups.items():
            if evt in events:
                counts[feature]+=1; mapped+=1; hit=True
                if feature in ("connect","accept"): counts["network_connection"]+=1
                if feature=="execve_API": counts["run"]+=1
        if evt in ("open","openat","creat"):
            for token in ("etc","usr","root","var","home","tmp","boot","dev","sys","mnt","opt","srv"):
                if f"/{token}/" in fd: counts[token]+=1
    vector=[float(counts.get(f,0)) for f in FEATURES]
    return {"feature_names":FEATURES,"feature_vector":vector,"feature_counts":{f:int(counts.get(f,0)) for f in FEATURES},"mapped_event_count":mapped,"unmapped_event_count":max(0,len(records)-mapped),"mapping_note":"Heuristic reconstruction; verify feature semantics and order against training pipeline."}
