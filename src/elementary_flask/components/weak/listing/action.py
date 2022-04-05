__all__ = ['ListingAction', 'listing_action']
from dataclasses import dataclass

from markupsafe import Markup

from elementary_flask.typing import Callable, AbstractIcon, Union
from ... import IClassIcon


@dataclass()
class ListingAction:
    func: Callable
    name: str
    batch: bool = False
    form_cls: type = None
    hidden: bool = False
    title: str = None
    icon: Union[AbstractIcon, str] = None

    # TODO: button component

    def __post_init__(self):
        if self.icon and isinstance(self.icon, str):
            self.icon = IClassIcon(self.icon)

    def button_inner_html(self):
        if self.title and self.icon:
            return Markup(self.icon.render()) + " " + self.title
        if self.title:
            return self.title
        if self.icon:
            return Markup(self.icon.render())
        return self.name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def listing_action(name=None, /, *, batch=False, form_cls=None, hidden=False, icon=None, title=None):
    def decorator(f):
        n = name or f.__name__
        # f.elementary_flask_listing_action =
        return ListingAction(f, n, batch=batch, form_cls=form_cls, hidden=hidden, icon=icon, title=title)

    return decorator
