from flaskup.globals import current_flaskup_app as _app


def render_default(form):
    return _app.core_jinja_env.render_template("forms/default_form.html", form=form)
