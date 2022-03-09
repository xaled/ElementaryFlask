from dataclasses import dataclass

from flaskly.typing import Optional


@dataclass()
class RenderResponse:
    content: Optional[str] = None
