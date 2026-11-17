#!/bin/sh
# Benign TCP Activity Workload (Section VII-C & VIII-C)
# Executes inside an Alpine container: opens local TCP listener and sends loopback Netcat messages.

CONTAINER_NAME="kubanomaly-benign-tcp"
PORT=9099
DURATION_SECONDS=${1:-60}

echo "[+] Starting Benign TCP Activity Container: $CONTAINER_NAME"
docker run -d --rm --name "$CONTAINER_NAME" alpine:latest sh -c "
    echo '[+] Workload running for $DURATION_SECONDS seconds...';
    END=\$((\$(date +%s) + $DURATION_SECONDS));
    # Start background netcat listener
    while true; do nc -l -p $PORT -e echo 'PONG'; done > /dev/null 2>&1 &
    sleep 1;
    while [ \$(date +%s) -lt \$END ]; do
        echo 'PING' | nc 127.0.0.1 $PORT > /dev/null 2>&1
        sleep 0.2
    done;
    echo '[+] Completed benign TCP loopback activity workload.'
"

echo "[+] Monitoring container $CONTAINER_NAME. Tail logs with: docker logs -f $CONTAINER_NAME"
