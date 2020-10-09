#!/usr/bin/env python
import json
import sys

count = 0
mismatches = 0

# Validate incoming twitter object id, id_str match and are expected types
# stdin is JSONL tweet objects (one fully-formed tweet per line of text)
try:
    for line in sys.stdin:
        try:
            t = json.loads(line.strip())
        except Exception as ex:
            print("parsing error %s", ex)
            continue
        id = t["id"]
        id_str = t["id_str"]
        assert isinstance(id, int)
        assert isinstance(id_str, str)
        count += 1
        if str(id) != id_str:
            mismatches += 1
            print(f"({mismatches}/{count}/{mismatches/count*100.0}) {id} != {id_str}")
except KeyboardInterrupt:
    print()
finally:
    error_percent = mismatches / count * 100.0 if count else 0.0
    print(f"count={count}, mismatches={mismatches}, percent_mismatch={error_percent}")
