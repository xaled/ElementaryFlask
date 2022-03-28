from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from html import escape as html_escape
from urllib.parse import urlencode

from flask import request
from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict

from flaskly.components.form import error, FormResponse
from flaskly.globals import current_flaskly_app as _app
from flaskly.typing import RenderReturnValue, FormResponseReturn, Callable
from ..weak_component import AbstractWeakComponent

SUBMIT_METHODS = ("POST", "PUT", "PATCH", "DELETE")


@dataclass()
class ListingAction:
    func: Callable
    name: str
    batch: bool = False
    form_cls: type = None
    hidden: bool = False

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


@dataclass()
class ListingField:
    field_name: str
    field_title: str = None
    shrink_cell: bool = False
    td_class: str = None
    th_class: str = None
    safe_html: bool = False
    generator: Callable = None
    formatter: Callable = None
    order: int = 5
    _td_class: str = field(init=False, default=None)
    _th_class: str = field(init=False, default=None)

    def td(self, item):
        val = self.generator(item) if self.generator is not None else getattr(item, self.field_name, "None")
        if not self.safe_html:
            val = html_escape(val)
        if self.formatter:
            val = self.formatter(val)

        if self._td_class is None:
            _td_class = ((self.td_class or "") + " shrink-cell" if self.shrink_cell else "").strip()
            self._td_class = f'class="{_td_class}"' if _td_class else ""

        return f"""<td {self._td_class}>{val}</td>"""

    def th(self):
        if self.field_title is None:
            self.field_title = self.field_name
        if self._th_class is None:
            _th_class = ((self.th_class or "") + " shrink-cell" if self.shrink_cell else "").strip()
            self._th_class = f'class="{_th_class}"' if _th_class else ""
        return f"""<th {self._th_class} scope="col">{self.field_title}</th>"""


def default_listing_render(listing: "AbstractListing", /, **options) -> RenderReturnValue:
    listing.init_listing_cls()
    items, count_str, next_page, previous_page = listing.list_items_request()
    ret = _app.core_jinja_env.render_template("listing/default_listing.html",
                                              listing=listing,
                                              items=items, count_str=count_str,
                                              next_page=next_page, previous_page=previous_page,
                                              )
    listing.view_page_kwargs = None
    return ret


def listing_field(field_name, /, *,
                  field_title: str = None,
                  shrink_cell: bool = False,
                  td_class: str = None,
                  th_class: str = None,
                  safe_html: bool = False,
                  formatter: Callable = None,
                  order: int = 5):
    def decorator(f):
        return ListingField(field_name,
                            field_title=field_title,
                            shrink_cell=shrink_cell,
                            td_class=td_class,
                            th_class=th_class,
                            safe_html=safe_html,
                            formatter=formatter,
                            order=order,
                            generator=f)

    return decorator


def listing_action(name=None, /, *, batch=False, form_cls=None, hidden=False):
    def decorator(f):
        n = name or f.__name__
        # f.flaskly_listing_action =
        return ListingAction(f, n, batch=batch, form_cls=form_cls, hidden=hidden)

    return decorator


class AbstractListing(AbstractWeakComponent, ABC):
    fields = None
    id_field = None
    item_view_uri = None
    item_edit_uri = None
    _actions = None
    _fields = None
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
            fields = dict()

            if cls.fields is not None:
                for field_or_field_name in cls.fields:
                    if isinstance(field_or_field_name, ListingField):
                        fields[field_or_field_name.field_name] = field_or_field_name
                    else:
                        fields[field_or_field_name] = ListingField(field_or_field_name)

            for key in dir(cls):
                itm = getattr(cls, key)
                # if getattr(itm, 'flaskly_listing_action', False) and callable(itm):
                if isinstance(itm, ListingAction):
                    actions.append(key)
                if isinstance(itm, ListingField):
                    fields[itm.field_name] = itm
            cls._actions = tuple(actions)

            # fields = dict()

            cls._fields = tuple(sorted(fields.values(), key=lambda x: x.order))
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
