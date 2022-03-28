from flaskly.components import HTTPError
from flaskly.typing import RenderReturnValue, Navigation
from ._jinja2_env import jinja2_env


def render_http_error(http_error: HTTPError, /, **options) -> RenderReturnValue:
    return jinja2_env.render_template('components/error.html',
                                      error_message=http_error.error_message,
                                      status_code=http_error.status_code,
                                      error_color='danger' if http_error.status_code >= 500 else 'warning',
                                      )


def render_navigation(navigation: Navigation, /, **options) -> RenderReturnValue:
    return jinja2_env.render_template('components/navigation.html',
                                      navigation=navigation,
                                      )
