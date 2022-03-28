from dataclasses import dataclass

from flaskly.typing import Callable


@dataclass()
class ListingAction:
    func: Callable
    name: str
    batch: bool = False
    form_cls: type = None
    hidden: bool = False

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def listing_action(name=None, /, *, batch=False, form_cls=None, hidden=False):
    def decorator(f):
        n = name or f.__name__
        # f.flaskly_listing_action =
        return ListingAction(f, n, batch=batch, form_cls=form_cls, hidden=hidden)

    return decorator
