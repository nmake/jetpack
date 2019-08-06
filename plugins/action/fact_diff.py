from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import re
from ansible.plugins.action import ActionBase
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleModuleError
from ansible.plugins.callback import CallbackBase

ARGSPEC = {
    'argument_spec': {
        'before': {
            'required': True,
        },
        'after': {
            'required': True
        }
    }
}

VALID_MODULE_KWARGS = ('argument_spec', 'mutually_exclusive', 'required_if',
                       'required_one_of', 'required_together')


class ActionModule(ActionBase):
    """ action module
    """

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._after = None
        self._before = None
        self._result = None

    def _check_argspec(self):
        # pylint: disable=W0212
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({'ANSIBLE_MODULE_ARGS': self._task.args}))
        # pylint: enable=W0212
        spec = {k: v for k, v in ARGSPEC.items() if k in VALID_MODULE_KWARGS}
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**spec)

    def _fail_json(self, msg):
        msg = msg.replace('(basic.py)', self._task.action)
        raise AnsibleModuleError(msg)

    def _set_vars(self):
        before = self._task.args.get('before')
        after = self._task.args.get('after')
        if isinstance(before, list):
            self._before = {'before': before}
        else:
            self._before = before
        if isinstance(after, list):
            self._after = {'after': after}
        else:
            self._after = after

    def run(self, tmp=None, task_vars=None):
        self._task.diff = True
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._check_argspec()
        self._set_vars()
        diff_dict = {'before': self._before, 'after': self._after}

        diff_text = CallbackBase()._get_diff(diff_dict)
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        diff_text = ansi_escape.sub('', diff_text)

        self._result.update({
            'diff': diff_dict,
            'changed': self._before != self._after,
            'diff_lines': diff_text.splitlines()
        })

        return self._result
