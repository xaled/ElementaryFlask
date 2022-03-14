from flaskly.globals import current_flaskly_app as _app
from .state import form_json_state


def render_default(form):
    return _app.core_jinja_env.render_template("forms/default_form.html", form=form)


def render_stateful(form):
    return _app.core_jinja_env.render_template("forms/stateful_form.html",
                                               form=form, form_state=form_json_state(form))


FORM_RENDERING_TYPES = {
    'default': render_default,
    'stateful': render_stateful,
}
