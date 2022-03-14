import json

from flask import url_for


def form_json_state(form):
    return json.dumps(form_state(form))


def form_state(form):
    errors = []
    for k in form.errors:
        errors.extend(form.errors[k])

    return dict(
        id=form.flaskly_form_id,
        method='POST',
        uri=url_for(form.flaskly_form_id),
        data=form.data,
        errors=errors,

    )
