
from ansible.errors import AnsibleFilterError
import re


def keep_keys(parsed, keys):
    if isinstance(parsed, list):
        res = [keep_keys(x, keys) for x in parsed]
        return res
    if isinstance(parsed, dict):  # pylint: disable=R1702
        working = {}
        for k, val in parsed.items():
            for key in keys:
                match = re.match(key, k)
                if not isinstance(val, (list, dict)):
                    if match:
                        working[k] = val
                else:
                    res = keep_keys(val, keys)
                    if isinstance(res, list) and not match:
                        res = [r for r in res if r not in ([], {})]
                        if all(isinstance(s, str) for s in res):
                            continue
                    if res in ([], {}):
                        continue
                    working[k] = res
        return working
    return parsed

class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'keep_keys': keep_keys
        }
