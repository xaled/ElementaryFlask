from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from html import escape as html_escape

from component import AbstractComponent
from flaskup.globals import current_flaskup_app as _app
from flaskup.typing import RenderReturnValue, Optional, List, NavigationData, NavigationItem
from .icon import AbstractIcon


class AbstractNavigationHandler(ABC):
    @abstractmethod
    def handle_nav(self) -> NavigationData:
        raise NotImplementedError()


class AbstractNavigation(AbstractComponent):
    def __init__(self, navigation_handler: AbstractNavigationHandler):
        super().__init__()
        self.navigation_handler = navigation_handler

    def render(self, **options) -> RenderReturnValue:
        nav_data = self.navigation_handler.handle_nav()
        return self.render_nav(nav_data, **options)

    def render_nav(self, nav_data: NavigationData, **options) -> RenderReturnValue:
        raise NotImplementedError()


class DefaultNavigationHandler(AbstractNavigationHandler):
    def handle_nav(self) -> NavigationData:
        return _app.config.navigation_data


class BootstrapTopNavigation(AbstractNavigation):  # TODO Bootstrap
    def __init__(self, navigation_handler, expand_at="md", appearance="navbar-dark bg-primary"):
        super(BootstrapTopNavigation, self).__init__(navigation_handler)
        self.expand_at = expand_at
        self.appearance = appearance

    def render_nav(self, nav_data: NavigationData, **options) -> RenderReturnValue:
        _expand_at = "navbar-expand-" + self.expand_at
        ret = f'<nav class="navbar {_expand_at} {html_escape(self.appearance)}"><div class="container-fluid">'

        # brand TODO
        ret += f'<a class="navbar-brand" href="/">{_app.name}</a>'

        # collapse button
        ret += """<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#fu_navbarCollapse" aria-controls="fu_navbarCollapse" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>"""

        # Items
        _me_auto = 'me-auto'  # TODO boostrap4
        group_ix = 0
        ret += f"""<div class="collapse navbar-collapse" id="fu_navbarCollapse"><ul class="navbar-nav {_me_auto}">"""
        for itm in nav_data:
            if isinstance(itm, NavigationLink):
                ret += self.render_item(itm)
            elif isinstance(itm, NavigationGroup):
                group_ix += 1
                ret += self.render_group(itm, group_ix)

        # Closing tabs
        ret += '</div></ul></div></nav>'

    def render_item(self, itm: "NavigationLink"):
        _active = ''  # TODO
        _link = html_escape(itm.get_link())
        _title = html_escape(itm.title)
        if itm.icon:
            _title = itm.icon.render() + ' ' + _title
        return f"""<li class="nav-item"><a class="nav-link {_active}"  href="{_link}">{_title}</a></li>"""

    def render_group(self, grp: "NavigationGroup", group_ix):
        _grp_id = "fu_navigationGroup" + str(group_ix)
        _title = html_escape(grp.title)
        if grp.icon:
            _title = grp.icon.render() + ' ' + _title
        ret = f"""<li class="nav-item dropdown"><a class="nav-link dropdown-toggle show" href="#" id="{_grp_id}" data-bs-toggle="dropdown" aria-expanded="true">{_title}</a><ul class="dropdown-menu" aria-labelledby="{_grp_id}">"""

        for itm in grp.items_list:
            if isinstance(itm, NavigationLink):
                _link = html_escape(itm.get_link())
                _title = html_escape(itm.title)
                if itm.icon:
                    _title = itm.icon.render() + ' ' + _title
                ret += f"""<li><a class="dropdown-item" href="{_link}">{_title}</a></li>"""
            elif isinstance(itm, NavigationGroup):
                _title = html_escape(itm.title)
                if itm.icon:
                    _title = itm.icon.render() + ' ' + _title
                ret += f"""<li><a class="dropdown-item" href="#">{_title}</a></li>"""
            elif isinstance(itm, NavigationSeparator):
                ret += '<li><hr class="dropdown-divider"></li>'

        ret += """</ul></li>"""
        return ret


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