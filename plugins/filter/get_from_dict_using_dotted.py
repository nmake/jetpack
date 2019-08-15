from functools import reduce  # forward compatibility for Python 3
import operator

def to_int(str):
    try:
        return int(str)
    except ValueError:
        return str

def get_from_dict_using_dotted(data_dict, keypath):
    """ get from dictionary
    """
    import q
    if keypath == '':
        return data_dict
    map_list = [to_int(x) for x in keypath.split('.')]
    q(map_list)
    try:
        return reduce(operator.getitem, map_list, data_dict)
    except KeyError:
        return {}


class FilterModule(object):
    ''' Network interface filter '''

    def filters(self):
        return {
            'get_from_dict_using_dotted': get_from_dict_using_dotted
        }
