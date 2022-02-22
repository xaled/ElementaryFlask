from abc import ABC

from flaskup.typing import RenderReturnValue
from .component import AbstractComponent


class AbstractIcon(AbstractComponent, ABC):
    pass


class HTMLIcon(AbstractIcon):
    def __init__(self, html_code):
        super(HTMLIcon, self).__init__()
        self.html_code = html_code

    def render(self, **options) -> RenderReturnValue:
        return self.html_code
