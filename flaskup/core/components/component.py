from collections import Iterable
from functools import reduce as _reduce
from operator import add as _add

from flaskup.typing import Renderable, List, Optional, RenderReturnValue
from .includes import ComponentIncludes

REDUCE_INCLUDES_MAX_DEPTH = 5


class AbstractComponent(Renderable):
    def __init__(self, component_includes: ComponentIncludes = None):
        from flaskup import current_flaskup_app
        # self.app =
        self.app = current_flaskup_app
        self.app_config = self.app.config
        self.component_includes = component_includes or ComponentIncludes()

    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()


class AbstractContainer(AbstractComponent):
    def __init__(self, children: List[AbstractComponent]):
        container_includes = _reduce(_add, (c.component_includes for c in children))
        super(AbstractContainer, self).__init__(component_includes=container_includes)
        self.children = children

    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()

    def render_children(self) -> RenderReturnValue:
        return ''.join(c.render() for c in self.children)


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
