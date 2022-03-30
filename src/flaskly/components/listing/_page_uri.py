from urllib.parse import urlencode


def page_uri(*, page=None, filters=None, query=None):
    t = list()
    for k, v in (("page", page), ('filters', filters), ('query', query)):
        if v and (k != 'page' or v != 1):
            t.append((k, v), )
    return '?' + urlencode(t)  # if t else '#'
