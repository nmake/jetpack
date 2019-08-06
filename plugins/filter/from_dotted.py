

import re
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import iteritems
from ansible.errors import AnsibleFilterError


def sort_list(val):
    if isinstance(val, list):
        return sorted(val)
    return val


def dmli(base, other):
    """ Return a new dict object that combines base and other

    This will create a new dict object that is a combination of the key/value
    pairs from base and other.  When both keys exist, the value will be
    selected from other.  If the value is a list object, the two lists will
    be combined based on list index.  (This is different than the dict_merge
    in network_utils common)

    :param base: dict object to serve as base
    :param other: dict object to combine with base

    :returns: new combined dict object
    """
    if not isinstance(base, dict):
        raise AssertionError("`base` must be of type <dict>")
    if not isinstance(other, dict):
        raise AssertionError("`other` must be of type <dict>")

    combined = dict()

    for key, value in iteritems(base):
        if isinstance(value, dict):
            if key in other:
                item = other.get(key)
                if item is not None:
                    if isinstance(other[key], Mapping):
                        combined[key] = dmli(value, other[key])
                    else:
                        combined[key] = other[key]
                else:
                    combined[key] = item
            else:
                combined[key] = value
        elif isinstance(value, list):
            if key in other:
                item = other.get(key)
                if item is not None:
                    left = {idx: val for idx, val in enumerate(value)}
                    right = {idx: val for idx, val in enumerate(item)}
                    for k, val in right.items():
                        if k in left:
                            if val is not None:
                                left[k] = dmli({"tmp": left[k]},
                                               {"tmp": val})['tmp']
                        else:
                            left[k] = val
                    combined[key] = list(left.values())
                else:
                    combined[key] = item
            else:
                combined[key] = value
        else:
            if key in other:
                other_value = other.get(key)
                if other_value is not None:
                    if sort_list(base[key]) != sort_list(other_value):
                        combined[key] = other_value
                    else:
                        combined[key] = value
                else:
                    combined[key] = other_value
            else:
                combined[key] = value

    for key in set(other.keys()).difference(base.keys()):
        combined[key] = other.get(key)

    return combined


def from_dotted(d):
    if isinstance(d, dict):
        working = {}
        for key, value in d.items():
            splitted = key.split('.', 1)
            cap = re.match(r'^(?P<key>.*)\[(?P<idx>\d+)\]', splitted[0])
            if cap:
                capdict = cap.groupdict()
                filled = [None] * int(capdict['idx'])
                if len(splitted) == 2:
                    filled.append(from_dotted({splitted[1]: value}))
                else:
                    filled.append(value)
                working[capdict['key']] = filled
                continue
            if len(splitted) == 2:
                if splitted[0] not in working:
                    working[splitted[0]] = {}
                res = from_dotted({splitted[1]: value})
                working[splitted[0]] = dmli(working[splitted[0]], res)
                continue
            working[key] = from_dotted(value)
        return working
    return d

class FilterModule(object):
    ''' Network filter '''

    def filters(self):
        return {
            'from_dotted': from_dotted
        }
