__all__ = ['AbstractNavigationProvider', 'DefaultNavigationProvider', 'StaticNavigationProvider']
from abc import ABC, abstractmethod

from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import NavigationMapInit


class AbstractNavigationProvider(ABC):
    @abstractmethod
    def generate_navigation(self) -> NavigationMapInit:
        raise NotImplementedError()


class DefaultNavigationProvider(AbstractNavigationProvider):
    def generate_navigation(self) -> NavigationMapInit:
        return _app.config.navigation_provider.generate_navigation()


class StaticNavigationProvider(AbstractNavigationProvider):
    def __init__(self, navigation_map):
        super(StaticNavigationProvider, self).__init__()
        self.navigation_map = navigation_map

    def generate_navigation(self) -> NavigationMapInit:
        return self.navigation_map
