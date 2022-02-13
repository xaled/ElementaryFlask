import typing as _typing
from types import SimpleNamespace
from typing import Optional, List, Dict, AnyStr, Set

import flask.typing as _flask_typing

ResponseReturnValue = _flask_typing.ResponseReturnValue
# TODO generics of the following
OptionalList = Optional[List]
OptionalDict = Optional[Dict]
OptionalSet = Optional[Set]
OptionalAnyStr = Optional[AnyStr]
OptionalStr = Optional[str]
Union = _typing.Union


class Renderable:
    def render(self) -> ResponseReturnValue:
        raise NotImplementedError()


class ChildrenRenderable:
    def render_children(self) -> str:
        raise NotImplementedError()


class HeadTagRenderable:
    def render_head_tag(self) -> str:
        raise NotImplementedError()


class BodyTagRenderable:
    def render_body_tag(self) -> str:
        raise NotImplementedError()


class HTMLTagOpenRenderable:
    def render_html_tag_open(self) -> str:
        raise NotImplementedError()


class AppContext:
    def context(self) -> SimpleNamespace:
        raise NotImplementedError()


RouteReturnValue = _typing.Union[ResponseReturnValue, Renderable]
