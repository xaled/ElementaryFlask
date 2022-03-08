# from abc import ABC, abstractmethod
# from flaskup.typing import RenderReturnValue
# from flaskup.components import AbstractComponent, ComponentIncludes
#
#
# class Form(AbstractComponent, ABC):
#     def __init__(self, component_includes: ComponentIncludes = None):
#         super(Form, self).__init__(component_includes=component_includes)
#         self.form_controls = list()
#         self.form_arguments = list()
#         self.submit_func = None
#         self.submit_func_name = None
#
#     def render(self, **options) -> RenderReturnValue:
#         pass
#
#     def render_form(self):
#         pass
#
#     def __call__(self, *args, **kwargs):
#         return self.submit_func(*args, **kwargs)
#
#     @staticmethod
#     def make_form(func, name, arguments):
#         ret = Form(**arguments)
#         ret.submit_func = func
#         ret.submit_func_name = name
#
