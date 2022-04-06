from flask.globals import session, request, g
from flask.helpers import get_flashed_messages, url_for
from jinja2 import Environment, FileSystemLoader
from jinja2.environment import DEFAULT_FILTERS
from markupsafe import Markup

from elementary_flask.globals import current_elementary_flask_app as _app


class Jinja2Env:
    def __init__(self, templates_path=None, parent=None, loader=None, autoescape=True, auto_reload=True,
                 elementary_flask_app=None,
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
        self.elementary_flask_app = elementary_flask_app
        if self.elementary_flask_app:
            self._update_elementary_flask_globals()

    def _update_elementary_flask_globals(self):
        self.jinja2_env.globals.update(
            config=_app.flask_app.config,
            elementary_flask_config=_app.config,
            # navigation_handler=_app.navigation_handler,

        )
        # app filters
        for k, v in _app.flask_app.jinja_env.filters.items():
            if k not in self.jinja2_env.filters or k in DEFAULT_FILTERS:
                self.jinja2_env.filters[k] = v

        # TODO Context Processors

    def render_template(self, template_name, **options):
        if not self.elementary_flask_app:
            self.elementary_flask_app = _app
            self._update_elementary_flask_globals()
        return Markup(self.jinja2_env.get_template(template_name).render(**options))
