
from ansible.errors import AnsibleFilterError
import json

# the double dump avoids this https://bugs.python.org/issue25457

def to_json_sorted(data):
    return json.dumps(json.loads(json.dumps(data)), sort_keys=True)

class FilterModule(object):
    ''' to_json_sorted '''

    def filters(self):
        return {
            'to_json_sorted': to_json_sorted
        }
