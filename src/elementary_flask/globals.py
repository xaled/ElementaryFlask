from flask.globals import LocalProxy, current_app


def _find_app():
    return current_app.elementary_flask  # noqa


current_elementary_flask_app: "ElementaryFlask" = LocalProxy(_find_app)  # type: ignore
