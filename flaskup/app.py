from types import SimpleNamespace

import flask as _f
from flask_wtf.csrf import CSRFProtect as _CSRFProtect
from jinja2 import Environment, FileSystemLoader

import flaskup.typing as t
from ._consts import STATIC_FOLDER, TEMPLATE_FOLDER
from .components import ComponentIncludes, PageResponse, FavIcon, make_page_response, Theme, LayoutMapping, \
    EmptyPageLayout, AbstractNavigationHandler, StaticNavigationHandler, NavigationLink, IClassIcon, AbstractIcon
from .components.bootstrap import DEFAULT_BOOTSTRAP_VERSION
from .presets.themes import DefaultTheme


class FlaskUp:
    def __init__(self, name, secret, static_folder='static', template_folder='templates',
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None,
                 theme: t.Optional[t.Union[Theme, str]] = None, include_bootstrap=True,
                 navigation_map: dict = None,
                 navigation_handler: AbstractNavigationHandler = None,
                 **options):
        # from .auth import LogoutSessionInterface

        # # TEMPLATE_DIR = "template/bt4"
        # MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
        # TEMPLATE_DIR = os.path.join(MODULE_DIR, 'template')
        # STATIC_DIR = os.path.join(MODULE_DIR, 'static')
        # app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
        self.name = name
        self.flask_app = _f.Flask(name, static_folder=static_folder,
                                  template_folder=template_folder)
        self.flask_app.config['SECRET_KEY'] = secret
        self.flask_app.flaskup = self
        # app.session_interface = LogoutSessionInterface(app.session_interface)
        self._csrf = _CSRFProtect(self.flask_app)
        self.core_bp = _f.Blueprint('core', __name__, url_prefix='/core',
                                    static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
        self.api_bp = _f.Blueprint('api', __name__, url_prefix='/api')
        # self._app_bp = _f.Blueprint('app', __name__, url_prefix='/app',
        #                             static_folder=static_folder,
        #                             template_folder=template_folder)

        # @self.flask_app.route('/')
        # def index():
        #     return _f.redirect('/app')
        self._route_mapping = dict()
        self._page_view_functions = dict()

        # App Config
        # self.flask_app.config = current_app.config['FLASKUP_']
        # self.config =
        self.config = SimpleNamespace()
        if icons:
            self.config.icons = icons

        self.config.default_includes = default_includes or ComponentIncludes()

        if default_meta_tags:
            self.config.default_meta_tags = default_meta_tags
        else:
            self.config.default_meta_tags = dict()

        if 'viewport' not in self.config.default_meta_tags:
            self.config.default_meta_tags['viewport'] = 'width=device-width, initial-scale=1'

        self.config.default_title = default_title if default_title is not None else name

        # Theme
        if theme and isinstance(theme, Theme):
            self.theme = theme
        elif theme == 'adminlte':
            from flaskup.presets.themes import AdminLTETheme
            self.theme = AdminLTETheme()
        else:
            # bootstrap_theme = options.get('bootstrap_theme', None)
            bootstrap_version = options.get('bootstrap_version', DEFAULT_BOOTSTRAP_VERSION)
            bootstrap_dependency = options.get('bootstrap_dependency', None)
            theme_default_includes = options.get('theme_default_includes', None)
            theme_layouts_mapping = options.get('theme_layouts_mapping', None)
            self.theme = DefaultTheme(bootstrap_version=bootstrap_version, bootstrap_theme=theme,
                                      layouts_mapping=theme_layouts_mapping, include_bootstrap=include_bootstrap,
                                      bootstrap_dependency=bootstrap_dependency,
                                      default_includes=theme_default_includes)

        self.config.default_includes += self.theme.default_includes

        # Default Layout Mapping
        self.layout_mapping = LayoutMapping(
            default=EmptyPageLayout()
        )

        # Core jinja2 environment
        self.core_jinja_env = Environment(autoescape=True, loader=FileSystemLoader(TEMPLATE_FOLDER))

        # Navigation
        self.navigation_map = navigation_map or []
        self.navigation_handler = navigation_handler or StaticNavigationHandler(self.navigation_map)

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **kwargs):
        # Registering Blueprints
        self.flask_app.register_blueprint(self.core_bp)
        # self.flask_app.register_blueprint(self._app_bp)
        self.flask_app.register_blueprint(self.api_bp)

        # TODO register error handlers

        # Run flask app
        self.flask_app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **kwargs)

    # def route(self, rule: str, **options: t.Any) -> t.Callable:
    #     def decorator(f: t.Callable) -> t.Callable:
    #         endpoint = options.pop("endpoint", None)
    #         # if endpoint is None:
    #         #     endpoint = f.__name__
    #         #
    #         # print(endpoint)
    #         #
    #         # if endpoint in self._route_mapping:
    #         #     ff = self._route_mapping[endpoint]
    #         # else:
    #         #     ff = FlaskUpApp._wrap_route(f)
    #         #     self._route_mapping[endpoint] = ff
    #         # print(ff)
    #         # self._app_bp.add_url_rule(rule, endpoint, FlaskUpApp._wrap_route(f), **options)
    #         self.flask_app.add_url_rule(rule, endpoint, f, **options)
    #         return f
    #
    #     return decorator

    # def route_page(self, rule: str, endpoint: t.OptionalStr = None, **options):
    #     def _view_function(cls):
    #         def _wrap(*args, **kwargs):
    #             p = cls(*args, **kwargs)
    #             return p.render()
    #
    #         return _wrap
    #
    #     def decorator(cls):
    #         _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'
    #         # print(_ep)
    #         old_cls, old_wrapper = self._page_view_functions.get(_ep, (None, None))
    #         if old_cls is not None and old_cls != cls:
    #             raise AssertionError(
    #                 "View function mapping is overwriting an existing"
    #                 f" endpoint function: {_ep}"
    #             )
    #         elif old_cls is None:
    #             self._page_view_functions[_ep] = cls, _view_function(cls)
    #
    #         wrapper = self._page_view_functions[_ep][1]
    #
    #         # print(endpoint)
    #         #
    #         # if endpoint in self._route_mapping:
    #         #     ff = self._route_mapping[endpoint]
    #         # else:
    #         #     ff = FlaskUpApp._wrap_route(f)
    #         #     self._route_mapping[endpoint] = ff
    #         # print(ff)
    #         # self._app_bp.add_url_rule(rule, endpoint, FlaskUpApp._wrap_route(f), **options)
    #         self.flask_app.add_url_rule(rule, _ep, wrapper, **options)
    #         return cls
    #
    #     return decorator
    #
    def route_page(self, rule: str, endpoint: t.OptionalStr = None,
                   page_layout='default',
                   navigation=False,
                   navigation_title=None,
                   navigation_params=None,
                   navigation_icon: t.Union[str, AbstractIcon] = None,
                   **options):
        def _view_function(f: t.Callable[..., t.PageRouteReturnValue]):
            def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
                # p = cls(*args, **kwargs)
                # return p.render()
                page_response = f(*args, **kwargs)
                if not isinstance(page_response, PageResponse):
                    page_response = make_page_response(page_response)
                pl = page_response.page_layout if page_response.page_layout is not None else page_layout
                return self.get_layout(pl).render_response(page_response)

            return _wrap

        def decorator(f):
            # _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'
            _ep = endpoint if endpoint is not None else f.__name__
            if navigation:
                _nt = navigation_title
                if not _nt:
                    _nt = _ep.replace('_', ' ').strip()
                    _nt = _nt[0].upper() + _nt[1:]
                _ni = navigation_icon
                if _ni and isinstance(_ni, str):
                    _ni = IClassIcon(_ni)
                self.navigation_map.append(NavigationLink(title=_nt, endpoint=_ep, params=navigation_params,
                                                          icon=_ni))
            # print(_ep)
            old_f, old_wrapper = self._page_view_functions.get(_ep, (None, None))
            if old_f is not None and old_f != f:
                raise AssertionError(
                    "View function mapping is overwriting an existing"
                    f" endpoint function: {_ep}"
                )
            elif old_f is None:
                self._page_view_functions[_ep] = f, _view_function(f)

            wrapper = self._page_view_functions[_ep][1]

            # print(endpoint)
            #
            # if endpoint in self._route_mapping:
            #     ff = self._route_mapping[endpoint]
            # else:
            #     ff = FlaskUpApp._wrap_route(f)
            #     self._route_mapping[endpoint] = ff
            # print(ff)
            # self._app_bp.add_url_rule(rule, endpoint, FlaskUpApp._wrap_route(f), **options)
            self.flask_app.add_url_rule(rule, _ep, wrapper, **options)
            return f

        # def decorator(cls):
        #     _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'
        #     # print(_ep)
        #     old_cls, old_wrapper = self._page_view_functions.get(_ep, (None, None))
        #     if old_cls is not None and old_cls != cls:
        #         raise AssertionError(
        #             "View function mapping is overwriting an existing"
        #             f" endpoint function: {_ep}"
        #         )
        #     elif old_cls is None:
        #         self._page_view_functions[_ep] = cls, _view_function(cls)
        #
        #     wrapper = self._page_view_functions[_ep][1]
        #
        #     # print(endpoint)
        #     #
        #     # if endpoint in self._route_mapping:
        #     #     ff = self._route_mapping[endpoint]
        #     # else:
        #     #     ff = FlaskUpApp._wrap_route(f)
        #     #     self._route_mapping[endpoint] = ff
        #     # print(ff)
        #     # self._app_bp.add_url_rule(rule, endpoint, FlaskUpApp._wrap_route(f), **options)
        #     self.flask_app.add_url_rule(rule, _ep, wrapper, **options)
        #     return cls

        return decorator

    def get_layout(self, layout_name, ignore=None):
        ignore = ignore or list()
        if self.theme.layouts_mapping not in ignore:
            return self.theme.layouts_mapping.get_layout(layout_name)
        if self.layout_mapping not in ignore:
            return self.layout_mapping.get_layout(layout_name)
        return self.layout_mapping.layouts['default']

    # @staticmethod
    # def _wrap_route(f: t.Callable[..., t.RouteReturnValue]):
    #     def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
    #         ret = f(*args, **kwargs)
    #         if isinstance(ret, t.Renderable):
    #             return ret.render()
    #         return ret
    #
    #     return _wrap

    def render_core_template(self, template_name, *args, **kwargs):
        return self.core_jinja_env.get_template(template_name).render(*args, **kwargs)

    def set_navigation_handler(self, navigation_handler: AbstractNavigationHandler):
        self.navigation_handler = navigation_handler

    def extend_navigation_map(self, *items, clear_old=False):
        if clear_old:
            self.navigation_map.clear()
        self.navigation_map.extend(items)

    def url_for(self, endpoint: str, **values: t.Any) -> str:
        return _f.url_for(endpoint, **values)
