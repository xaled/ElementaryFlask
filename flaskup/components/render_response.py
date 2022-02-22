from dataclasses import dataclass

from flaskup.typing import Optional


@dataclass()
class RenderResponse:
    content: Optional[str] = None
