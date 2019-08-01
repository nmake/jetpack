
import re


def _flatten_list_of_dicts_key(parsed, key):
    if isinstance(parsed, list):
        parsed = [_flatten_list_of_dicts_key(x, key) for x in parsed]
        return parsed
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            match = re.match(key['key'], k)
            try:
                if all(v.get(key['value']) for v in val) and match:
                    working[k] = [x[key['value']] for x in val]
                    continue
            except (AttributeError, TypeError):
                pass
            working[k] = _flatten_list_of_dicts_key(val, key)
        return working
    return parsed


def flatten_list_of_dicts(parsed, flatten):
    for key in flatten:
        parsed = _flatten_list_of_dicts_key(parsed, key)
    return parsed


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'flatten_list_of_dicts': flatten_list_of_dicts
        }
