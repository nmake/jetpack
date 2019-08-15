"""
filter specific to the object browser template
"""
from functools import reduce  # forward compatibility for Python 3
import operator
import json


def _to_json_sorted(data):
    return json.dumps(json.loads(json.dumps(data)), sort_keys=True)


def _to_int(string):
    try:
        return int(string)
    except ValueError:
        return string


def _get_from_dict(data_dict, keypath):
    map_list = [_to_int(x) for x in keypath.split('.')]
    try:
        res = reduce(operator.getitem, map_list, data_dict)
        return res
    except KeyError:
        return {}


def object_browser_filter(report_type, hostvars, playhosts, keypaths):
    """
    filter plugin specific to the object browser
    """
    res = {}
    if report_type == "all_in_one":
        for host in playhosts:
            res[host] = {}
            if not keypaths:
                res[host]['hostvars'] = hostvars[host]
            else:
                for keypath in keypaths:
                    res[host][keypath] = _get_from_dict(hostvars[host],
                                                        keypath)
    elif report_type == "per_host":
        res[playhosts[0]] = {}
        if not keypaths:
            res[playhosts[0]]['hostvars'] = hostvars
        else:
            for keypath in keypaths:
                res[playhosts[0]][keypath] = _get_from_dict(hostvars,
                                                            keypath)
    return _to_json_sorted(res)


class FilterModule(object):  # pylint: disable=R0205, R0903
    """
    object_browser_filter
    """

    def filters(self):  # pylint: disable=R0201
        ''' filters '''
        return {
            'object_browser_filter': object_browser_filter
        }
