from flask import render_template

from flaskup.components import AbstractComponent
from flaskup.typing import RenderReturnValue


class PageErrorComponents(AbstractComponent):
    def __init__(self):
        super(PageErrorComponents, self).__init__()

    def render(self, **options) -> RenderReturnValue:
        return render_template('error.html', status_code=options.response.status_code, status_code_msg='aaaaa!')
