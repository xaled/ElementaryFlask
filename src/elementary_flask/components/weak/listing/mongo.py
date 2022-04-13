__all__ = ["mongo_collection_admin_listing"]

from .listing import AbstractListing, default_listing_render


# def mongo_collection_admin_listing(
#         cls, *,
#         item_view_uri=None,
#         item_edit_uri=None,
#         item_edit_title=None,
#         item_edit_icon=None,
#         default_renderer=default_listing_render,
#         show_header=True,
#         items_per_page=20,
#         additional_filters=None,
#         additional_actions=None,
#         default_sort=None,
#         id_field='id',
#         listing_fields=None,
#         view_fields=None,
#         edit_fields=None,
#         filters_fields=None,
#
# ):
#     name = cls.__name__ + 'MongoCollection'
#     cls_fields = [k for k, v in cls._fields.items() if k != 'id']
#     view_fields = view_fields or cls_fields
#     edit_fields = edit_fields or cls_fields
#
#     def list_items(self, page=1, items_per_page=20, filters=None, query=None, sort=None):
#         if sort:
#             return self._mongo_document_cls.objects(
#                 **_mfilter(filters=filters, query=query)
#             ).order_by(*_msort(sort))[(page - 1) * items_per_page:page * items_per_page]
#         return self._mongo_document_cls.objects(
#             **_mfilter(filters=filters, query=query)
#         )[(page - 1) * items_per_page:page * items_per_page]
#
#     def count_items(self, filters=None, query=None):
#         return self._mongo_document_cls.objects(**_mfilter(filters=filters, query=query)).count()
#
#     cls_dict = dict(
#         _mongo_document_cls=cls,
#         list_items=list_items,
#         count_items=count_items,
#         columns=listing_fields,
#         id_field=id_field,
#         item_view_uri=item_view_uri,
#         item_edit_uri=item_edit_uri,
#         item_edit_title=item_edit_title,
#         item_edit_icon=item_edit_icon,
#         default_renderer=default_renderer,
#         show_header=show_header,
#         items_per_page=items_per_page,
#         default_sort=default_sort,
#     )
#     # TODO delete action
#     # cls_dict.update(actions)
#     # cls_dict.update(filters)
#
#     return type(
#         name,
#         (AbstractListing,),
#         cls_dict
#     )


def mongo_collection_admin_listing(
        document_cls, *,
        item_view_uri='./{}',
        item_view_title=None,
        item_view_icon="fas fa-eye",  # TODO generic icon
        item_edit_uri="./{}/edit",
        item_edit_title=None,
        item_edit_icon="fas fa-pen",  # TODO generic icon
        item_delete_func=None,
        item_delete_title=None,
        item_delete_icon="fas fa-trash",  # TODO: generic icon
        default_renderer=default_listing_render,
        show_header=True,
        items_per_page=20,
        additional_filters=None,
        additional_actions=None,
        default_sort=None,
        id_field='id',
        listing_fields=None,
        view_fields=None,
        edit_fields=None,
        filters_fields=None,
        click_action='view',

):
    cls_fields = [k for k, v in document_cls._fields.items() if k != 'id']
    listing_fields = listing_fields or cls_fields
    view_fields = view_fields or cls_fields
    edit_fields = edit_fields or cls_fields

    class _CLS(AbstractListing):
        _mongo_document_cls = document_cls

        def list_items(self, page=1, items_per_page=20, filters=None, query=None, sort=None):
            item_count = self.count_items(filters=None, query=None)
            # if item_count == 0:
            #     return []
            cursor = self._mongo_document_cls.objects(**_mfilter(filters=filters, query=query))
            if sort:
                cursor = cursor.order_by(*_msort(sort))
            slice_start = (page - 1) * items_per_page
            slice_end = page * items_per_page
            return cursor[slice_start:slice_end]

        def count_items(self, filters=None, query=None):
            return self._mongo_document_cls.objects(**_mfilter(filters=filters, query=query)).count()

        def delete(self, ids):
            from elementary_flask.form import toast
            docs = list(self._mongo_document_cls.objects(id__in=ids))
            for d in docs:
                d.delete()
            if len(docs) > 1 or len(docs) == 0:
                return toast("%d item are delete" % len(docs), message_type="success")  # TODO refresh items
            if len(docs) == 1:
                return toast("item is deleted", message_type="success")  # TODO refresh items

    cls_dict = dict(
        columns=listing_fields,
        id_field=id_field,
        item_view_uri=item_view_uri,
        item_view_title=item_view_title,
        item_view_icon=item_view_icon,
        item_edit_uri=item_edit_uri,
        item_edit_title=item_edit_title,
        item_edit_icon=item_edit_icon,
        item_delete_func=item_delete_func or _CLS.delete,
        item_delete_title=item_delete_title,
        item_delete_icon=item_delete_icon,
        default_renderer=default_renderer,
        show_header=show_header,
        items_per_page=items_per_page,
        default_sort=default_sort,
        click_action=click_action,
    )
    for k, v in cls_dict.items():
        setattr(_CLS, k, v)
    # _CLS.__dict__.update()
    # TODO delete action
    # cls_dict.update(actions)
    # cls_dict.update(filters)
    _CLS.__name__ = document_cls.__name__ + 'MongoListing'

    return _CLS


def _msort(sort=None):
    if not sort:
        return list()
    ret = list()
    for k, o in sort:
        ret.append(f'{"-" if o == "desc" else "+"}{k}')


def _mfilter(filters=None, query=None):
    # TODO query and filters
    return dict()
