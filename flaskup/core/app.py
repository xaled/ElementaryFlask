from types import SimpleNamespace

import flask as _f
from flask_wtf.csrf import CSRFProtect as _CSRFProtect

import flaskup.typing as t
from .components.favicon import FavIcon
from .._consts import STATIC_FOLDER, TEMPLATE_FOLDER


class FlaskUpApp(t.AppContext):
    def __init__(self, name, secret, static_folder='static', template_folder='templates',
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None):
        # from .auth import LogoutSessionInterface

        # # TEMPLATE_DIR = "template/bt4"
        # MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
        # TEMPLATE_DIR = os.path.join(MODULE_DIR, 'template')
        # STATIC_DIR = os.path.join(MODULE_DIR, 'static')
        # app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
        self.flask_app = _f.Flask(name, static_folder=static_folder,
                                  template_folder=template_folder)
        self.flask_app.config['SECRET_KEY'] = secret
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

        # App context
        self.ctx = SimpleNamespace()
        if icons:
            self.ctx.icons = icons

        if default_includes:
            self.ctx.default_includes = default_includes

        if default_meta_tags:
            self.ctx.default_meta_tags = default_meta_tags

        self.ctx.default_title = default_title if default_title is not None else name

    def context(self) -> SimpleNamespace:
        return self.ctx

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

    def route_page(self, rule: str, endpoint: t.OptionalStr = None, **options):
        def _view_function(cls):
            def _wrap(*args, **kwargs):
                p = cls(*args, **kwargs)
                return p.render()

            return _wrap

        def decorator(cls):
            _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'
            # print(_ep)
            old_cls, old_wrapper = self._page_view_functions.get(_ep, (None, None))
            if old_cls is not None and old_cls != cls:
                raise AssertionError(
                    "View function mapping is overwriting an existing"
                    f" endpoint function: {_ep}"
                )
            elif old_cls is None:
                self._page_view_functions[_ep] = cls, _view_function(cls)

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
            return cls

        return decorator

    # @staticmethod
    # def _wrap_route(f: t.Callable[..., t.RouteReturnValue]):
    #     def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
    #         ret = f(*args, **kwargs)
    #         if isinstance(ret, t.Renderable):
    #             return ret.render()
    #         return ret
    #
    #     return _wrap
