from functools import reduce as _reduce
from operator import add as _add

from flaskup.typing import Renderable, List, ChildrenRenderable
from .includes import ComponentIncludes


class AbstractComponent(Renderable):
    def __init__(self, component_includes: ComponentIncludes = None):
        from flaskup import current_flaskup_app
        # self.app =
        self.app = current_flaskup_app
        self.app_config = self.app.config
        self.component_includes = component_includes or ComponentIncludes()

    def render(self) -> str:
        raise NotImplementedError()


class AbstractContainer(AbstractComponent, ChildrenRenderable):
    def __init__(self, children: List[AbstractComponent]):
        container_includes = _reduce(_add, (c.component_includes for c in children))
        super(AbstractContainer, self).__init__(component_includes=container_includes)
        self.children = children

    def render(self) -> str:
        raise NotImplementedError()

    def render_children(self) -> str:
        return ''.join(c.render() for c in self.children)
