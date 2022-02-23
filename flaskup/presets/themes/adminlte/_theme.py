from flaskup.components import Theme, LayoutMapping, ComponentIncludes, Dependency, \
    CSSDependencyLink, JavascriptDependencyLink
from flaskup.components.bootstrap import adminlte_dependency
from .layouts import AdminLTEDefaultLayout


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
                           "https://cdn.jsdelivr.net/npm/admin-lte@3.2.0/dist/js/adminlte.min.js")
                       ]
                       )
        ])
        super(AdminLTETheme, self).__init__(bootstrap_dependency=adminlte_dependency,
                                            default_includes=default_includes,
                                            layouts_mapping=LayoutMapping(
                                                default=AdminLTEDefaultLayout()
                                            ))