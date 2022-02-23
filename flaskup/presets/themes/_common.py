from os.path import join

from flask.globals import session, request, g
from flask.helpers import get_flashed_messages, url_for
from jinja2 import Environment, FileSystemLoader

from flaskup._consts import TEMPLATE_FOLDER
from flaskup.utils import Jinja2Env

THEMES_FOLDER = join(TEMPLATE_FOLDER, 'themes')


def make_jinja2_theme_env(theme_name, loader=None, autoescape=True, auto_reload=True, **options):
    loader = loader or FileSystemLoader(join(THEMES_FOLDER, theme_name))
    env = Environment(loader=loader, autoescape=autoescape, auto_reload=auto_reload, **options)

    env.globals.update(
        url_for=url_for,
        get_flashed_messages=get_flashed_messages,
        request=request,
        session=session,
        g=g,
    )
    return Jinja2Env(env)
