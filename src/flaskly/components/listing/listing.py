from abc import ABC, abstractmethod
from urllib.parse import urlencode

from flask import request
from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict

from flaskly.components.form import error, FormResponse
from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import FormResponseReturn
from .action import ListingAction
from .field import ListingColumn
from .renderer import default_listing_render
from ..weak_component import AbstractWeakComponent

SUBMIT_METHODS = ("POST", "PUT", "PATCH", "DELETE")


class AbstractListing(AbstractWeakComponent, ABC):
    columns = None
    id_field = None
    item_view_uri = None
    item_edit_uri = None
    _actions = None
    _columns = None
    _init = False
    default_renderer = default_listing_render
    show_header = True
    items_per_page = 20

    def __init__(self):
        super(AbstractListing, self).__init__()
        self.view_page_kwargs = None
        self.view_form = FlaskForm()

    def __call__(self, **kwargs):
        if bool(request) and request.method == 'GET':
            self.view_page_kwargs = kwargs
            return self
        if _is_submitted():
            # TODO: validate on submit

            form_response = self.on_submit()

            if not isinstance(form_response, FormResponse):
                form_response = FormResponse(form_response)

            _app.logger.debug('Listing %s action submit data: %s, response: %s',
                              self.__class__.__name__, request.form, form_response)
            return form_response
        return False

    def list_items_request(self):
        def _correct_page(p, mp):
            if p < 1:
                p = 1
            if p > mp:
                p = mp
            return p

        def _page_uri(p, f):
            t = (("page", p),)
            if f:
                t += (('filters', f),)
            return '?' + urlencode(t)

        try:
            page = request.args.get('page', 1, type=int)
        except:
            page = 1
        items_per_page = self.items_per_page
        filters = request.args.get('filters', None)
        c_total = self.count_items(filters=filters)
        max_page = (c_total // items_per_page) + (1 if c_total % items_per_page else 0)
        page = _correct_page(page, max_page)

        c_f = (page - 1) * items_per_page + 1
        c_t = min(page * items_per_page, c_total)
        next_page = _page_uri(_correct_page(page + 1, max_page), filters)
        previous_page = _page_uri(_correct_page(page - 1, max_page), filters)
        count_str = f"{c_f}-{c_t}/{c_total}"
        return self.list_items(
            page=page, items_per_page=items_per_page, filters=filters), count_str, next_page, previous_page

    @abstractmethod
    def list_items(self, page=1, items_per_page=20, filters=None):
        raise NotImplementedError()

    @abstractmethod
    def count_items(self, filters=None):
        raise NotImplementedError()

    def __len__(self):
        return self.count_items()

    @classmethod
    def init_listing_cls(cls):
        if not cls._init:
            actions = list()
            columns = dict()

            if cls.columns is not None:
                for column_or_name in cls.columns:
                    if isinstance(column_or_name, ListingColumn):
                        columns[column_or_name.name] = column_or_name
                    else:
                        columns[column_or_name] = ListingColumn(column_or_name)

            for key in dir(cls):
                itm = getattr(cls, key)
                # if getattr(itm, 'flaskly_listing_action', False) and callable(itm):
                if isinstance(itm, ListingAction):
                    actions.append(key)
                if isinstance(itm, ListingColumn):
                    columns[itm.name] = itm
            cls._actions = tuple(actions)

            # columns = dict()

            cls._columns = tuple(sorted(columns.values(), key=lambda x: x.order))
            cls._init = True

    def on_submit(self) -> FormResponseReturn:
        # if self._actions is None:
        self.init_listing_cls()
        formdata, action_name, ids = _get_form_data_splits()

        if ids is None:
            return error('No item ID was sent!')

        if action_name is None or action_name not in self._actions:
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

    def hidden_thead(self):
        return "" if self.show_header else "hidden"

    # @classmethod
    # def field_title(cls, field_name):
    #     if not hasattr(cls, field_name + '_field_title'):
    #         setattr(cls, field_name + '_field_title', field_name)
    #     return getattr(cls, field_name + '_field_title')
    #
    # @classmethod
    # def field_generator(cls, field_name):
    #     def _generator(itm):
    #         return getattr(itm, field_name, None)
    #
    #     if not hasattr(cls, field_name + '_generator'):
    #         setattr(cls, field_name + '_generator', _generator)
    #     return getattr(cls, field_name + '_generator')
    #
    # @classmethod
    # def field_formatter(cls, field_name):
    #     def _formatter(val):
    #         return html_escape(val)
    #
    #     if not hasattr(cls, field_name + '_formatter'):
    #         setattr(cls, field_name + '_formatter', _formatter)
    #     return getattr(cls, field_name + '_formatter')
    #
    # @classmethod
    # def field_html_generator(cls, field_name):
    #     def _html_generator(itm):
    #         return cls.field_formatter(field_name)(cls.field_generator(field_name)(itm))
    #
    #     if not hasattr(cls, field_name + '_html_generator'):
    #         setattr(cls, field_name + '_html_generator', _html_generator)
    #     return getattr(cls, field_name + '_html_generator')


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
