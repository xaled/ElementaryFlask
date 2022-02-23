from types import SimpleNamespace

from flaskup.components import EmptyPageLayout
from ._jinja2_env import jinja2_env


class AdminLTEDefaultLayout(EmptyPageLayout):
    def __init__(self, additional_includes=None):
        super(AdminLTEDefaultLayout, self).__init__(additional_includes=additional_includes)

    def render_body_tag(self, ns: SimpleNamespace) -> str:
        return jinja2_env.render_template('layouts/default_body.html',
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
