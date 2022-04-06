# __all__ = ['MarkupPlus', 'RenderException']  # , 'RenderError']


# class MarkupPlus:
#     def __init__(self,
#                  markup: Optional[Union[str, Markup]] = "",
#                  # headers: Optional[Dict] = None,
#                  # additional_blocks: Optional[BlocksDict] = None,
#                  # init_js: str = None,
#                  # init_alpine: str = None,
#                  # init_dict: Dict = None,
#                  ):
#         self.markup = markup if isinstance(markup, Markup) else Markup(markup)
#         # self.additional_blocks = additional_blocks or dict()
#         # self.init_dict = defaultdict(list)
#         # self._extend_init_dict(init_dict)
#         #
#         # for key, var in (('js', init_js), ('alpine', init_alpine),):
#         #     if var:
#         #         self.init_dict[key].append(var)
#
#     def copy(self):
#         return MarkupPlus(markup=self.markup,
#                           # headers=dict(self.headers),
#                           # additional_blocks=dict(self.additional_blocks),
#                           # init_dict=self.init_dict,
#                           )
#
#     def __repr__(self):
#         return self.markup
#
#     def __str__(self):
#         return self.markup
#
#     def __call__(self):
#         return self.markup
#
#     def __html__(self):
#         return self.markup
#
#     def __add__(self, other):
#         if not other:
#             return self
#
#         if isinstance(other, str) or isinstance(other, Markup):
#             res = self.copy()
#             res.markup += other
#             return res
#
#         # if isinstance(other, RenderError):
#         #     # res = other.copy()
#         #     # res.content = self.content + other.content
#         #     # return res
#         #     raise RenderException(render_error=other)
#
#         if isinstance(other, MarkupPlus):
#             res = self.copy()
#             res.markup += other.markup
#             # res.headers.update(other.headers)
#             # res.additional_blocks.update(other.additional_blocks)  # TODO: additional blocks concatenation
#             # res._extend_init_dict(other.init_dict)
#             return res
#
#         return self  # raise error??
#
#     def __radd__(self, other):
#         if not other:
#             return self
#         other = MarkupPlus(markup=other if isinstance(other, Markup) else escape(other))
#         return other + self
#
#     # def _extend_init_dict(self, other_init_dict):
#     #     if other_init_dict:
#     #         for k, v in other_init_dict.items():
#     #             self.init_dict[k].extend(self.init_dict[v])


# class RenderError(MarkupPlus):
#     def __init__(self, error_message='Render Error', status_code=500):
#         super(RenderError, self).__init__(content=error_message, status_code=status_code)
#         self.error_message = error_message
#
#     def copy(self):
#         return RenderError(error_message=self.error_message, status_code=self.status_code)
#
#     def __add__(self, other):
#         raise RenderException(render_error=self)
#
#     def __radd__(self, other):
#         raise RenderException(render_error=self)


# class RenderException(Exception):
#     def __init__(self, render_error=None, error_message="Render Error", status_code=500):
#         render_error = render_error or RenderError(error_message=error_message, status_code=status_code)
#         super(RenderException, self).__init__(render_error.error_message)
#         self.render_error = render_error


# class RenderException(Exception):
#     pass
