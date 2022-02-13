from dataclasses import dataclass, field

from flaskup.typing import OptionalSet


@dataclass(frozen=True)
class ComponentIncludes:
    css_includes: OptionalSet = field(default_factory=set)
    js_includes: OptionalSet = field(default_factory=set)

    def __add__(self, other):
        return ComponentIncludes(
            css_includes=self.css_includes.union(other.css_includes),
            js_includes=self.js_includes.union(other.js_includes),
        )

    def render_head_includes(self):
        # TODO advanced tags: integrity, crossorigin
        # TODO js head includes
        return ''.join(f'<link href="{css_link}" rel="stylesheet" crossorigin="anonymous">'
                       for css_link in self.css_includes)

    def render_body_includes(self):
        # TODO: integrity check, crossorigin
        return ''.join(f'<script src="{js_link}"></script>' for js_link in self.js_includes)
