from types import SimpleNamespace

from flaskup.components.page_layout import EmptyPageLayout


class TopNavigationLayout(EmptyPageLayout):
    def __init__(self, additional_includes=None, block_names=None):
        super(TopNavigationLayout, self).__init__(additional_includes=additional_includes,
                                                  block_names=block_names)

    def render_body_tag(self, ns: SimpleNamespace) -> str:
        rendered_blocks = ns.rendered_blocks
        component_includes = ns.component_includes

        body = '<body>'

        # Page content
        body += rendered_blocks['main']

        # Body includes
        body += component_includes.render_body_includes()
        body += '</body>'
        return body
