# from flaskup.typing import Callable
# from .form import Form
# from .form_argument import FormArgument
#
#
# def form_argument(**options):
#     """
#     Attaches an argument to the form.
#
#     :param options: options past to init FormArgument class
#     """
#
#     def decorator(f):
#         argument = FormArgument(**options)
#         if isinstance(f, Form):
#             f.form_arguments.append(argument)
#         else:
#             if not hasattr(f, "__flaskup_form_items__"):
#                 f.__flaskup_form_items__ = []  # type: ignore
#
#             f.__flaskup_form_items__.append(argument)  # type: ignore
#         return f
#
#     return decorator
#
#
#
