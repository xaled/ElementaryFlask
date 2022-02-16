from dataclasses import dataclass, field
from types import SimpleNamespace

from flaskup.typing import Optional, BlockInit, BlockDict, HeadersValue, PageResponseInit
from .component import ComponentIncludes, reduce_includes


@dataclass()
class PageResponse:
    block_init: BlockInit
    component_includes: ComponentIncludes = field(init=False)
    ns: SimpleNamespace = field(default_factory=SimpleNamespace)
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    author: Optional[str] = None
    viewport: Optional[str] = None
    headers: Optional[HeadersValue] = None
    status_code: Optional[int] = None
    status_code_msg: Optional[str] = None
    status_code_error: bool = False
    page_layout: Optional[str] = None
    blocks: BlockDict = field(init=False)

    def __post_init__(self):
        if not isinstance(self.block_init, dict):
            self.blocks = {'main': self.block_init}
        else:
            self.blocks = self.block_init
        self.component_includes = reduce_includes(self.blocks.items())
        self.meta_tags = dict(description=self.description, keywords=self.keywords, author=self.author,
                              viewport=self.viewport)


class PageErrorResponse(PageResponse):
    def __init__(self, status_code, status_code_msg=None, page_layout=None, headers=None):
        # TODO default status_code_msg for status_code
        if page_layout is None:
            page_layout = 'error'
        super(PageErrorResponse, self).__init__(None, status_code=status_code, status_code_msg=status_code_msg,
                                                page_layout=page_layout, title=status_code_msg,
                                                headers=headers)


def make_page_response(response_init: PageResponseInit, page_layout=None):
    if not isinstance(response_init, tuple):
        response_init = (response_init,)

    if isinstance(response_init[0], int):  # Page error
        status_code = response_init[0]
        status_code_msg = None
        headers = None
        if len(response_init) == 3:
            status_code_msg, headers = response_init[1], response_init[2]
        elif len(response_init) == 2:
            if isinstance(response_init[1], str):
                status_code_msg = response_init[1]
            else:
                headers = response_init[1]
        return PageErrorResponse(status_code, page_layout=page_layout,
                                 status_code_msg=status_code_msg, headers=headers)
    else:
        block_init = response_init[0]
        headers = None
        status_code = None
        if len(response_init) == 3:
            status_code, headers = response_init[1], response_init[2]
        elif len(response_init) == 2:
            if isinstance(response_init[1], int):
                status_code = response_init[1]
            else:
                headers = response_init[1]
        return PageResponse(block_init, page_layout=page_layout, status_code=status_code, headers=headers)
