
from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, MutableMapping



def to_dotted(nested_json):
    out = {}

    def flatten(data, name=''):
        if isinstance(data, (dict, Mapping, MutableMapping)):
            for k, val in data.items():
                if name:
                    nname = name + '.{}'.format(k)
                else:
                    nname = k
                flatten(val, nname)
        elif isinstance(data, list):
            for idx, val in enumerate(data):
                flatten(val, '{}[{}]'.format(name, idx))
        else:
            out[name] = data

    flatten(nested_json)
    return out

class FilterModule(object):
    ''' Network filter '''

    def filters(self):
        return {
            'to_dotted': to_dotted
        }
