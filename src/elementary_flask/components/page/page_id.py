# from urllib.parse import quote_plus
#
#
# def _assert_naming_convention(param):
#     assert '=' not in param
#     assert '&' not in param
#
#
# def page_id(endpoint, **params):
#     _assert_naming_convention(endpoint)
#     ret = endpoint
#     keys = sorted(list(params.keys()))
#     for k in keys:
#         v = params[k]
#         _assert_naming_convention(k)
#         ret += f'&{k}={quote_plus(v)}'
