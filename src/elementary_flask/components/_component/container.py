__all__ = ['NormalContainer', ]  # 'AbstractContainer']

from elementary_flask.typing import RenderReturnValue, ContainerChildren
from .component import render
from .element_component import AbstractHTMLElementComponent


def _init_children(children):
    if not isinstance(children, list) and not isinstance(children, tuple) and not isinstance(children, set):
        children = (children,)
    elif not isinstance(children, tuple):
        children = tuple(children)
    return children


# class AbstractContainer(AbstractComponent, ABC):
#     def __init__(self, children: ContainerChildren):
#
#         # components = [c.component_includes for c in children if
#         #               isinstance(c, AbstractComponent) and c.component_includes is not None]
#         # container_includes = None
#         # if components:
#         #     container_includes = _reduce(_add, components)
#         # super(AbstractContainer, self).__init__(component_includes=container_includes)
#         self.children = _init_children(children)
#
#     @abstractmethod
#     def render(self, **options) -> RenderReturnValue:
#         raise NotImplementedError()


class NormalContainer(AbstractHTMLElementComponent):
    separator = None

    def __init__(self, children: ContainerChildren, /, *, id_=None, extra_classes=None, tag_attributes=None,
                 separator=None):
        super(NormalContainer, self).__init__(id_=id_, extra_classes=extra_classes, tag_attributes=tag_attributes)
        self.children = _init_children(children)
        if separator:
            self.separator = separator

    def render_inner_html(self, **options) -> RenderReturnValue:
        return render(*self.children)
