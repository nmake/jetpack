from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleModuleError
from ansible.parsing.plugin_docs import read_docstring
from ansible.parsing.yaml.objects import AnsibleMapping


ARGSPEC = {
    'argument_spec': {
        'modules': {
            'type': 'list',
            'elements': 'dict',
            'suboptions': {
                'name': {
                    'type': 'str',
                },
                'data': {
                    'type': 'str'
                }
            },
            'required': True
        }
    }
}

VALID_MODULE_KWARGS = (
    'argument_spec', 'mutually_exclusive', 'required_if',
    'required_one_of', 'required_together'
)


class ActionModule(ActionBase):
    """ action module
    """

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._errors = []
        self._modules = None
        self._result = None
        self._revised = None
        self._spec = None

    def _check_argspec(self):
        # pylint: disable=W0212
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({'ANSIBLE_MODULE_ARGS': self._task.args}))
        # pylint: enable=W0212
        spec = {k: v for k, v in ARGSPEC.items() if k in VALID_MODULE_KWARGS}
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**spec)

    def _check_for_errors(self):
        if self._errors:
            raise AnsibleError(".  ".join(self._errors))

    def _check_modules(self):
        for module in self._modules:
            if module['name'] not in self._shared_loader_obj.module_loader:
                self._errors.append("{} was not found".format(module['name']))
        self._check_for_errors()

    def _compare_spec(self, spec, data):
        if isinstance(data, list):
            working = [self._compare_spec(spec, x) for x in data]
            return working
        if isinstance(data, dict):
            working = {}
            for skey, sval in spec.items():
                dval = data.get(skey)
                if dval is None:
                    continue
                sval_type = sval.get('type', 'str')
                if sval_type in ['list', 'dict']:
                    if 'suboptions' not in sval:
                        self._errors.append("{} missing 'options' in module"
                                            " specification".format(skey))
                        continue
                    working[skey] = self._compare_spec(sval['suboptions'],
                                                       dval)
                else:
                    working[skey] = dval
            return working

        if isinstance(spec, AnsibleMapping):
            desired = 'dict'
        self._errors.append("Cannot compare, module requires a {}"
                            " but a {} was provided."
                            .format(desired, type(data).__name__))
        return data

    def _fail_json(self, msg):
        msg = msg.replace('(basic.py)', self._task.action)
        raise AnsibleModuleError(msg)

    def _set_vars(self):
        self._modules = self._task.args.get('modules')

    def _get_spec(self, module):
        mloadr = self._shared_loader_obj.module_loader
        filename = mloadr.find_plugin(module)
        docstring = read_docstring(filename, verbose=True, ignore_errors=True)
        if not docstring.get('doc'):
            self._errors.append("{} missing documentation string"
                                .format(module))
        self._check_for_errors()
        spec = docstring.get('doc').get('options')
        if not spec:
            self._errors.append(
                "{} malformed documentation string".format(module))
        self._check_for_errors()
        return spec

    def run(self, tmp=None, task_vars=None):
        # pylint: disable=W0212
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._check_argspec()
        self._set_vars()
        self._check_modules()
        self._result.update({
            'before': {},
            'ready': {},
            'changed': False,
            'modules': []
        })

        for module in self._modules:
            spec = self._get_spec(module['name'])
            updated = self._compare_spec(spec, module['data'])
            self._check_for_errors()
            if updated != module['data']:
                self._result['changed'] = True
            self._result['before'][module['name']] = module['data']
            self._result['ready'][module['name']] = updated
            self._result['modules'].append(module)

        return self._result
