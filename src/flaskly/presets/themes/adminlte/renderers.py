from flaskly.components import AbstractRenderer, HTTPError
from flaskly.typing import RenderReturnValue
from ._jinja2_env import jinja2_env


class HTTPErrorRenderer(AbstractRenderer):
    def render(self, weak_component: HTTPError, **options) -> RenderReturnValue:
        return jinja2_env.render_template('components/error.html',
                                          error_message=weak_component.error_message,
                                          status_code=weak_component.status_code,
                                          error_color='danger' if weak_component.status_code >= 500 else 'warning',
                                          )
