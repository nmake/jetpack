
from ansible.errors import AnsibleFilterError
import re


def replace_keys(parsed, keys):
    if isinstance(parsed, list):
        working = [replace_keys(x, keys) for x in parsed]
        return working
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            new_key = k
            for key in keys:
                new_key = re.sub(key['before'], key['after'], new_key)
            if new_key:
                working[new_key] = replace_keys(val, keys)
        return working
    return parsed

class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'replace_keys': replace_keys
        }
