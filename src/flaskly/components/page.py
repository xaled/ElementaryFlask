# from html import escape as html_escape
#
# from flaskly.typing import Renderable, Optional, ResponseReturnValue, Union
# from .component import AbstractComponent, ComponentIncludes, AbstractContainer
# from .page_layout import PageResponse, AbstractPageLayout
# from flaskly.globals import current_flaskly_app
#
#
# class Page(AbstractComponent):
#     pass
#     # def __init__(self, page_layout='default',
#     #              content: Union[ResponseReturnValue, AbstractContainer] = None,
#     #              ):
#     #     super(Page, self).__init__()
#     #     self.page_layout = page_layout
#     #     self.content = content
#     #
#     # def render(self, **options) -> ResponseReturnValue:
#     #     return current_flaskly_app.get_page_layout(self.page_layout).render_response(self.content)
#     #
#