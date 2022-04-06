__all__ = ['Renderable', 'AbstractComponent', 'render', 'RenderException']

from abc import ABC, abstractmethod
from collections.abc import Iterable

# from .markup_plus import MarkupPlus, RenderException # , RenderError,
from markupsafe import Markup

from elementary_flask.typing import RenderReturnValue, Block


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
    error_strategy = 'safe'
    # component_includes = None

    # def __init__(self, component_includes: ComponentIncludes = None):
    #     # self.app =
    #     # self.app = current_elementary_flask_app
    #     # self.app_config = self.app.config
    #     if component_includes:
    #         self.component_includes = component_includes
    #     # TODO: bootstrap components (get version from current app, raise if not included)

    @abstractmethod
    def render(self, /, format_spec=None, **options) -> RenderReturnValue:
        raise NotImplementedError()

    def __repr__(self):
        return self.render()

    def __str__(self):
        return self.render()

    def __html__(self):
        return self.render()

    def __html_format__(self, format_spec=None):
        return self.render(format_spec=format_spec)

    def __call__(self, /, format_spec=None, **options) -> RenderReturnValue:
        return self.render(format_spec=format_spec, **options)


def _render(block: Block, **options) -> RenderReturnValue:
    # if isinstance(block, str) or isinstance(block, MarkupPlus) or isinstance(block, Markup):
    if isinstance(block, str) or isinstance(block, Markup):
        return block
    try:
        if isinstance(block, Renderable) or callable(getattr(block, 'render', None)):
            return block.render(**options)
        if callable(block):
            return block(**options)
        if hasattr(block, '__html_format__') and ('format_spec' in options or not hasattr(block, '__html__')):
            return block.__html_format__(options.get('format_spec', None))
        if hasattr(block, '__html__'):
            return block.__html__()
    except Exception as e:
        if getattr(block, 'error_strategy', None) == 'safe':  # TODO override with app error strategy
            return 'Error'
        raise RenderException('Error while rendering: ', e)
    raise RenderException('Unsupported block type')


def render(*blocks: Iterable[Block], separator=None) -> RenderReturnValue:
    res = Markup()
    first = True
    no_separator = not separator
    for b in blocks:
        if no_separator or first:
            res += _render(b)
        else:
            res += separator + _render(b)
        first = False
    return res


class RenderException(Exception):
    pass
