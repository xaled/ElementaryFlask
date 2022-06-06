__all__ = ['AbstractHTMLElementComponent']

from abc import ABC

from wtforms.widgets.core import html_params
from markupsafe import Markup

from .component import AbstractComponent
from elementary_flask.typing import RenderReturnValue


class AbstractHTMLElementComponent(AbstractComponent, ABC):
    html_params = staticmethod(html_params)
    void_element = False
    html_tag = None
    classes = None

    def __init__(self, extra_classes=None, **attributes):
        self.base_attributes = attributes or dict()
        if self.classes:
            self.base_attributes.setdefault('class', self.classes)
        if extra_classes:
            self.base_attributes['class'] = _append_classes(self.base_attributes.get('class', None), extra_classes)

    def render_start_tag(self, extra_classes=None, **attributes):
        _attributes = dict(self.base_attributes)
        _attributes.update(attributes)
        if extra_classes:
            _attributes['class'] = _append_classes(_attributes.get('class', None), extra_classes)
        return Markup("<%s %s>" % (self.html_tag, self.html_params(**_attributes)))

    def render_end_tag(self):
        return Markup('</%s>' % self.html_tag)

    def render(self, /, extra_classes=None, tag_attributes=None, **options) -> RenderReturnValue:
        tag_attributes = tag_attributes or dict()
        if self.void_element:
            return self.render_start_tag(extra_classes=extra_classes, **tag_attributes)

        return (
                self.render_start_tag(extra_classes=extra_classes, **tag_attributes)
                + self.render_inner_html() + self.render_end_tag()
        )

    def render_inner_html(self, **options) -> RenderReturnValue:
        return ""


def _append_classes(*classes_strings):
    ret = [c.strip() for c in classes_strings if c and c.strip()]
    if ret:
        return ' '.join(ret)
    return None
