
from ansible.errors import AnsibleFilterError
from ansible.module_utils.network.common.utils import dict_merge


def _rekey_on_member_key(parsed, key):
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            res = _rekey_on_member_key(val, key)
            if isinstance(res, dict) and key in res:
                if res[key] in working:
                    if not isinstance(working[res[key]], list):
                        working[res[key]] = [working[res[key]]]
                    working[res[key]].append(res)
                else:
                    working[res[key]] = res
                continue
            working = dict_merge(working, {k: res})
        return working
    if isinstance(parsed, list):
        if all(x.get(key) for x in parsed):
            working = {}
            for entry in parsed:
                res = _rekey_on_member_key(entry, key)
                if entry[key] in working:
                    for k, val in working.items():
                        if not isinstance(val, list):
                            working[k] = [val]
                    working[entry[key]].append(res)
                else:
                    working[entry[key]] = res
            return working
    return parsed


def rekey_on_members(parsed, members):
    for key in members:
        parsed = _rekey_on_member_key(parsed, key)
    return parsed


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'rekey_on_members': rekey_on_members
        }
