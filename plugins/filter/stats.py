
from ansible.errors import AnsibleFilterError
from ansible.module_utils.network.common.utils import dict_merge
from collections import Counter

import q

def _stats(parsed, key, statsd):
    if isinstance(parsed, list):
        working = []
        for entry in parsed:
            res, resstats = _stats(entry, key, statsd)
            working.append(res)
            statsd = dict_merge(statsd, resstats)
        return working, statsd
    if isinstance(parsed, dict):
        working = {}
        for k, val in parsed.items():
            res, resstats = _stats(val, key, statsd)
            working = dict_merge(working, {k: res})
            statsd = dict_merge(statsd, resstats)
            counts = None
            if isinstance(res, dict):
                try:
                    counts = dict(Counter(cval[key]
                                          for ckey, cval in res.items()))
                except (AttributeError, TypeError, KeyError):
                    pass
            if isinstance(res, list):
                try:
                    counts = dict(Counter(cval[key] for cval in res))
                except (AttributeError, TypeError, KeyError):
                    pass
            if counts:
                stats_dict = {k + "_stats": {'count_by_' + key: counts,
                                             'total': len(res)}}
                working = dict_merge(working, stats_dict)
                statsd = dict_merge(statsd, stats_dict)
        return working, statsd
    return parsed, statsd


def stats(parsed, keys, only_stats=False):
    q(keys, only_stats)
    statsd = {}
    for key in keys:
        parsed, statsd = _stats(parsed, key, statsd)
    if only_stats:
        return statsd
    return parsed


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'stats': stats
        }
