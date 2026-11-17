#!/bin/sh
# Benign File Activity Workload (Section VII-C & VIII-B)
# Executes inside an Alpine container: repeatedly creates temporary files and reads them back.

CONTAINER_NAME="kubanomaly-benign-file"
DURATION_SECONDS=${1:-60}

echo "[+] Starting Benign File Activity Container: $CONTAINER_NAME"
docker run -d --rm --name "$CONTAINER_NAME" alpine:latest sh -c "
    echo '[+] Workload running for $DURATION_SECONDS seconds...';
    END=\$((\$(date +%s) + $DURATION_SECONDS));
    while [ \$(date +%s) -lt \$END ]; do
        TMP_FILE=\"/tmp/test_\$(date +%s%N).txt\"
        echo \"sample data payload \$(date)\" > \"\$TMP_FILE\"
        cat \"\$TMP_FILE\" > /dev/null
        rm -f \"\$TMP_FILE\"
        sleep 0.1
    done;
    echo '[+] Completed benign file activity workload.'
"

echo "[+] Monitoring container $CONTAINER_NAME. Tail logs with: docker logs -f $CONTAINER_NAME"
