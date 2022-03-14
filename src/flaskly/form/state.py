import json

from flask import url_for


def form_json_state(form):
    return json.dumps(form_state(form))


def form_state(form):
    errors = dict()
    for k in list(form.data.keys()) + [None]:
        errors[k or ''] = '; '.join(form.errors.get(k, []))

    return dict(
        id=form.flaskly_form_id,
        method='POST',
        uri=url_for(form.flaskly_form_id),
        data=form.data,
        errors=errors,

    )
