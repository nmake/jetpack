from ansible.errors import AnsibleFilterError


def do_yaql(data, expression):
    try:
        import yaql
    except ImportError:
        raise AnsibleFilterError("The yaql filter plugin require yaql."
                                 " 'pip install yaql'")

    engine = yaql.factory.YaqlFactory().create()  # pylint: disable=E1101
    expression = engine(expression)
    result = expression.evaluate(data=data)
    return result


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'yaql': do_yaql
        }
