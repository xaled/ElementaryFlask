__all__ = ["ElementaryBluePrint"]

from flask import Blueprint, Flask

from .scaffold import ElementaryScaffold


class ElementaryBluePrint(Blueprint, ElementaryScaffold):
    def __init__(self, name, *args, **kwargs):
        Blueprint.__init__(self, name, *args, **kwargs)
        ElementaryScaffold.__init__(self)

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

        if flask_app:
            raise ValueError('Flask App is not initialized yet. None value provided')

        self.elementary_bp_register(elementary_app)
        super(ElementaryBluePrint, self).register(flask_app, options)

    def elementary_bp_register(self, elementary_app):
        elementary_app.crontab.extend(self.elementary_ns.crontab)
        elementary_app.extend_navigation_map(self.elementary_ns.navigation_map)
