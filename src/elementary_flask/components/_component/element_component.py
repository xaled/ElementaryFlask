__all__ = ['AbstractHTMLElementComponent']

from abc import ABC, abstractmethod

from wtforms.widgets.core import html_params
from markupsafe import Markup

from .component import AbstractComponent
from elementary_flask.typing import RenderReturnValue


class AbstractHTMLElementComponent(AbstractComponent, ABC):
    html_params = staticmethod(html_params)
    void_element = False
    html_tag = None
    classes = None

    def __init__(self, id_=None, extra_classes=None, tag_attributes=None):
        self.base_attributes = tag_attributes or dict()
        self.base_attributes['class'] = _append_classes(self.classes, extra_classes)
        if id_:
            self.base_attributes['id'] = id_

    def render(self, /, id_=None, extra_classes=None, tag_attributes=None, **options) -> RenderReturnValue:
        attributes = dict(self.base_attributes)
        tag_attributes = dict(tag_attributes) if tag_attributes else dict()
        if id_:
            tag_attributes['id'] = id_
        if extra_classes:
            tag_attributes['class'] = _append_classes(tag_attributes.get('class', None), extra_classes)
        attributes.update(tag_attributes)

        ret = Markup("<%s %s>" % (self.html_tag, self.html_params(**attributes))) + self.render_inner_html()
        if not self.void_element:
            ret += Markup('</%s>' % self.html_tag)
        return ret

    @abstractmethod
    def render_inner_html(self, **options) -> RenderReturnValue:
        raise NotImplementedError()


def _append_classes(*classes_strings):
    ret = [c.strip() for c in classes_strings if c and c.strip()]
    if ret:
        return ' '.join(ret)
    return None
