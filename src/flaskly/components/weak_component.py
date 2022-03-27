from abc import ABC, abstractmethod

from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import RenderReturnValue
from .component import AbstractComponent


class AbstractRenderer(AbstractComponent, ABC):
    @abstractmethod
    def render(self, weak_component: "AbstractWeakComponent", **options) -> RenderReturnValue:
        raise NotImplementedError()


class ReprRenderer(AbstractRenderer):
    def render(self, weak_component: "AbstractWeakComponent", **options) -> RenderReturnValue:
        return repr(weak_component)


class AbstractWeakComponent(AbstractComponent):
    default_renderer: AbstractRenderer = ReprRenderer()
    _renderer: AbstractRenderer = None

    def render(self, **options) -> RenderReturnValue:
        return self.find_renderer().render(self, **options)

    @staticmethod
    def get_renderer():
        return None

    @classmethod
    def find_renderer(cls) -> AbstractRenderer:
        cls._renderer = cls._renderer or _app.find_renderer(cls) or cls.get_renderer() or cls.default_renderer
        if cls._renderer is None:
            raise Exception('No renderer is found')
        return cls._renderer
