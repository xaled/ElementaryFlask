__all__ = ['NormalContainer', 'ContainerMixin']  # 'AbstractContainer']

from elementary_flask.typing import RenderReturnValue, ContainerChildren
from .component import render
from .element_component import AbstractHTMLElementComponent


def _init_children(children):
    if not isinstance(children, list) and not isinstance(children, tuple) and not isinstance(children, set):
        children = (children,)
    elif not isinstance(children, tuple):
        children = tuple(children)
    return children


class ContainerMixin:
    children = []

    def __iter__(self):
        return self.children.__iter__()


class NormalContainer(AbstractHTMLElementComponent, ContainerMixin):
    separator = None

    def __init__(self, children: ContainerChildren, /, *, extra_classes=None, tag_attributes=None,
                 separator=None):
        tag_attributes = tag_attributes or dict()
        super(NormalContainer, self).__init__(extra_classes=extra_classes, **tag_attributes)
        self.children = _init_children(children)
        if separator:
            self.separator = separator

    def render_inner_html(self, **options) -> RenderReturnValue:
        return render(*self.children)
