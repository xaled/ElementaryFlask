def redirect(uri):
    return {
        'action': 'redirect',
        'destination': uri,
    }


def jseval(js_code):
    return {
        'action': 'eval',
        'code': js_code,
    }


def toast(msg):
    return {
        'action': 'toast',
        'msg': msg,
    }


def replace_html(html):
    return {
        'action': 'replace',
        'html': html,
    }
