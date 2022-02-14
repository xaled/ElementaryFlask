from flask.globals import LocalProxy, current_app


def _find_app():
    return current_app.flaskup


current_flaskup_app: "FlaskUp" = LocalProxy(_find_app)  # type: ignore
