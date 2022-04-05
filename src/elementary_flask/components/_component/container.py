__all__ = ['AbstractContainer', 'NormalContainer']
from abc import ABC, abstractmethod

from elementary_flask.typing import RenderReturnValue, ContainerChildren
from .component import AbstractComponent, render


class AbstractContainer(AbstractComponent, ABC):
    def __init__(self, children: ContainerChildren):
        if not isinstance(children, list) and not isinstance(children, tuple) and not isinstance(children, set):
            children = (children,)
        elif not isinstance(children, tuple):
            children = tuple(children)
        # components = [c.component_includes for c in children if
        #               isinstance(c, AbstractComponent) and c.component_includes is not None]
        # container_includes = None
        # if components:
        #     container_includes = _reduce(_add, components)
        # super(AbstractContainer, self).__init__(component_includes=container_includes)
        self.children = children

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()


class NormalContainer(AbstractContainer):
    def __init__(self, children: ContainerChildren, prefix='', suffix='', separator=''):
        super(NormalContainer, self).__init__(children)
        self.prefix = prefix
        self.suffix = suffix
        self.separator = separator

    def render(self, **options) -> RenderReturnValue:
        # return self.prefix + self.separator.join(render(c) for c in self.children) + self.suffix
        # return render(self.prefix, *self.children, self.suffix)
        first = True
        res = self.prefix
        for c in self.children:
            if first:
                res += render(c)
                first = False
            else:
                res += self.separator + render(c)
        return res + self.suffix
