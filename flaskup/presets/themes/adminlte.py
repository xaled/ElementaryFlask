from types import SimpleNamespace

from flaskup.components import Theme, LayoutMapping, EmptyPageLayout, ComponentIncludes, Dependency, \
    CSSDependencyLink, JavascriptDependencyLink
from flaskup.components.bootstrap import adminlte_dependency
from flaskup.globals import current_flaskup_app as _app


class AdminLTETheme(Theme):
    def __init__(self):
        default_includes = ComponentIncludes([
            Dependency('source_sans_pro_font',
                       links=[CSSDependencyLink(
                           "https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback")]
                       ),
            Dependency('fontawesome-free', version='5.15.3',
                       links=[CSSDependencyLink(
                           "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.3/css/all.min.css")]
                       ),
            Dependency('adminlte', version='3.2.0',
                       links=[JavascriptDependencyLink(
                           "https://cdn.jsdelivr.net/npm/admin-lte@3.2.0/dist/js/adminlte.min.js")]
                       )
        ])
        super(AdminLTETheme, self).__init__(bootstrap_dependency=adminlte_dependency,
                                            default_includes=default_includes,
                                            layouts_mapping=LayoutMapping(
                                                default=AdminLTEDefaultLayout()
                                            ))


class AdminLTEDefaultLayout(EmptyPageLayout):
    def __init__(self, additional_includes=None):
        super(AdminLTEDefaultLayout, self).__init__(additional_includes=additional_includes)

    def render_body_tag(self, ns: SimpleNamespace) -> str:
        return _app.render_core_template('themes/adminlte/default_body.html',
                                         # body_includes=ns.component_includes.render_body_includes(),
                                         **ns.__dict__, )
        # rendered_blocks = ns.rendered_blocks
        # component_includes = ns.component_includes
        #
        # body = '<body>'
        #
        # # Page content
        # body += rendered_blocks['main']
        #
        # # Body includes
        # body += component_includes.render_body_includes()
        # body += '</body>'
        # return body
