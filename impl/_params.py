import logging
import re

from _util import assert_raises, IronbotException, Delay
from _attr import AttributeDict



class IronbotParametersException(IronbotException):
    pass


def pop(params):
    """
    >>> p = [1, 2, 3]
    >>> pop(p), p
    (1, [2, 3])
    >>> pop(p), p
    (2, [3])
    >>> pop(p), p
    (3, [])
    >>> assert_raises(IronbotParametersException, pop, p)
    """
    try:
        p = params[0]
    except IndexError:
        raise IronbotParametersException("Expected a parameter, found nothing")
    del params[0]
    return p


def pop_re(params):
    """
    >>> bool(pop_re(['1']).match('1'))
    True
    >>> bool(pop_re(['1']).match('0'))
    False
    """
    return re.compile(pop(params))


BOOL_VALS = {"TRUE": True, "FALSE": False}


def str_2_bool(s):
    try:
        return BOOL_VALS[s.upper()]
    except:
        raise IronbotException("Cannot cast to bool: '%s'" % s)


def pop_bool(params):
    """
    >>> pop_bool(['fAlSe'])
    False
    >>> pop_bool(['TrUe'])
    True
    >>> try: pop_bool(['TrAlSe'])
    ... except IronbotParametersException: print "YES!"
    YES!
    """
    try:
        s = pop(params)
        return BOOL_VALS[s.upper()]
    except KeyError:
        raise IronbotParametersException("Expected a value of type bool, got '%s'" % s)


def pop_menu_path(params):
    res = []
    while params:
        v = pop(params)
        if v == '<END>':
            break
        res.append(v)
    return res


def pop_type(type):
    """
    >>> p = [1, ' 2.0 ', '', 's']
    >>> pop_type(float)(p) == 1.0, pop_type(float)(p) == 2.0
    (True, True)
    >>> assert_raises(IronbotParametersException, pop_type(float), p)
    """
    def _pop(params):
        p = pop(params)
        try:
            return type(p)
        except ValueError:
            raise IronbotParametersException("Cannot transfer '%s' to float" % p)
    return _pop


def fixed_val(val):
    """
    >>> p = [1, ' 2.0 ', '', 's']
    >>> fixed_val(3)(p), p
    (3, [1, ' 2.0 ', '', 's'])
    """
    return lambda _: val


def parse_positional(rules, param_list):
    """
    >>> pl = ['a', 'b', '1']
    >>> rules = (pop, pop, pop_type(int))
    >>> parse_positional(rules, pl), pl
    (['a', 'b', 1], [])
    """
    res = []
    for r in rules:
        res.append(r(param_list))
    return res


SET_PREFIX = 'set_'
RE_PREFIX = 're_'


def get_attr_and_action(s, default_action):
    """
    >>> get_attr_and_action(' b  j  ', 'q')
    ('j', 'b')
    >>> get_attr_and_action(' b  j  r', 'q')
    (None, None)
    >>> get_attr_and_action(' b  ', 'q')
    ('b', 'q')
    """
    s = [v for v in s.split(' ') if v]
    if len(s) == 2:
        return s[1], s[0]
    if len(s) == 1:
        return s[0], default_action
    return None, None


def parse_named(pdict, attr_dict, a, default_action='wait', insert_attr_dict=False):
    """
    >>> from math import fabs
    >>> pd = {'a': (('a1', fixed_val(0)),), 'b': (('b1', fixed_val(0)), ('b2', pop_type(Delay)))}
    >>> def printer(obj, v):
    ...     print obj
    ...     return obj["attr1"] + v
    >>> ad = AttributeDict()
    >>> ad.add_attr("attr1", 0, get=(pop_type(int),))
    >>> ad.add_class_attr("dict", "attr1", get=printer)
    >>> assert parse_named(pd, ad, ['a'], 'get') == {'a1': 0}
    >>> v = parse_named(pd, ad, ['a', 'b', '1s'], 'get'); assert fabs(v['b2'].value - 1) < 0.0001
    >>> del v['b2']; assert v == {'a1': 0, 'b1': 0}
    >>> p = parse_named(pd, ad, ['attr1', '2'], 'get'); p
    {'attributes': {'get': [('attr1', [2])]}}
    >>> ad.action({"attr1": 1}, 'attr1', 'get', p['attributes']['get'][0][1])
    {'attr1': 1}
    3
    >>> ad = AttributeDict()
    >>> ad.add_attr("attr1", 0, get=(pop_type(int),), set=(pop,))
    >>> ad.add_class_attr("dict", "attr1", get=printer, set=printer)
    >>> p = parse_named(pd, ad, ['set attr1', '2'], 'get'); p
    {'attributes': {'set': [('attr1', ['2'])]}}
    """
    res = {}
    while a:
        name = pop(a)
        rule = pdict.get(name, None)
        if rule:
            for rname, rproc in rule:
                if rname in res:
                    raise IronbotParametersException("'%s' value is redefined by parameter '%s'" % (rname, name))
                res[rname] = rproc(a)
        else:
            try:
                attr, action = get_attr_and_action(name, default_action)
                if attr is None:
                    raise IronbotParametersException("Attribute and action value cannot be parsed: '%s'" % name)
                if 'attributes' not in res:
                    res['attributes'] = {}
                if action not in res['attributes']:
                    res['attributes'][action] = []
                res['attributes'][action].append((attr, attr_dict.read_params(attr, action, a)))
            except KeyError:
                raise IronbotParametersException("Got an unknown attribute parameter: '%s'" % name)
    if insert_attr_dict:
        res['attr_dict'] = attr_dict
    return res


EMPTY_ATTRDICT = AttributeDict()


def robot_args((pos, d), attr_dict=EMPTY_ATTRDICT, default_action='wait', insert_attr_dict=False):
    """
    >>> def f(*a, **kw): return a, kw
    >>> ad = AttributeDict()
    >>> ad.add_attr("attr1", 0, get=(pop_type(int),))
    >>> def printer(obj, v):
    ...     print obj
    ...     return obj[0] + v
    >>> ad.add_class_attr("list", "attr1", get=printer)
    >>> rules = ((pop, pop, pop_type(int)), {'a': (('a1', fixed_val(0)),), 'b': (('b1', fixed_val(0)), ('b2', pop_type(Delay)))})
    >>> g = robot_args(rules, ad, 'get')(f)
    >>> g('a', 'b', '1', 'a')
    (('a', 'b', 1), {'a1': 0})
    >>> g('a', 'b', '1', 'attr1', '10')
    (('a', 'b', 1), {'attributes': {'get': [('attr1', [10])]}})
    >>> g = robot_args(rules, ad, 'get', True)(f)
    >>> res = g('a', 'b', 1)
    >>> assert id(res[1]['attr_dict']) == id(ad)
    """
    def decorator(f):
        def callable(*a):
            params = list(a)
            fixed = parse_positional(pos, params)
            named = parse_named(d, attr_dict, params, default_action, insert_attr_dict)
            return f(*fixed, **named)
        callable.__doc__ = f.__doc__
        return callable
    return decorator


