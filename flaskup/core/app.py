from types import SimpleNamespace

import flask as _f
from flask_wtf.csrf import CSRFProtect as _CSRFProtect

import flaskup.typing as t
from .components import ComponentIncludes, PageResponse, FavIcon, make_page_response
from .._consts import STATIC_FOLDER, TEMPLATE_FOLDER
from ..view.themes import ALLOWED_THEMES


class FlaskUp:
    def __init__(self, name, secret, static_folder='static', template_folder='templates',
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None,
                 **options):
        # from .auth import LogoutSessionInterface

        # # TEMPLATE_DIR = "template/bt4"
        # MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
        # TEMPLATE_DIR = os.path.join(MODULE_DIR, 'template')
        # STATIC_DIR = os.path.join(MODULE_DIR, 'static')
        # app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
        self.flask_app = _f.Flask(name, static_folder=static_folder,
                                  template_folder=template_folder)
        self.flask_app.config['SECRET_KEY'] = secret
        self.flask_app.flaskup = self
        # app.session_interface = LogoutSessionInterface(app.session_interface)
        self._csrf = _CSRFProtect(self.flask_app)
        self._core_bp = _f.Blueprint('core', __name__, url_prefix='/core',
                                     static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
        self._api_bp = _f.Blueprint('api', __name__, url_prefix='/api')
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

        # Bootstrap
        include_bootstrap = options.get('include_bootstrap', True)
        if include_bootstrap:
            bootstrap_theme = options.get('bootstrap_theme', 'vanilla')
            bootstrap_theme = bootstrap_theme if bootstrap_theme in ALLOWED_THEMES else 'vanilla'
            self.config.default_includes.css_includes.add(
                f'/core/static/bootstrap/themes/{bootstrap_theme}/bootstrap.min.css')
            self.config.default_includes.js_includes.add(
                '/core/static/bootstrap/bootstrap.bundle.min.js')

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **kwargs):
        # Registering Blueprints
        self.flask_app.register_blueprint(self._core_bp)
        # self.flask_app.register_blueprint(self._app_bp)
        self.flask_app.register_blueprint(self._api_bp)

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
                   **options):
        def _view_function(f: t.Callable[..., t.PageRouteReturnValue]):
            def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
                # p = cls(*args, **kwargs)
                # return p.render()
                page_response = f(*args, **kwargs)
                if not isinstance(page_response, PageResponse):
                    page_response = make_page_response(page_response)
                pl = page_response.page_layout if page_response.page_layout is not None else page_layout
                return self.get_page_layout(pl).render_response(page_response)

            return _wrap

        def decorator(f):
            # _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'
            _ep = endpoint if endpoint is not None else f.__name__
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

    def get_page_layout(self, page_layout):
        from flaskup.core.components.page_layout import DefaultPageLayout
        return DefaultPageLayout('default')

    # @staticmethod
    # def _wrap_route(f: t.Callable[..., t.RouteReturnValue]):
    #     def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
    #         ret = f(*args, **kwargs)
    #         if isinstance(ret, t.Renderable):
    #             return ret.render()
    #         return ret
    #
    #     return _wrap
