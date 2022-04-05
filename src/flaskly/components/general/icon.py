__all__ = ['AbstractIcon', 'HTMLIcon', 'IClassIcon']
from abc import ABC

from flaskly.typing import RenderReturnValue
from .. import AbstractComponent


class AbstractIcon(AbstractComponent, ABC):
    def __init__(self, icon_class=None):
        super(AbstractIcon, self).__init__()
        self.icon_class = icon_class


class HTMLIcon(AbstractIcon):
    def __init__(self, html_code, icon_class=None):
        super(HTMLIcon, self).__init__(icon_class)
        self.html_code = html_code

    def render(self, **options) -> RenderReturnValue:
        return self.html_code


class IClassIcon(HTMLIcon):
    def __init__(self, icon_class):
        super(IClassIcon, self).__init__(f'<i class="{icon_class}"></i>', icon_class=icon_class)
