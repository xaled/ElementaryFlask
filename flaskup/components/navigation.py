from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from flaskup.globals import current_flaskup_app as _app
from flaskup.typing import RenderReturnValue, Optional, List, NavigationData, NavigationItem
from .component import AbstractComponent
from .icon import AbstractIcon


class AbstractNavigationHandler(ABC):
    @abstractmethod
    def handle_nav(self) -> NavigationData:
        raise NotImplementedError()


class AbstractNavigation(AbstractComponent):
    def __init__(self, navigation_handler: AbstractNavigationHandler = None):
        super().__init__()
        self.navigation_handler = navigation_handler or DefaultNavigationHandler()

    def render(self, **options) -> RenderReturnValue:
        nav_data = self.navigation_handler.handle_nav()
        return self.render_nav(nav_data, **options)

    def render_nav(self, nav_data: NavigationData, **options) -> RenderReturnValue:
        raise NotImplementedError()


class DefaultNavigationHandler(AbstractNavigationHandler):
    def handle_nav(self) -> NavigationData:
        return _app.navigation_handler.handle_nav()


class StaticNavigationHandler(AbstractNavigationHandler):
    def __init__(self, navigation_map):
        super(StaticNavigationHandler, self).__init__()
        self.navigation_map = navigation_map

    def handle_nav(self) -> NavigationData:
        return self.navigation_map


@dataclass
class NavigationLink:
    title: str
    icon: Optional[AbstractIcon] = None
    link: Optional[str] = None
    endpoint: Optional[str] = None
    params: Optional[dict] = None
    disabled: bool = False

    def __post_init__(self):
        if not self.link and not self.endpoint:
            raise ValueError("link or endpoint should be set ")

    def get_link(self):
        return self.link or _app.url_for(self.endpoint, **self.params)


@dataclass
class NavigationGroup:
    title: str
    icon: Optional[AbstractIcon] = None
    items_list: List[NavigationItem] = field(default_factory=list)


class NavigationSeparator:
    pass
