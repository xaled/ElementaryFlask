from abc import ABC, abstractmethod
from dataclasses import dataclass
from html import escape as html_escape

from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import RenderReturnValue, Optional, List, NavigationData
from .component import AbstractComponent
from .icon import AbstractIcon


class AbstractNavigationHandler(ABC):
    @abstractmethod
    def generate_navmap(self) -> NavigationData:
        raise NotImplementedError()


class AbstractNavigation(AbstractComponent):
    def __init__(self, navigation_handler: AbstractNavigationHandler = None):
        super().__init__()
        self.navigation_handler = navigation_handler or DefaultNavigationHandler()

    def render(self, **options) -> RenderReturnValue:
        nav_data = self.navigation_handler.generate_navmap()
        return self.render_nav(nav_data, **options)

    def render_nav(self, nav_data: NavigationData, **options) -> RenderReturnValue:
        raise NotImplementedError()


class DefaultNavigationHandler(AbstractNavigationHandler):
    def generate_navmap(self) -> NavigationData:
        return _app.config.navigation_handler.generate_navmap()


class StaticNavigationHandler(AbstractNavigationHandler):
    def __init__(self, navigation_map):
        super(StaticNavigationHandler, self).__init__()
        self.navigation_map = navigation_map

    def generate_navmap(self) -> NavigationData:
        return self.navigation_map


@dataclass
class NavigationItem:
    title: str
    icon: Optional[AbstractIcon] = None
    link: Optional[str] = None
    endpoint: Optional[str] = None
    params: Optional[dict] = None
    disabled: bool = False
    navigation_type: str = 'link'


class NavigationLink(NavigationItem):
    def __init__(self,
                 title: str,
                 icon: Optional[AbstractIcon] = None,
                 link: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 params: Optional[dict] = None,
                 disabled: bool = False,
                 ):
        if not link and not endpoint:
            raise ValueError("link or endpoint should be set ")
        super(NavigationLink, self).__init__(title, navigation_type='link', icon=icon, link=link, endpoint=endpoint,
                                             params=params, disabled=disabled)

    def get_link(self):
        if self.params:
            return self.link or _app.url_for(self.endpoint, **self.params)
        return self.link or _app.url_for(self.endpoint)

    def get_html_title(self):
        _title = html_escape(self.title)
        if self.icon:
            _title = self.icon.render() + ' ' + _title
        return _title


class NavigationGroup(NavigationItem):
    def __init__(self, title, icon=None, items_list: List[NavigationItem] = None):
        super(NavigationGroup, self).__init__(title, navigation_type='group', icon=icon)
        self.items_list = items_list or list()


class NavigationSeparator(NavigationItem):
    def __init__(self):
        super(NavigationSeparator, self).__init__(None, navigation_type='separator')
