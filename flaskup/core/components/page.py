from html import escape as html_escape

from flaskup.typing import Renderable, Optional, ResponseReturnValue, OptionalStr, \
    HeadTagRenderable, BodyTagRenderable, HTMLTagOpenRenderable, Union
from .component import AbstractComponent, ComponentIncludes, AbstractContainer


class Page(AbstractComponent, HeadTagRenderable, BodyTagRenderable, HTMLTagOpenRenderable):
    def __init__(self,
                 title: OptionalStr = None,
                 additional_includes: Optional[ComponentIncludes] = None,
                 content: Union[ResponseReturnValue, AbstractContainer] = None,
                 description: OptionalStr = None,
                 keywords: OptionalStr = None,
                 author: OptionalStr = None,
                 viewport: OptionalStr = None,

                 ):
        super(Page, self).__init__()

        # Includes
        page_includes = ComponentIncludes() if not isinstance(content, AbstractContainer) \
            else content.component_includes
        if hasattr(self.app_config, 'default_includes'):
            page_includes = self.app_config.default_includes + page_includes
        if additional_includes:
            page_includes = content.component_includes + additional_includes
        self.component_includes = page_includes

        # Content & Meta
        self.title = title
        self.content = content
        self.meta_tags = dict(description=description, keywords=keywords, author=author, viewport=viewport)

    def render(self) -> ResponseReturnValue:
        if self.content is None or isinstance(self.content, Renderable) or isinstance(self.content, str):
            return '<!DOCTYPE html>' + self.render_html_tag_open() + self.render_head_tag() + self.render_body_tag() \
                   + '</html>'
        return self.content

    def render_head_tag(self) -> str:
        head = "<head>"

        # Charset
        head += '<meta charset="UTF-8">'

        # Fav icons
        if hasattr(self.app_config, 'icons'):
            for icon in self.app_config.icons:
                head += icon.rendered

        # Title
        title = self.title if self.title is not None or not hasattr(self.app_config, 'default_title') \
            else self.app_config.default_title
        if title is not None:
            head += f'<title>{html_escape(title)}</title>'

        # Meta tags
        for meta in ('description', 'keywords', 'author', 'viewport'):
            if self.meta_tags[meta] is not None or not hasattr(self.app_config, 'default_meta_tags') \
                    or meta not in self.app_config.default_meta_tags:
                meta_value = self.meta_tags[meta]
            else:
                meta_value = self.app_config.default_meta_tags[meta]
            if meta_value:
                head += f'<meta name="{meta}" content="{html_escape(meta_value)}">'

        # Head includes
        head += self.component_includes.render_head_includes()

        head += "</head>"
        return head

    def render_body_tag(self) -> str:
        body = '<body>'

        # Page content
        body += self.render_content()

        # Body includes
        body += self.component_includes.render_body_includes()
        body += '</body>'
        return body

    def render_content(self) -> str:
        if isinstance(self.content, Renderable):
            return self.content.render()
        elif isinstance(self.content, str):
            return self.content
        elif self.content is None:
            return ''
        else:
            raise "Content is neither String or Renderable"

    def render_html_tag_open(self) -> str:
        return '<html>'
