from types import SimpleNamespace

import flask as _f
import yaml
from redis import Redis

import elementary_flask.typing as t
from ._consts import STATIC_FOLDER, TEMPLATE_FOLDER
from .components import FavIcon, Theme, LayoutMapping, \
    EmptyPageLayout
from .components.weak.form import default_form_render
from .components.weak.navigation import AbstractNavigationProvider, StaticNavigationProvider, Navigation
from .cron import cron_endpoint, CronEntry
from .includes import DEFAULT_BOOTSTRAP_VERSION, DEFAULT_ALPINEJS_DEPENDENCY, ComponentIncludes
from .presets.themes import DefaultTheme
from .blueprint import ElementaryScaffold


class ElementaryFlask(ElementaryScaffold):
    def __init__(self, name, secret, static_folder='static', template_folder='templates',
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None,
                 theme: t.Optional[t.Union[Theme, str]] = None, include_bootstrap=True,
                 navigation_map: dict = None,
                 navigation_provider: AbstractNavigationProvider = None,
                 include_alpinejs=True,
                 alpinejs_dependency=None,
                 logo_src=None,
                 renderers=None,
                 crontab: t.Iterable[CronEntry] = None,
                 **options):
        # from .auth import LogoutSessionInterface

        # # TEMPLATE_DIR = "template/bt4"
        # MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
        # TEMPLATE_DIR = os.path.join(MODULE_DIR, 'template')
        # STATIC_DIR = os.path.join(MODULE_DIR, 'static')
        # app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
        ElementaryScaffold.__init__(self)
        self._init = False
        self.name = name
        self.flask_app = _f.Flask(name, static_folder=static_folder,
                                  template_folder=template_folder)
        self.flask_config = self.flask_app.config
        # self.flask_config['SECRET_KEY'] = secret
        self.flask_app.elementary_flask = self
        # app.session_interface = LogoutSessionInterface(app.session_interface)
        # self._csrf = _CSRFProtect(self.flask_app)
        self.core_bp = _f.Blueprint('core', __name__, url_prefix='/core',
                                    static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
        # self.api_bp = _f.Blueprint('api', __name__, url_prefix='/api')
        # self.form_bp = _f.Blueprint('form', __name__, url_prefix='/form')

        # @self.flask_app.route('/')
        # def index():
        #     return _f.redirect('/app')
        # self._route_mapping = dict()
        # self._page_view_functions = dict()

        # App Config
        self.config = SimpleNamespace()
        self.flask_app.update_template_context(dict(elementary_flask_config=self.config))

        # Default includes
        self.config.default_includes = default_includes or ComponentIncludes()

        # Logo & Favicons
        self.config.logo_src = logo_src or "/core/static/img/logo.png"
        self.config.icons = icons or [FavIcon(href=self.config.logo_src, mimetype="image/png")]

        # Metas
        if default_meta_tags:
            self.config.default_meta_tags = default_meta_tags
        else:
            self.config.default_meta_tags = dict()

        if 'viewport' not in self.config.default_meta_tags:
            self.config.default_meta_tags['viewport'] = 'width=device-width, initial-scale=1'

        self.config.default_title = default_title if default_title is not None else name

        # AlpineJS
        if include_alpinejs or alpinejs_dependency:
            alpinejs_dependency = alpinejs_dependency or DEFAULT_ALPINEJS_DEPENDENCY
            self.config.default_includes.dependencies.insert(0, alpinejs_dependency)

        # Theme
        if theme and isinstance(theme, Theme):
            self.theme = theme
        elif theme == 'adminlte':
            from elementary_flask.presets.themes import AdminLTETheme
            self.theme = AdminLTETheme()
        else:
            # bootstrap_theme = options.get('bootstrap_theme', None)
            bootstrap_version = options.get('bootstrap_version', DEFAULT_BOOTSTRAP_VERSION)
            bootstrap_dependency = options.get('bootstrap_dependency', None)
            theme_default_includes = options.get('theme_default_includes', None)
            theme_layouts_mapping = options.get('theme_layouts_mapping', None)
            self.theme = DefaultTheme(bootstrap_version=bootstrap_version, bootstrap_theme=theme,
                                      layouts_mapping=theme_layouts_mapping,
                                      include_bootstrap=include_bootstrap,
                                      bootstrap_dependency=bootstrap_dependency,
                                      default_includes=theme_default_includes)

        self.config.default_includes += self.theme.default_includes

        # ElementaryFlask js & css
        self.config.default_includes += ComponentIncludes(
            js_includes={'/core/static/elementary_flask.js'},
            css_includes={'/core/static/elementary_flask.css'},
        )

        # Default Layout Mapping
        self.layout_mapping = LayoutMapping(
            default=EmptyPageLayout()
        )

        # Core jinja2 environment
        # self.core_jinja_env = Environment(autoescape=True, loader=FileSystemLoader(TEMPLATE_FOLDER))
        from elementary_flask.utils.jinja2 import Jinja2Env
        self.core_jinja_env = Jinja2Env(TEMPLATE_FOLDER)

        # Navigation
        self.config.navigation_map = navigation_map or []
        self.elementary_ns.navigation_map = self.config.navigation_map
        self.config.navigation_provider = navigation_provider or StaticNavigationProvider(self.config.navigation_map)
        self.config.navigation = Navigation()

        # Logger
        self.logger = self.flask_app.logger

        # Renderers
        self.renderers = dict(DEFAULT_RENDERERS)
        if renderers:
            self.renderers.update(renderers)

        # Default Template filters
        # self.flask_app.add_template_filter()

        # Crontab & cron endpoint rule
        self.crontab = self.elementary_ns.crontab  # Default crons
        if crontab:
            self.crontab.extend(crontab)

        self.core_bp.add_url_rule('/cron', 'cron', cron_endpoint)

        self.redis = None

    def _init_app(self, debug=False):
        if self._init:
            return
        # Registering Blueprints
        self.flask_config.from_file('../config.yml', load=yaml.safe_load)
        self.flask_app.register_blueprint(self.core_bp)
        # self.flask_app.register_blueprint(self.api_bp)
        # self.flask_app.register_blueprint(self.form_bp)
        # TODO register error handlers

        # Redis server
        redis_config = self.flask_config.get('REDIS', False)
        if redis_config is not False:
            redis_config = redis_config if redis_config is not None else dict()
            if 'url' in redis_config:
                self.redis = Redis.from_url(redis_config['url'])
            else:
                self.redis = Redis(
                    host=redis_config.get('host', None) or ("localhost" if debug else 'redis'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('core_db', 1),
                )

        # logging level
        if debug:
            import logging
            self.logger.setLevel(logging.DEBUG)
            self.flask_config['ELEMENTARY_FLASK_RENDER_ERROR_STRATEGY'] = 'raise'

        self._init = True

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **kwargs):
        self._init_app(debug=debug)

        # Run flask app
        self.flask_app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **kwargs)

    def get_layout(self, layout_name):
        # ignore = ignore or list()
        # if self.theme.layouts_mapping not in ignore:
        #     res = self.theme.layouts_mapping.get_layout(layout_name)
        #     if res:
        #         return res
        # if self.layout_mapping not in ignore:
        #     return self.layout_mapping.get_layout(layout_name)
        # return self.layout_mapping.layouts['default']

        # if self.theme:
        return self.theme.layouts_mapping.get_layout(layout_name)
        # return self.layouts_mapping.get_layout(layout_name)

    def render_core_template(self, template_name, **kwargs):
        # return self.core_jinja_env.get_template(template_name).render(*args, **kwargs)
        return self.core_jinja_env.render_template(template_name, **kwargs)

    def set_navigation_provider(self, navigation_provider: AbstractNavigationProvider):
        self.config.navigation_provider = navigation_provider

    def extend_navigation_map(self, *items, clear_old=False):
        if clear_old:
            self.config.navigation_map.clear()
        self.config.navigation_map.extend(items)

    @staticmethod
    def url_for(endpoint: str, **values: t.Any) -> str:
        return _f.url_for(endpoint, **values)

    def __call__(self, environ: dict, start_response: t.Callable) -> t.Any:
        self._init_app()
        return self.flask_app(environ=environ, start_response=start_response)

    def add_url_rule(
            self,
            rule: str,
            endpoint: t.Optional[str] = None,
            view_func: t.Optional[t.Callable] = None,
            provide_automatic_options: t.Optional[bool] = None,
            **options: t.Any,
    ) -> None:
        return self.flask_app.add_url_rule(rule, endpoint=endpoint, view_func=view_func,
                                           provide_automatic_options=provide_automatic_options, **options)

    def register_blueprint(self, blueprint, **options: t.Any) -> None:
        return self.flask_app.register_blueprint(blueprint, **options)

    def _is_setup_finished(self) -> bool:
        return self.flask_app._is_setup_finished()


DEFAULT_RENDERERS = {
    'Form': default_form_render
}
