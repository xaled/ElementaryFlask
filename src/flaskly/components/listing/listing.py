from abc import ABC, abstractmethod
from dataclasses import dataclass

from flask import request
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict

from flaskly.components.form import error
from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import RenderReturnValue, FormResponseReturn
from ..component import AbstractComponent

SUBMIT_METHODS = ("POST", "PUT", "PATCH", "DELETE")


@dataclass()
class ListingAction:
    name: str
    batch: bool = False
    form_cls: type = None


class AbstractListing(AbstractComponent, ABC):
    fields = None
    id_field = None
    item_view_uri = None
    _actions = None

    def __init__(self):
        super(AbstractListing, self).__init__()
        self.view_page_kwargs = None

    def __call__(self, **kwargs):
        if bool(request) and request.method == 'GET':
            self.view_page_kwargs = kwargs
            return self
        if _is_submitted():
            return self.on_submit()
        return False

    @abstractmethod
    def list_items(self, page=1, items_per_page=20, filters=None):
        raise NotImplementedError()

    @abstractmethod
    def __len__(self):
        raise NotImplementedError()

    def render(self, **options) -> RenderReturnValue:
        if self._actions is None:
            self.init_actions()

        ret = _app.core_jinja_env.render_template("listing/default_listing.html",
                                                  listing=self,
                                                  )
        self.view_page_kwargs = None
        return ret

    @classmethod
    def init_actions(cls):
        actions = list()
        for key in dir(cls):
            itm = getattr(cls, key)
            if callable(itm) and getattr(itm, 'flaskly_listing_action', False):
                actions.append(key)
        cls._actions = tuple(actions)

    def on_submit(self) -> FormResponseReturn:
        if self._actions is None:
            self.init_actions()
        formdata, action_name, ids = _get_form_data_splits()

        if ids is None:
            return error('No item ID was sent!')

        if action_name is None or not action_name in self._actions:
            return error('Unknown action was sent!')

        action_func = getattr(self, self._actions[action_name])
        action = action_func.flaskly_listing_action

        if not (action.batch or isinstance(ids, str)) or not (action.form_cls is None or formdata):
            return error('Error processing action data!')

        ids = [ids] if isinstance(ids, str) and action.batch else ids
        if action.form_cls:
            return action_func(ids, action.form_cls(formdata=formdata))
        return action_func(ids)

    @classmethod
    def page_view(cls, **kwargs):
        return cls()(**kwargs)


def listing_action(name=None, batch=False, form_cls=None):
    def decorator(f):
        n = name or f.__name__
        f.flaskly_listing_action = ListingAction(n, batch=batch, form_cls=form_cls)
        return f

    return decorator


def _get_form_data_splits():
    if _is_submitted():
        if request.files:
            return _split_form_data(CombinedMultiDict((request.files, request.form)))
        elif request.form:
            return _split_form_data(request.form)
        elif request.get_json():
            return _split_form_data(ImmutableMultiDict(request.get_json()))

    return None, None


def _split_form_data(obj):
    ret = dict(**obj)
    action = ret.pop('action', None)
    ids = ret.pop('ids', None)
    return ImmutableMultiDict(ret), action, ids


def _is_submitted():
    return bool(request) and request.method in SUBMIT_METHODS
