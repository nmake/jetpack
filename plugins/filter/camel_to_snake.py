
from ansible.errors import AnsibleFilterError
import re


def camel_to_snake(parsed):
    if isinstance(parsed, list):
        working = [camel_to_snake(x) for x in parsed]
        return working
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            new_key = k
            for fnd in re.findall("([a-z][A-Z])", new_key):
                fixed = '_'.join(list(fnd)).lower()
                new_key = new_key.replace(fnd, fixed)
            working[new_key] = camel_to_snake(val)
        return working
    return parsed


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'camel_to_snake': camel_to_snake
        }
