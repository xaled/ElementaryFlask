__all__ = ["ElementaryBluePrint"]

from flask import Blueprint, Flask

from elementary_flask.components import NavigationGroup, get_icon
from .scaffold import ElementaryScaffold


class ElementaryBluePrint(Blueprint, ElementaryScaffold):
    def __init__(self, name, import_name, navigation_title=None, navigation_icon=None, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, *args, **kwargs)
        ElementaryScaffold.__init__(self)
        self.navigation_title = navigation_title or name
        self.navigation_icon = get_icon(navigation_icon)

    def register(self, app, options: dict) -> None:
        from elementary_flask.app import ElementaryFlask
        flask_app, elementary_app = None, None
        if isinstance(app, Flask):
            flask_app = app
            if hasattr(app, 'elementary_flask'):
                elementary_app = app.elementary_flask
        elif isinstance(app, ElementaryFlask):
            elementary_app = app
            flask_app = elementary_app.flask_app
        else:
            raise ValueError('Unknown app type')

        if not flask_app:
            raise ValueError('Flask App is not initialized yet. None value provided')

        self.elementary_bp_register(elementary_app)
        super(ElementaryBluePrint, self).register(flask_app, options)

    def elementary_bp_register(self, elementary_app):
        elementary_app.crontab.extend(self.elementary_ns.crontab)
        elementary_app.extend_navigation_map(
            NavigationGroup(self.navigation_title,
                            icon=self.navigation_icon,
                            items_list=self.elementary_ns.navigation_map)
        )
