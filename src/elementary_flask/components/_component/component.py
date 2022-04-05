__all__ = ['Renderable', 'AbstractComponent', 'render']
from abc import ABC, abstractmethod
from collections.abc import Iterable

from elementary_flask.typing import RenderReturnValue, Block
from .render_response import RenderResponse, RenderError


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

    # component_includes = None

    # def __init__(self, component_includes: ComponentIncludes = None):
    #     # self.app =
    #     # self.app = current_elementary_flask_app
    #     # self.app_config = self.app.config
    #     if component_includes:
    #         self.component_includes = component_includes
    #     # TODO: bootstrap components (get version from current app, raise if not included)

    @abstractmethod
    def render(self, **options) -> RenderReturnValue:
        raise NotImplementedError()

    def __str__(self):
        return self.render()

    def __call__(self, **options) -> RenderReturnValue:
        return self.render(**options)


def _render(block: Block, **options) -> RenderReturnValue:
    if isinstance(block, str) or isinstance(block, RenderResponse):
        return block
    if isinstance(block, Renderable) or callable(getattr(block, 'render', None)):
        return block.render(**options)
    if callable(block):
        return block(**options)
    return RenderError('Unsupported block type')


def render(*blocks: Iterable[Block]) -> RenderReturnValue:
    res = RenderResponse(content="")
    for b in blocks:
        res += _render(b)
    return res
