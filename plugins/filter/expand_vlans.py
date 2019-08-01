import re
from ansible.errors import AnsibleFilterError


def _expand_vlan(vlan):
    match = re.match(r'([A-Za-z]*)(.+)', vlan)
    if not match:
        return vlan
    index = match.group(2)
    indices = list()
    for item in index.split(','):
        tokens = item.split('-')
        if len(tokens) == 1:
            indices.append(int(tokens[0]))
        elif len(tokens) == 2:
            start, end = tokens
            for i in range(int(start), int(end) + 1):
                indices.append(i)
                i += 1
    return ['%d' % int(index) for index in indices]


def _expand_vlans(parsed, key):
    if isinstance(parsed, list):
        parsed = [_expand_vlans(p, key) for p in parsed]
    elif isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            match = re.match(key, k)
            if match and isinstance(val, str):
                working[k] = _expand_vlan(val)
            else:
                working[k] = _expand_vlans(val, key)
        return working
    return parsed


def expand_vlans(parsed, keys):
    for key in keys:
        parsed = _expand_vlans(parsed, key)
    return parsed

class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'expand_vlans': expand_vlans
        }
