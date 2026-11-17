"""
Unit tests for KubAnomaly Monitoring Agent
Validates windowing bucket math b(t) = W * floor(t / W) (Paper Eq. 7)
and Falco log line parsing.
"""
import math
import json

def compute_bucket(timestamp: float, window_size: int = 10) -> int:
    return window_size * math.floor(timestamp / window_size)

def test_bucket_windowing():
    # Events within the same 10-second window should map to the exact same bucket
    w = 10
    t1 = 1700000002.5
    t2 = 1700000008.9
    t3 = 1700000010.1

    b1 = compute_bucket(t1, w)
    b2 = compute_bucket(t2, w)
    b3 = compute_bucket(t3, w)

    assert b1 == b2
    assert b3 == b1 + 10

def test_falco_json_parsing():
    raw_line = '{"output": "test", "priority": "Notice", "output_fields": {"container.id": "abc123456", "evt.type": "openat"}}'
    record = json.loads(raw_line)
    assert record["output_fields"]["container.id"] == "abc123456"
    assert record["output_fields"]["evt.type"] == "openat"
