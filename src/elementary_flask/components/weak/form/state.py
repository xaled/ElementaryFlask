__all__ = ['form_state', 'form_json_state']
import json

from flask import url_for


def form_json_state(form):
    return json.dumps(form_state(form))


def form_state(form):
    errors = dict()
    for k in list(form.data.keys()) + [None]:
        errors[k or ''] = '; '.join(form.errors.get(k, []))

    return dict(
        id=form.elementary_flask_form_id,
        method='POST',
        uri=url_for(form.elementary_flask_form_id),
        data=form.data,
        errors=errors,

    )
