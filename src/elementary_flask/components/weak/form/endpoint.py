__all__ = ['form_endpoint_wrapper']
from elementary_flask.globals import current_elementary_flask_app as _app
from .response import FormResponse


def form_endpoint_wrapper(frm_cls):
    def _wrap():  # TODO typing form response
        _frm = frm_cls()
        if _frm.validate_on_submit():
            form_response = _frm.on_submit()
        else:
            # return toast('validation error')
            form_response = _frm

        if not isinstance(form_response, FormResponse):
            form_response = FormResponse(form_response)

        _app.logger.debug('Form %s submit data: %s, response: %s',
                          _frm.elementary_flask_form_id, _frm.data, form_response)
        return form_response.to_dict()

    return _wrap
