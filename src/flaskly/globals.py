from flask.globals import LocalProxy, current_app


def _find_app():
    return current_app.flaskly


current_flaskly_app: "FlasklyApp" = LocalProxy(_find_app)  # type: ignore
