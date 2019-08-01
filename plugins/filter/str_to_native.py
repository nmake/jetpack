
from ansible.errors import AnsibleFilterError
import ast

def str_to_native(parsed):
    if isinstance(parsed, list):
        parsed = [str_to_native(p) for p in parsed]
    elif isinstance(parsed, dict):
        for k, val in parsed.items():
            parsed[k] = str_to_native(val)
    else:
        try:
            parsed = ast.literal_eval(parsed)
        except (ValueError, SyntaxError):
            pass
        if isinstance(parsed, str):
            if parsed == "none":
                parsed = None
            elif parsed.lower() == "false":
                parsed = False
            elif parsed.lower() == "true":
                parsed = True
    return parsed


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'str_to_native': str_to_native
        }
