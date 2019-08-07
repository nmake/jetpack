

import re
from itertools import chain
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import iteritems
from ansible.errors import AnsibleFilterError


def sort_list(val):
    if isinstance(val, list):
        return sorted(val)
    return val


def dict_merge_bang(base, other):
    """ Return a new dict object that combines base and other

    This will create a new dict object that is a combination of the key/value
    pairs from base and other.  When both keys exist, the value will be
    selected from other.  If the value is a list object, the lists will be
    combined, entries in other prefixed with a ! will be removed.

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
                        combined[key] = dict_merge_bang(value, other[key])
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
                    if all(isinstance(x, str) for x in item) and \
                      all(isinstance(x, str) for x in value):
                        for entry in item:
                            if entry.startswith('!') and entry[1:] in value:
                                value.remove(entry[1:])
                            elif entry not in value and not entry.startswith('!'):
                                value.append(entry)
                        combined[key] = value
                    else:
                        try:
                            combined[key] = list(set(chain(value, item)))
                        except TypeError:
                            value.extend([i for i in item if i not in value])
                            combined[key] = value
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


class FilterModule(object):
    ''' Network filter '''

    def filters(self):
        return {
            'dict_merge_bang': dict_merge_bang
        }
