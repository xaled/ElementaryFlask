from dataclasses import dataclass

from wtforms import Form

from flaskly.typing import FormActionInit
from .state import form_state


class FormAction:
    def __init__(self, action, **params):
        self.action = action
        self.params = params

    def to_dict(self):
        return {
            "action": self.action,
            "params": self.params,
        }


@dataclass
class FormResponse:
    actions: FormActionInit

    def __post_init__(self):
        if isinstance(self.actions, FormAction):
            self.actions = [self.actions]
        elif isinstance(self.actions, Form):  # TODO stateless & submit forms
            self.actions = [update_form(self.actions)]

    def to_dict(self):
        return {'actions': [a.to_dict() for a in self.actions]}


def redirect(uri):
    return FormAction('redirect', destination=uri)


def jseval(js_code):
    return FormAction('eval', code=js_code)


def toast(message, message_type='error', message_title='', sticky=False, timeout=10):
    return FormAction('toast', message=message, message_type=message_type, message_title=message_title,
                      sticky=sticky, timeout=timeout)


def replace_html(html):
    return FormAction('replace', html=html)


def update_state(**new_state):
    return FormAction('state', new_state=new_state)


def update_form(form):
    return update_state(formState=form_state(form))


def error(error_msg):
    return toast(error_msg, message_type='error', message_title='Error')
