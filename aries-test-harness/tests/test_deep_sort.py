import json
import logging

import pytest

class TestJson:

    def test_deep_sort(self):
        log = logging.getLogger()

        map1 = {"c": 3, "b": 2, "a": 1}
        map2 = {"f": 6, "e": 5, "d": 4}
        map1["b"] = map2

        json_str = json.dumps(map1)
        log.info(json_str)
        assert json_str == '{"c": 3, "b": {"f": 6, "e": 5, "d": 4}, "a": 1}'

        def sorted_payload(val, level=0):
            valdict = None
            if isinstance(val, str) and len(val) > 1 and (val[0]+val[-1]) == '{}':
                valdict = dict(json.loads(val))
            elif isinstance(val, dict):
                valdict = val
            if valdict:
                valdict = dict(sorted(valdict.items()))
                valdict = {k:sorted_payload(v, level+1) for (k,v) in valdict.items()}
                val = level and valdict or json.dumps(valdict)
            return val

        json_str = sorted_payload(json_str)
        log.info(json_str)
        assert json_str == '{"a": 1, "b": {"d": 4, "e": 5, "f": 6}, "c": 3}'

def main():
    tc = TestJson()
    tc.test_deep_sort()

if __name__ == "__main__":
    exit(main())
