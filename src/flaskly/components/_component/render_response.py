__all__ = ['RenderResponse', 'RenderError', 'RenderException']
from dataclasses import dataclass, field

from flaskly.typing import Optional, Dict, BlocksDict


@dataclass()
class RenderResponse:
    content: Optional[str] = None
    headers: Optional[Dict] = field(default_factory=dict)
    additional_blocks: Optional[BlocksDict] = field(default_factory=dict)
    status_code: int = None

    def copy(self):
        return RenderResponse(content=self.content, headers=dict(self.headers),
                              additional_blocks=dict(self.additional_blocks),
                              status_code=self.status_code)

    def __str__(self):
        return self.content

    def __add__(self, other):
        if isinstance(other, str):
            res = self.copy()
            res.content += other
            return res

        if isinstance(other, RenderError):
            # res = other.copy()
            # res.content = self.content + other.content
            # return res
            raise RenderException(render_error=other)

        if isinstance(other, RenderResponse):
            res = self.copy()
            res.content += other.content
            res.headers.update(other.headers)
            res.additional_blocks.update(other.additional_blocks)  # TODO: additional blocks concatenation
            return res

        return self  # raise error??

    def __radd__(self, other):
        other = RenderResponse(content=other)
        return other + self


class RenderError(RenderResponse):
    def __init__(self, error_message='Render Error', status_code=500):
        super(RenderError, self).__init__(content=error_message, status_code=status_code)
        self.error_message = error_message

    def copy(self):
        return RenderError(error_message=self.error_message, status_code=self.status_code)

    def __add__(self, other):
        raise RenderException(render_error=self)

    def __radd__(self, other):
        raise RenderException(render_error=self)


class RenderException(Exception):
    def __init__(self, render_error=None, error_message="Render Error", status_code=500):
        render_error = render_error or RenderError(error_message=error_message, status_code=status_code)
        super(RenderException, self).__init__(render_error.error_message)
        self.render_error = render_error
