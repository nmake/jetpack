from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
from ansible.plugins.action import ActionBase
from ansible.module_utils.six import PY3
from ansible.module_utils.network.common.utils import dict_merge
from ansible.errors import AnsibleError
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible.errors import AnsibleModuleError
from ansible.template import Templar
from ansible.utils.display import Display

display = Display()


try:
    from genie.conf.base import Device
    from genie.libs.parser.utils import get_parser
    HAS_GENIE = True
except ImportError:
    HAS_GENIE = False

try:
    from pyats.datastructures import AttrDict
    HAS_PYATS = True
except ImportError:
    HAS_PYATS = False

try:
    import xmltodict
    HAS_XMLTODICT = True
except ImportError:
    HAS_XMLTODICT = False


ARGSPEC = {
    'argument_spec': {
        'commands':
            {
                'type': 'list',
                'elements': 'dict',
                'options':
                    {
                        'command':
                            {
                                'type': 'str'
                            },
                        'set_fact':
                            {
                                'type': 'bool'
                            },
                        'transform':
                            {
                                'type': 'list',
                                'elements': 'dict',
                            }
                    }
            },
        'engine':
            {
                'type': 'str',
                'choices': ['pyats', 'native_json', 'native_xml']
            },
        'ignore_parser_errors':
            {
                'type': 'bool',
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
        self._cmd_dict = None
        self._errors = []
        self._facts = {}
        self._filters = {}
        self._ignore_parser_errors = False
        self._network_os = None
        self._commands = None
        self._module_name = None
        self._engine = None
        self._pyats_device = None
        self._result = None
        self._result_details = []
        self._templar_filters = Templar(loader=None).environment.filters


    def _add_facts(self, parsed):
        if isinstance(parsed, list):
            for chunk in parsed:
                self._facts = dict_merge(self._facts, chunk)
        elif isinstance(parsed, dict):
            for k, val in parsed.items():
                if k in self._facts:
                    # pylint: disable=C0123
                    if type(self._facts[k]) != type(val):
                        message = ("Cannot merge '{}' and '{}'"
                                   " for facts key '{fkey}'. Ensure"
                                   " all values for '{fkey}' are of"
                                   " the same type".format(
                                       type(self._facts[k]).__name__,
                                       type(val).__name__,
                                       fkey=k))
                        raise AnsibleError(message)
            self._facts = dict_merge(self._facts, parsed)

    def _check_argspec(self):
        # pylint: disable=W0212
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({'ANSIBLE_MODULE_ARGS': self._task.args}))
        # pylint: enable=W0212
        spec = {k: v for k, v in ARGSPEC.items() if k in VALID_MODULE_KWARGS}
        basic.AnsibleModule.fail_json = self._fail_json
        basic.AnsibleModule(**spec)

    def _check_engine(self):
        if self._engine == "pyats":
            if not PY3:
                self._errors.append("Genie requires Python 3")
            if not HAS_GENIE:
                self._errors.append("Genie not found. Run 'pip install genie'")
            if not HAS_PYATS:
                self._errors.append("pyATS not found. Run 'pip install pyats'")
        elif self._engine == "native_xml":
            if not HAS_XMLTODICT:
                self._errors.append("xmltodict not found."
                                    " Run 'pip install xmltodict'")

    def _check_network_os(self):
        if not self._network_os:
            self._errors.append("'network_os' must be provided or"
                                "ansible_network_os set for this host")

    def _check_commands_against_pyats(self):
        network_os = self._task.args.get('network_os') or self._network_os
        self._pyats_device = Device("uut", os=network_os)
        self._pyats_device.custom.setdefault("abstraction",
                                             {})["order"] = ["os"]
        self._pyats_device.cli = AttrDict({"execute": None})
        for command in self._commands:
            try:
                get_parser(command['command'], self._pyats_device)
            except Exception:  # pylint: disable=W0703
                self._errors.append("Unable to find parser for command "
                                    "'{}' for {}".format(command['command'],
                                                         network_os))
        self._check_for_errors()

    def _check_for_errors(self):
        if self._errors:
            raise AnsibleError(".  ".join(self._errors))

    def _check_module_name(self):
        if self._module_name not in self._shared_loader_obj.module_loader:
            self._errors.append("{} is not supported".format(self._network_os))
        self._check_for_errors()

    def _check_transforms(self):
        for command in self._commands:
            for transform in command.get('transform', []):
                if 'name' not in transform:
                    self._errors.append(
                        "Transform '{}' missing `name` in command '{}'"
                        .format(transform['name'], command['command']))
                    continue
                if not self._filters.get(transform['name']):
                    self._errors.append(
                        "Transform '{}' not found in command '{}'"
                        .format(transform['name'], command['command']))

    def _fail_json(self, msg):
        msg = msg.replace('(basic.py)', self._task.action)
        raise AnsibleModuleError(msg)

    def _load_filters(self):
        filter_loader = getattr(self._shared_loader_obj, 'filter_loader')
        for fpl in filter_loader.all():
            self._filters.update(fpl.filters())
        for command in self._commands:
            for transform in command.get('transform', []):
                if 'name' not in transform:
                    self._errors.append(
                        "Transform '{}' missing `name` in command '{}'"
                        .format(transform['name'], command['command']))
                    continue
                if hasattr(self._task, 'collections'):
                    for collection in self._task.collections:
                        full_name = "{}.{}".format(collection, transform['name'])
                        filterfn = self._templar_filters.get(full_name)
                        if filterfn:
                            self._filters[transform['name']] = filterfn
                            break
                if transform['name'] not in self._filters:
                    full_name = "{}.{}".format('nmake.jetpack',
                                               transform['name'])
                    filterfn = self._templar_filters.get(full_name)
                    if filterfn:
                        self._filters[transform['name']] = filterfn

    def _set_send_commands(self):
        if self._engine == 'native_json':
            if self._network_os == "junos":
                append_json = " | display json"
            else:
                append_json = " | json"
            for command in self._commands:
                command['command'] += append_json
        elif self._engine == 'native_xml':
            append_xml = " | xmlout"
            for command in self._commands:
                command['command'] += append_xml

    def _parse_stdout(self):
        for command in self._commands:
            stdout = self._cmd_dict.get(command['command'])
            entry = {"command": command['command']}
            try:
                if self._engine == 'pyats':
                    parsed = self._pyats_device.parse(command['command'],
                                                      output=stdout)
                elif self._engine == 'native_json':
                    if isinstance(stdout, str):
                        parsed = {}
                    else:
                        parsed = stdout
                elif self._engine == 'native_xml':
                    if not stdout:
                        parsed = {}
                    else:
                        splitted = stdout.splitlines()
                        if splitted[-1] == ']]>]]>':
                            stdout = '\n'.join(splitted[:-1])
                        parsed = xmltodict.parse(stdout)

            except Exception:  # pylint: disable=W0703
                msg = ("Unable to parse output for command '{}' for {}"
                       .format(command['command'], self._network_os))
                if self._ignore_parser_errors:
                    display.warning(msg)
                    parsed = {}
                else:
                    self._errors.append(msg)
            self._check_for_errors()

            parsed = self._run_transforms(command, parsed)
            entry['parsed'] = parsed
            self._result_details.append(entry)
            if command.get('set_fact'):
                self._add_facts(parsed)

    def _run_commands(self):
        commands = list(set(command['command'] for command in self._commands))
        new_module_args = {"commands": commands}
        res = self._execute_module(module_name=self._module_name,
                                   module_args=new_module_args,
                                   task_vars={}, tmp=None)
        if res.get('failed'):
            raise AnsibleError("Failure while running command on"
                               " device: {}".format(res['msg']))
        self._cmd_dict = {c: res['stdout'][idx]
                          for idx, c in enumerate(commands)}

    def _run_transforms(self, command, parsed):
        for transform in command.get('transform', []):
            filterfn = self._filters.get(transform['name'])
            del transform['name']
            parsed = filterfn(parsed, **transform)
        return parsed

    def _set_vars(self, task_vars):
        self._network_os = task_vars.get('ansible_network_os')
        self._commands = self._task.args.get('commands')
        self._module_name = '{}_command'.format(self._network_os)
        self._engine = self._task.args.get('engine')
        self._ignore_parser_errors = self._task.args.get('ignore_parser_errors')

    def run(self, tmp=None, task_vars=None):

        # pylint: disable=W0212
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._check_argspec()
        self._set_vars(task_vars)
        self._check_engine()
        self._check_network_os()
        self._check_for_errors()

        self._load_filters()
        self._check_transforms()
        self._check_for_errors()

        self._check_module_name()
        if self._engine == 'pyats':
            self._check_commands_against_pyats()
        self._check_for_errors()

        self._set_send_commands()
        self._run_commands()
        self._parse_stdout()

        current_facts = task_vars.get('vars', {}).get('ansible_facts', {})
        new_facts = dict_merge(current_facts, self._facts)
        self._result.update({
            'ansible_facts': new_facts,
            'details': self._result_details
        })

        return self._result
