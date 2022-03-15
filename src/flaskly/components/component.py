from abc import ABC, abstractmethod
from collections import Iterable
from functools import reduce as _reduce
from operator import add as _add

from flaskly.includes import ComponentIncludes
from flaskly.typing import Optional, RenderReturnValue, ContainerChildren

REDUCE_INCLUDES_MAX_DEPTH = 5


class Renderable(ABC):
    """
    An Interface for renderable objects
    """

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        """Return the rendered object as a string or :class:`RenderResponse` object.

        :param options: namespace used in rendering the object. May be passed to the template engine.
        """
        raise NotImplementedError()


class AbstractComponent(Renderable):
    """
    AbstractComponent
    """
    component_includes = None

    def __init__(self, component_includes: ComponentIncludes = None):
        # self.app =
        # self.app = current_flaskly_app
        # self.app_config = self.app.config
        if component_includes:
            self.component_includes = component_includes
        # TODO: bootstrap components (get version from current app, raise if not included)

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()


class AbstractContainer(AbstractComponent):
    def __init__(self, children: ContainerChildren):
        if not isinstance(children, list):
            children = [children]
        components = [c.component_includes for c in children if
                      isinstance(c, AbstractComponent) and c.component_includes is not None]
        container_includes = None
        if components:
            container_includes = _reduce(_add, components)
        super(AbstractContainer, self).__init__(component_includes=container_includes)
        self.children = children

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()

    def render_children(self) -> RenderReturnValue:
        return ''.join(c.render() for c in self.children)


class NormalContainer(AbstractContainer):
    def __init__(self, children: ContainerChildren, prefix='', suffix=''):
        super(NormalContainer, self).__init__(children)
        self.prefix = prefix
        self.suffix = suffix

    def render(self, **options) -> RenderReturnValue:
        return self.prefix + self.render_children() + self.suffix


def reduce_includes(*includes_or_components) -> ComponentIncludes:
    def _reduce_includes(*args, depth=0) -> Optional[ComponentIncludes]:
        ret = None
        for itm in args:
            if isinstance(itm, Iterable) and depth < REDUCE_INCLUDES_MAX_DEPTH:
                itm = _reduce_includes(*itm, depth=depth + 1)
            elif isinstance(itm, Iterable):
                ValueError('includes max depth reached')

            if itm is None:
                continue

            if isinstance(itm, AbstractComponent):
                itm = itm.component_includes

            if isinstance(itm, ComponentIncludes):
                if ret is None:
                    ret = itm
                else:
                    ret += itm

        return ret

    reduced = _reduce_includes(*includes_or_components)
    if reduced is None:
        return ComponentIncludes()
    return reduced
