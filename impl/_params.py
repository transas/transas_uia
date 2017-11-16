import logging
import re

#from _util import assert_raises, IronbotException, Delay
#from _attr import AttributeDict



class TuiaParametersException(Exception):
    pass


def parse(param):
    """
    >>> p = [1, 2, 3]
    >>> parse(p)
    [1, 2, 3]
    """
    return param


def parse_re(p):
    """
    >>> bool(parse_re('1').match('1'))
    True
    >>> bool(parse_re('1').match('0'))
    False
    """
    return re.compile(parse(p))


BOOL_VALS = {"TRUE": True, "FALSE": False, 'Y': True, 'N': False, 'YES': True, 'NO': False}


def str_2_bool(s):
    if isinstance(s, bool):
        return s
    try:
        return BOOL_VALS[s.upper()]
    except:
        raise TuiaParametersException("Cannot cast to bool: '%s'" % s)


def parse_bool(param):
    """
    >>> parse_bool('fAlSe')
    False
    >>> parse_bool('TrUe')
    True
    >>> try: parse_bool('TrAlSe')
    ... except TuiaParametersException: print("YES!")
    YES!
    """
    try:
        s = parse(param)
        if isinstance(s, bool):
            return s
        return BOOL_VALS[s.upper()]
    except KeyError:
        raise TuiaParametersException("Expected a value of type bool, got '%s'" % s)


def pop_menu_path(params):
    res = []
    while params:
        v = parse(params)
        if v == '<END>':
            break
        res.append(v)
    return res


def fixed_val(val):
    """
    >>> p = [1, ' 2.0 ', '', 's']
    >>> fixed_val(3)(p), p
    (3, [1, ' 2.0 ', '', 's'])
    """
    return lambda _: val


def parse_positional(rules, param_list):
    """
    >>> pl = ['a', 'b', 'YES']
    >>> rules = (parse, parse, parse_bool)
    >>> parse_positional(rules, pl), pl
    (['a', 'b', True], [])
    """
    res = []
    for r in rules:
        res.append(r(param_list[0]))
        del param_list[0]
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


def parse_named2(pdict, kw):
    """
    >>> pd = {'a': ('a1', fixed_val(0)), 'b': ('b1', fixed_val(0),)}
    >>> def printer(obj, v):
    ...     print(obj)
    ...     return obj["attr1"] + v
    >>> assert parse_named2(pd, {'a': None}) == {'a1': 0}
    >>> v = parse_named2(pd, {'a': None, 'b': 1})
    >>> assert v == {'a1': 0, 'b1': 0}
    """
    res = {}
    for name, v in kw.items():
        rule = pdict.get(name, None)
        if rule:
            rname, rproc = rule
            res[rname] = rproc(v)
    return res


def robot_args(pdescr):
    pos, d = pdescr
    def decorator(f):
        def callable(*a, **kw):
            params = list(a)
            fixed = parse_positional(pos, params)
            named = parse_named2(d, kw)
            return f(*fixed, **named)
        callable.__doc__ = f.__doc__
        return callable
    return decorator


