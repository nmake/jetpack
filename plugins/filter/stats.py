
from ansible.errors import AnsibleFilterError
from ansible.module_utils.network.common.utils import dict_merge
from collections import Counter


def _stats(parsed, key, statsd, missing_key="unknown"):
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
                    if any(key in cval for ckey, cval in res.items()):
                        counts = dict(Counter(cval.get(key, missing_key)
                                              for ckey, cval in res.items()))
                except (AttributeError, TypeError, KeyError):
                    pass
            if isinstance(res, list):
                try:
                    if any(key in cval for cval in res):
                        counts = dict(Counter(cval.get(key, missing_key)
                                              for cval in res))
                except (AttributeError, TypeError, KeyError):
                    pass
            if counts:
                ckey = 'count_by_' + key
                count_dict = {ckey: counts}
                count_dict[ckey]['total'] = len(res)
                stats_dict = {"stats": count_dict}
                working = dict_merge(working, stats_dict)
                statsd = dict_merge(statsd, stats_dict)
        return working, statsd
    return parsed, statsd


def stats(parsed, keys, only_stats=False):
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
