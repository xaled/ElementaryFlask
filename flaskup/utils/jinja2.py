from flask.globals import session, request, g
from flask.helpers import get_flashed_messages, url_for
from jinja2 import Environment, FileSystemLoader

from flaskup.globals import current_flaskup_app as _app


class Jinja2Env:
    def __init__(self, templates_path=None, parent=None, loader=None, autoescape=True, auto_reload=True,
                 flaskup_app=None,
                 **options, ):
        loader = loader or FileSystemLoader(templates_path)
        self.jinja2_env = Environment(loader=loader, autoescape=autoescape, auto_reload=auto_reload, **options)
        self.jinja2_env.globals.update(
            url_for=url_for,
            get_flashed_messages=get_flashed_messages,
            request=request,
            session=session,
            g=g,
        )
        self.parent = parent
        self.flaskup_app = flaskup_app
        if self.flaskup_app:
            self._update_flaskup_globals()

    def _update_flaskup_globals(self):
        self.jinja2_env.globals.update(
            config=_app.flask_app.config,
            flaskup_config=_app.config,
            navigation_handler=_app.navigation_handler,

        )
        # TODO app filters

    def render_template(self, template_name, **options):
        if not self.flaskup_app:
            self.flaskup_app = _app
            self._update_flaskup_globals()
        return self.jinja2_env.get_template(template_name).render(**options)
