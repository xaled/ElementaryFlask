import re
from types import SimpleNamespace

import flask as _f
from flask_wtf.csrf import CSRFProtect as _CSRFProtect

import flaskly.typing as t
from ._consts import STATIC_FOLDER, TEMPLATE_FOLDER
from .components import PageResponse, PageErrorResponse, FavIcon, make_page_response, Theme, LayoutMapping, \
    EmptyPageLayout, IClassIcon, AbstractIcon, \
    RenderResponse
from .components.form import wrap_form_cls, form_endpoint_func, default_form_render, FormResponse
from .components.navigation import AbstractNavigationProvider, StaticNavigationProvider, Navigation, NavigationLink
from .includes import DEFAULT_BOOTSTRAP_VERSION, DEFAULT_ALPINEJS_DEPENDENCY, ComponentIncludes
from .presets.themes import DefaultTheme

_form_name_validator = re.compile(r'^[a-z0-9_]+$', re.IGNORECASE)


class FlasklyApp:
    def __init__(self, name, secret, static_folder='static', template_folder='templates',
                 default_includes=None, default_meta_tags=None, default_title=None, icons: t.List[FavIcon] = None,
                 theme: t.Optional[t.Union[Theme, str]] = None, include_bootstrap=True,
                 navigation_map: dict = None,
                 navigation_provider: AbstractNavigationProvider = None,
                 include_alpinejs=True,
                 alpinejs_dependency=None,
                 logo_src=None,
                 renderers=None,
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
        self.flask_app.flaskly = self
        # app.session_interface = LogoutSessionInterface(app.session_interface)
        self._csrf = _CSRFProtect(self.flask_app)
        self.core_bp = _f.Blueprint('core', __name__, url_prefix='/core',
                                    static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
        self.api_bp = _f.Blueprint('api', __name__, url_prefix='/api')
        self.form_bp = _f.Blueprint('form', __name__, url_prefix='/form')

        # @self.flask_app.route('/')
        # def index():
        #     return _f.redirect('/app')
        self._route_mapping = dict()
        self._page_view_functions = dict()

        # App Config
        self.config = SimpleNamespace()
        self.flask_app.update_template_context(dict(flaskly_config=self.config))

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
            from flaskly.presets.themes import AdminLTETheme
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

        # Flaskly js & css
        self.config.default_includes += ComponentIncludes(
            js_includes={'/core/static/flaskly.js'},
            css_includes={'/core/static/flaskly.css'},
        )

        # Default Layout Mapping
        self.layout_mapping = LayoutMapping(
            default=EmptyPageLayout()
        )

        # Core jinja2 environment
        # self.core_jinja_env = Environment(autoescape=True, loader=FileSystemLoader(TEMPLATE_FOLDER))
        from flaskly.utils.jinja2 import Jinja2Env
        self.core_jinja_env = Jinja2Env(TEMPLATE_FOLDER)

        # Navigation
        self.config.navigation_map = navigation_map or []
        self.config.navigation_provider = navigation_provider or StaticNavigationProvider(self.config.navigation_map)
        self.config.navigation = Navigation()

        # Logger
        self.logger = self.flask_app.logger

        # Renderers
        self.renderers = dict(DEFAULT_RENDERERS)
        if renderers:
            self.renderers.update(renderers)

    def run(self, host=None, port=None, debug=None, load_dotenv=True, **kwargs):
        # Registering Blueprints
        self.flask_app.register_blueprint(self.core_bp)
        self.flask_app.register_blueprint(self.api_bp)
        self.flask_app.register_blueprint(self.form_bp)

        # TODO register error handlers

        # Run flask app
        self.flask_app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **kwargs)

    def route_page(self, rule: str, endpoint: t.OptionalStr = None,
                   page_layout='default',
                   navigation=False,
                   navigation_title=None,
                   navigation_params=None,
                   navigation_icon: t.Union[str, AbstractIcon] = None,
                   **options):
        """Decorate a page view function to register it with the given URL
        rule and options.

        .. code-block:: python

            @app.route_page("/")
            def index():
                return "Hello, World!"

        :param rule: The URL rule string.
        :param endpoint: Name for the route. Default value: the name of function.
        :param page_layout: Name of :class:`PageLayout` that renders the response. Default value: ``'default'``.
        :param navigation: Add the page to navigation. Default value: ``None``.
        :param navigation_title: The page title used in navigation.
        :param navigation_icon: The page icon used in navigation.
        :param options: Extra options passed to the Flask object.
        """
        return self._route_page(rule, endpoint=endpoint,
                                page_layout=page_layout,
                                navigation=navigation,
                                navigation_title=navigation_title,
                                navigation_params=navigation_params,
                                navigation_icon=navigation_icon,
                                methods=None,
                                **options)

    def _route_page(self, rule: str, endpoint: t.OptionalStr = None,
                    page_layout='default',
                    navigation=False,
                    navigation_title=None,
                    navigation_params=None,
                    navigation_icon: t.Union[str, AbstractIcon] = None,
                    methods=None,
                    **options):
        def _view_function(f: t.Callable[..., t.PageRouteReturnValue]):
            def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
                # p = cls(*args, **kwargs)
                # return p.render()
                page_response = f(*args, **kwargs)
                if isinstance(page_response, _f.Response):
                    return page_response
                if isinstance(page_response, FormResponse):
                    return page_response.to_dict()
                if not isinstance(page_response, PageResponse):
                    page_response = make_page_response(page_response)
                pl = page_response.page_layout if page_response.page_layout is not None else page_layout
                # try:
                if isinstance(page_response, PageErrorResponse):
                    render_response = self.get_layout('error').render(page_response=page_response)
                else:
                    render_response = self.get_layout(pl).render(page_response=page_response)

                # except RenderException as e: # TODO: let the exception raise or keep the page structure and show error
                #     render_response = self.get_layout('error').render(render_error=e.render_error)

                # if isinstance(render_response, RenderError): already handled
                #     return render_response.error_message, render_response.status_code  # Todo error template
                if isinstance(render_response, RenderResponse):
                    if render_response.status_code is not None:
                        return render_response.content, render_response.status_code, render_response.headers
                    else:
                        return render_response.content, render_response.headers
                else:
                    return render_response

            return _wrap

        def decorator(f):
            # _ep = endpoint if endpoint is not None else cls.__name__ + '.__init__'rende
            _ep = endpoint if endpoint is not None else f.__name__
            if navigation:
                _nt = navigation_title
                if not _nt:
                    _nt = _ep.replace('_', ' ').strip()
                    _nt = _nt[0].upper() + _nt[1:]
                _ni = navigation_icon
                if _ni and isinstance(_ni, str):
                    _ni = IClassIcon(_ni)
                self.config.navigation_map.append(NavigationLink(title=_nt, endpoint=_ep, params=navigation_params,
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

            self.flask_app.add_url_rule(rule, _ep, wrapper, methods=methods, **options)
            return f

        return decorator

    def listing(self, rule: str, endpoint: t.OptionalStr = None, **options):

        def decorator(cls):
            # TODO: sanitize rule
            for rule_suffix in ('',):  # '/<int:page>', '/<str:filter>', '/<str:filter>/<int:page>'):
                self._route_page(rule + rule_suffix, endpoint or cls.__name__,
                                 methods=['GET', 'POST'], **options)(cls.page_view)

            return cls

        return decorator

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

    def url_for(self, endpoint: str, **values: t.Any) -> str:
        return _f.url_for(endpoint, **values)

    def form(self,
             name: t.Optional[str] = None,
             rendering_type: str = 'stateful',
             **options: t.Any,
             ):
        """Creates a new :class:`Form` and uses the decorated function as
        callback.

        :param name: the name of the form. Default: class name.
        :param rendering_type: Form rendering types. Default: 'default'.
        :param options: extra options passed to flask add_url_rule.
        """

        # if rendering_type not in FORM_RENDERING_TYPES:
        #     rendering_type = 'default'

        def decorator(cls):
            n = name or cls.__name__
            rule = n
            if not _form_name_validator.match(rule):
                raise ValueError('Forbidden value for rule: ' + rule)

            # Make class renderable
            wrap_form_cls(cls, form_id='form.' + n, rendering_type=rendering_type)

            # register form endpoint
            options['methods'] = ['POST']
            self._register_endpoint_function(self.form_bp, rule, cls, n, form_endpoint_func, options)
            return cls

        return decorator

    def _register_endpoint_function(self, bp, rule, func, endpoint, func_wrapper, add_url_options):

        old_f, old_wrapper = self._page_view_functions.get(endpoint, (None, None))
        if old_f is not None and old_f != func:
            raise AssertionError(
                "Endpoint function mapping is overwriting an existing"
                f" endpoint function: {endpoint}"
            )
        elif old_f is None:
            self._page_view_functions[endpoint] = func, func_wrapper(func)

        wrapper = self._page_view_functions[endpoint][1]

        bp.add_url_rule(rule, endpoint, wrapper, **add_url_options)


DEFAULT_RENDERERS = {
    'Form': default_form_render
}
