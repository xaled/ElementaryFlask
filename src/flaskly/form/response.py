from .state import form_state


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


def update_state(**new_state):
    return {
        'action': 'state',
        'new_state': new_state,
    }


def update_form(form):
    return {
        'action': 'state',
        'new_state': form_state(form),
    }
