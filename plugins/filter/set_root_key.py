import re
from ansible.errors import AnsibleFilterError
from ansible.module_utils.network.common.utils import dict_merge


def set_root_key(parsed, key):
    return {key: parsed}


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'set_root_key': set_root_key
        }
