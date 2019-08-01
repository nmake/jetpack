import re
from ansible.errors import AnsibleFilterError
from ansible.module_utils.network.common.utils import dict_merge

def _unnest(parsed, key):
    if isinstance(parsed, list):
        parsed = [_unnest(x, key) for x in parsed]
        return parsed
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            match = re.match(k, key)
            if match and isinstance(val, dict):
                working = dict_merge(working, _unnest(val, key))
            else:
                working[k] = _unnest(val, key)
        return working
    return parsed

def unnest(parsed, keys):
    for key in keys:
        parsed = _unnest(parsed, key)
    return parsed

class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'unnest': unnest
        }
