from .includes import DependencyLink, Dependency, _create_dependency_links

BOOTSTRAP5 = (5, 1, 3)
BOOTSTRAP4 = (4, 6, 1)
DEFAULT_BOOTSTRAP_VERSION = BOOTSTRAP5
INCLUDED_BOOTSTRAP_VERSION = (BOOTSTRAP4, BOOTSTRAP5)
_bootstrap4_jquery_dependency = Dependency('jquery', version='3.5.1', links=[
    DependencyLink('https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js',
                   include_type='javascript',
                   integrity='sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj')
])
_bootstrap_js_links = {
    BOOTSTRAP4: DependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js',
        include_type='javascript',
        integrity='sha384-fQybjgWLrvvRgtW6bFlB7jaZrFsaBXjsOMm/tB9LTS58ONXgqbR9W8oWht/amnpF'
    ),
    BOOTSTRAP5: DependencyLink(
        'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        include_type='javascript',
        integrity='sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p'
    )
}
_bootstrap4_dependency = Dependency(
    'bootstrap', version=BOOTSTRAP4, dependencies=[_bootstrap4_jquery_dependency],
    links=[
        DependencyLink(
            'https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/css/bootstrap.min.css',
            include_type='css',
            integrity='sha384-zCbKRCUGaJDkqS1kPbPd7TveP5iyJE0EjAuZQTgFLD2ylzuqKfdKlfG/eSrtxUkn'),
        _bootstrap_js_links[BOOTSTRAP4]])

_bootstrap5_dependency = Dependency(
    'bootstrap', version=BOOTSTRAP5,
    links=[
        DependencyLink(
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            include_type='css',
            integrity='sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3'),
        _bootstrap_js_links[BOOTSTRAP5]])

_bootstrap_dependencies = {
    (BOOTSTRAP4, 'vanilla'): _bootstrap4_dependency,
    (BOOTSTRAP5, 'vanilla'): _bootstrap5_dependency,
}
BOOTSWATCH_THEMES = {
    BOOTSTRAP5: ['cerulean', 'cyborg', 'flatly', 'litera', 'lux', 'minty', 'pulse', 'regent', 'simplex', 'slate',
                 'spacelab', 'united', 'yeti', 'cosmo', 'darkly', 'journal', 'lumen', 'materia', 'morph', 'quartz',
                 'sandstone', 'sketchy', 'solar', 'superhero', 'vapor', 'zephyr'],
    BOOTSTRAP4: ['yeti', 'united', 'superhero', 'spacelab', 'solar', 'slate', 'sketchy', 'simplex', 'sandstone',
                 'pulse', 'minty', 'materia', 'lux', 'lumen', 'litera', 'journal', 'flatly', 'darkly', 'cyborg',
                 'cosmo', 'cerulean', ]
}


def make_bootstrap_dependency(version=None, theme=None,
                              links=None, css_includes=None, js_includes=None, dependencies=None):
    global _bootstrap_dependencies
    links = links or list()
    version = version or DEFAULT_BOOTSTRAP_VERSION
    _create_dependency_links(links, css_includes=css_includes, js_includes=js_includes)

    if version not in INCLUDED_BOOTSTRAP_VERSION and not links:
        raise ValueError('No include links provided')

    if links:
        return Dependency('bootstrap', version=version, theme=theme, links=links, dependencies=dependencies)

    _theme = theme if theme else 'vanilla'
    if (version, theme) not in _bootstrap_dependencies:
        if _theme in BOOTSWATCH_THEMES[version]:
            _version = ".".join(str(vs) for vs in version)
            links = [
                DependencyLink(f'https://cdn.jsdelivr.net/npm/bootswatch@{_version}/dist/{_theme}/bootstrap.min.css',
                               'css'),
                _bootstrap_js_links[version]
            ]
        # TODO: adminkit, adminlte
        else:
            raise Exception('Unsupported theme for bootstrap ' + '.'.join(version))

        _bootstrap_dependencies[(version, theme)] = Dependency('bootstrap', version=version, theme=theme, links=links)

    return _bootstrap_dependencies[(version, theme)]
