from dataclasses import dataclass, field
from html import escape as html_escape
from types import SimpleNamespace

from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import List, Optional, RenderReturnValue, Block, ResponseReturnValue
from .component import ComponentIncludes, reduce_includes, Renderable
from .page_response import PageResponse


class BlockNotRenderable(Exception):
    pass


@dataclass()
class AbstractPageLayout:
    block_names: List[str] = field(default_factory=lambda: ['main'])
    additional_includes: Optional[ComponentIncludes] = None
    _reduced_includes: Optional[ComponentIncludes] = field(init=False, default=None)

    # def __post_init__(self):
    #     from flaskly import current_flaskly_app
    #     # self.app =
    #     self.app = current_flaskly_app
    #     _app.config = self.app.config

    def render_response(self, response: PageResponse) -> ResponseReturnValue:
        # if content is None or isinstance(content, Renderable) or isinstance(content, str):
        #     if self.additional_includes and isinstance(content, AbstractComponent):
        #         component_includes = self.additional_includes + content.component_includes
        #     elif isinstance(content, AbstractComponent):
        #         component_includes = content.component_includes
        #     else:
        #         component_includes = None
        #
        #     return '<!DOCTYPE html>' + self.render_html_tag_open() \
        #            + self.render_head_tag(content, component_includes) \
        #            + self.render_body_tag(content, component_includes) + '</html>'
        # return content
        # Namespace
        ns = response.ns
        ns.response = response

        # Includes
        # if self.additional_includes:
        #     ns.component_includes = self.additional_includes + content.component_includes
        # else:
        #     ns.component_includes = content.component_includes
        if self._reduced_includes is None:
            self._reduced_includes = reduce_includes(_app.config.default_includes, self.additional_includes)
        ns.component_includes = reduce_includes(self._reduced_includes, response.component_includes)

        rendered_blocks = dict()
        for block_name in self.block_names:
            # try:
            rendered_blocks[block_name] = self.render_block(response.blocks[block_name], ns)
            # except BlockNotRenderable:
            #     return content.blocks[block_name]

        ns.rendered_blocks = rendered_blocks

        # Render Layout
        rendered_page = self.render_layout(ns)
        status_code = response.status_code
        headers = response.headers
        if status_code is None and headers is None:
            return rendered_page
        elif status_code is not None and headers is not None:
            return rendered_page, status_code, headers
        elif status_code is not None:
            return rendered_page, status_code
        return rendered_page, headers

    def render_layout(self, ns: SimpleNamespace) -> RenderReturnValue:
        raise NotImplementedError()

    def render_block(self, block: Block, ns: SimpleNamespace) -> ResponseReturnValue:
        if isinstance(block, Renderable) or callable(getattr(block, "render", None)):
            return block.render(**ns.__dict__)
        if isinstance(block, str):
            return block
        if block is None:
            return ''
        raise BlockNotRenderable()


class EmptyPageLayout(AbstractPageLayout):
    def __init__(self, additional_includes=None, block_names=None):
        block_names = block_names or ['main']
        if 'main' not in block_names:
            block_names.append('main')
        super(EmptyPageLayout, self).__init__(block_names=block_names,
                                              additional_includes=additional_includes)

    def render_layout(self, ns: SimpleNamespace) -> RenderReturnValue:
        return '<!DOCTYPE html><html>' \
               + self.render_head_tag(ns.response, ns.component_includes) \
               + self.render_body_tag(ns) + '</html>'

    def render_head_tag(self, response: PageResponse, component_includes: ComponentIncludes) -> str:
        head = "<head>"

        # Charset
        head += '<meta charset="UTF-8">'

        # Fav icons
        if hasattr(_app.config, 'icons'):
            for icon in _app.config.icons:
                head += icon.rendered

        # Title
        title = response.title if response.title is not None or not hasattr(_app.config, 'default_title') \
            else _app.config.default_title
        if title is not None:
            head += f'<title>{html_escape(title)}</title>'

        # Meta tags
        for meta in ('description', 'keywords', 'author', 'viewport'):
            if response.meta_tags[meta] is not None or not hasattr(_app.config, 'default_meta_tags') \
                    or meta not in _app.config.default_meta_tags:
                meta_value = response.meta_tags[meta]
            else:
                meta_value = _app.config.default_meta_tags[meta]
            if meta_value:
                head += f'<meta name="{meta}" content="{html_escape(meta_value)}">'

        # Head includes
        if component_includes:
            head += component_includes.render_head_includes()

        head += "</head>"
        return head

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


class LayoutMapping:
    def __init__(self, parent: Optional["LayoutMapping"] = None, **layouts):
        self.parent = parent
        self.layouts = layouts

    def get_layout(self, layout):
        return self._get_layout(layout, [])

    def _get_layout(self, layout, ignore):
        if layout in self.layouts:
            return self.layouts[layout]
        if self.parent and self.parent not in ignore:
            ignore.append(layout)
            return self.parent._get_layout(layout, ignore)
        return _app.get_layout(layout, ignore)
