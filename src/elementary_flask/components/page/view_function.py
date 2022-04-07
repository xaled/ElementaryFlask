__all__ = ['page_view_wrapper']

from flask import Response

from elementary_flask.globals import current_elementary_flask_app as _app
import elementary_flask.typing as t
from .page_response import PageResponse, PageErrorResponse, make_page_response


def page_view_wrapper(f: t.Callable[..., t.PageRouteReturnValue], default_page_layout='default'):
    def _wrap(*args, **kwargs) -> t.ResponseReturnValue:
        # p = cls(*args, **kwargs)
        # return p.render()
        page_response = f(*args, **kwargs)
        if isinstance(page_response, Response):
            return page_response
        # if isinstance(page_response, FormResponse):  # TODO FormResponse should not go through page_view_function
        #     return page_response.to_dict()
        if not isinstance(page_response, PageResponse):
            page_response = make_page_response(page_response)
        pl = page_response.page_layout if page_response.page_layout is not None else default_page_layout
        # try:
        if isinstance(page_response, PageErrorResponse):
            render_response = _app.get_layout('error').render(page_response=page_response)
        else:
            render_response = _app.get_layout(pl).render(page_response=page_response)

        # except RenderException as e: # TODO: let the exception raise or keep the page structure and show error
        #     render_response = self.get_layout('error').render(render_error=e.render_error)

        # if isinstance(render_response, RenderError): already handled
        #     return render_response.error_message, render_response.status_code  # Todo error template

        # if isinstance(render_response, MarkupPlus):
        #     if render_response.status_code is not None:
        #         return render_response.content, render_response.status_code, render_response.headers
        #     else:
        #         return render_response.content, render_response.headers
        # else:
        #     return render_response
        return render_response

    return _wrap
