from dataclasses import dataclass, field

from flaskly.includes import BootstrapDependency, ComponentIncludes
from flaskly.typing import Optional
from .page_layout import LayoutMapping


@dataclass()
class Theme:
    bootstrap_dependency: Optional[BootstrapDependency] = None
    default_includes: Optional[ComponentIncludes] = field(default_factory=ComponentIncludes)
    layouts_mapping: LayoutMapping = field(default_factory=LayoutMapping)

    def __post_init__(self):
        self.default_includes = self.default_includes or ComponentIncludes()
        if self.bootstrap_dependency:
            self.default_includes.dependencies.insert(0, self.bootstrap_dependency)
