import typing as _typing
from typing import Optional, List, Dict, AnyStr, Set

import flask.typing as _flask_typing

ResponseReturnValue = _flask_typing.ResponseReturnValue
OptionalList = Optional[List]
OptionalDict = Optional[Dict]
OptionalSet = Optional[Set]
OptionalAnyStr = Optional[AnyStr]
OptionalStr = Optional[str]
Union = _typing.Union
Callable = _typing.Callable
Any = _typing.Any
Tuple = _typing.Tuple

RenderReturnValue = Union["RenderResponse", Optional[str]]

# class Renderable:
#     def render(self, **options) -> RenderReturnValue:
#         raise NotImplementedError()


StatusCode = _flask_typing.StatusCode
HeadersValue = _flask_typing.HeadersValue
Block = Union[RenderReturnValue, "Renderable"]
BlocksDict = dict[str, Block]
BlocksInit = Union[Block, BlocksDict]
PageErrorResponseInit = Union[StatusCode, Tuple[StatusCode, str], Tuple[StatusCode, HeadersValue],
                              Tuple[StatusCode, str, HeadersValue]]
PageResponseInit = Union[BlocksInit, Tuple[BlocksInit, StatusCode], Tuple[BlocksInit, StatusCode, HeadersValue],
                         Tuple[BlocksInit, HeadersValue], PageErrorResponseInit]

PageRouteReturnValue = Union["PageResponse", PageResponseInit]
ComponentIncludes = "ComponentIncludes"
NavigationItem = Union["NavigationLink", "NavigationSeparator", "NavigationGroup"]
NavigationData = List[NavigationItem]

# class ChildrenRenderable:
#     def render_children(self) -> str:
#         raise NotImplementedError()
#
#
# class HeadTagRenderable:
#     def render_head_tag(self) -> str:
#         raise NotImplementedError()
#
#
# class BodyTagRenderable:
#     def render_body_tag(self) -> str:
#         raise NotImplementedError()
#
#
# class HTMLTagOpenRenderable:
#     def render_html_tag_open(self) -> str:
#         raise NotImplementedError()


# class AppContext:
#     def context(self) -> SimpleNamespace:
#         raise NotImplementedError()


# RouteReturnValue = _typing.Union[ResponseReturnValue, Renderable]
