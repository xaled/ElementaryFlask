from dataclasses import dataclass, field
from html import escape as html_escape
from types import SimpleNamespace

from flaskup.typing import List, Optional, Renderable, RenderReturnValue, Block, ResponseReturnValue
from .component import ComponentIncludes, reduce_includes
from .page_response import PageResponse


class BlockNotRenderable(Exception):
    pass


@dataclass()
class AbstractPageLayout:
    layout_name: str
    block_names: List[str] = field(default_factory=lambda: ['main'])
    additional_includes: Optional[ComponentIncludes] = None

    def __post_init__(self):
        from flaskup import current_flaskup_app
        # self.app =
        self.app = current_flaskup_app
        self.app_config = self.app.config

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
        ns.content = response

        # Includes
        # if self.additional_includes:
        #     ns.component_includes = self.additional_includes + content.component_includes
        # else:
        #     ns.component_includes = content.component_includes
        ns.component_includes = reduce_includes(self.app_config.default_includes, self.additional_includes,
                                                response.component_includes)

        # Render blocks
        def _render_block(block: Block) -> ResponseReturnValue:
            if isinstance(block, Renderable):
                return block.render(**ns.__dict__)
            if isinstance(block, str):
                return block
            if block is None:
                return ''
            raise BlockNotRenderable()

        rendered_blocks = dict()
        for block_name in self.block_names:
            # try:
            rendered_blocks[block_name] = _render_block(response.blocks[block_name])
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


class DefaultPageLayout(AbstractPageLayout):
    def __init__(self, layout_name, additional_includes=None):
        super(DefaultPageLayout, self).__init__(layout_name, block_names=['main'],
                                                additional_includes=additional_includes)

    def render_layout(self, ns: SimpleNamespace) -> RenderReturnValue:
        def render_head_tag(response: PageResponse, component_includes: ComponentIncludes) -> str:
            head = "<head>"

            # Charset
            head += '<meta charset="UTF-8">'

            # Fav icons
            if hasattr(self.app_config, 'icons'):
                for icon in self.app_config.icons:
                    head += icon.rendered

            # Title
            title = response.title if response.title is not None or not hasattr(self.app_config, 'default_title') \
                else self.app_config.default_title
            if title is not None:
                head += f'<title>{html_escape(title)}</title>'

            # Meta tags
            for meta in ('description', 'keywords', 'author', 'viewport'):
                if response.meta_tags[meta] is not None or not hasattr(self.app_config, 'default_meta_tags') \
                        or meta not in self.app_config.default_meta_tags:
                    meta_value = response.meta_tags[meta]
                else:
                    meta_value = self.app_config.default_meta_tags[meta]
                if meta_value:
                    head += f'<meta name="{meta}" content="{html_escape(meta_value)}">'

            # Head includes
            head += component_includes.render_head_includes()

            head += "</head>"
            return head

        def render_body_tag(component_includes: ComponentIncludes, rendered_blocks: dict[str, str]) -> str:
            body = '<body>'

            # Page content
            body += rendered_blocks['main']

            # Body includes
            body += component_includes.render_body_includes()
            body += '</body>'
            return body

        return '<!DOCTYPE html><html>' \
               + render_head_tag(ns.content, ns.component_includes) \
               + render_body_tag(ns.component_includes, ns.rendered_blocks) + '</html>'
