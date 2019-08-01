
from ansible.errors import AnsibleFilterError
import re

from ansible.module_utils.network.common.utils import dict_merge


def nxos_flatten_table_row(parsed, plural=False):
    if isinstance(parsed, list):
        parsed = [nxos_flatten_table_row(x, plural) for x in parsed]
        return parsed
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            if k.startswith("TABLE") or k.startswith("ROW"):
                if isinstance(val, list):
                    name = "_".join(k.split('_')[1:])
                    if not name.endswith('s') and plural:
                        name += 's'
                    working[name] = [nxos_flatten_table_row(x, plural)
                                     for x in val]
                elif isinstance(val, dict):
                    working = dict_merge(working,
                                         nxos_flatten_table_row(val, plural))
            else:
                working[k] = nxos_flatten_table_row(val, plural)
        return working
    return parsed

class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'nxos_flatten_table_row': nxos_flatten_table_row
        }
