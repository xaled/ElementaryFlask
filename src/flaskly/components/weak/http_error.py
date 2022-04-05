__all__ = ['DefaultHTTPErrorRenderer', 'HTTPError']
from html import escape as html_escape

from flaskly.typing import RenderReturnValue
from .. import AbstractWeakComponent, AbstractRenderer


class DefaultHTTPErrorRenderer(AbstractRenderer):
    def render(self, weak_component: "HTTPError", **options) -> RenderReturnValue:
        return f"""<h1 class="text-danger">{weak_component.status_code}: <small>{html_escape(
            weak_component.error_message)}</small></h1>"""


class HTTPError(AbstractWeakComponent):
    default_renderer = DefaultHTTPErrorRenderer()

    def __init__(self, status_code=500, error_message="Error"):
        super(HTTPError, self).__init__()
        self.status_code = status_code
        self.error_message = error_message
