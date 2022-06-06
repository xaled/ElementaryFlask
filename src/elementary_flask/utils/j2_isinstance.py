_CLS_MAPPING = {
    # Elementary classes

    # Built-in Types
    'str': str,
    'bytes': bytes,
    'int': int,
    'float': float,
    'complex': complex,
    'bool': bool,
    'list': list,
    'tuple': tuple,
    'range': range,
    'dict': dict,
    'set': set,
}


def j2_isinstance(obj, cls_str):
    return isinstance(obj, _CLS_MAPPING.get(cls_str))
