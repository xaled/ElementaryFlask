from html import escape as html_escape

from elementary_flask.components import NormalContainer

RESPONSIVE_CONTAINER_BREAKPOINTS = ('fluid', 'sm', 'md', 'lg', 'xl', 'xxl')


class Row(NormalContainer):
    def __init__(self, children):
        super(Row, self).__init__(children, prefix="<div class='row'>", suffix="</div>")


class Col(NormalContainer):
    def __init__(self, children, col_class="col"):
        super(Col, self).__init__(children, prefix=f"<div class='{html_escape(col_class)}'>", suffix="</div>")


class ResponsiveContainer(NormalContainer):
    def __init__(self, children, container_breakpoint=None):
        if container_breakpoint is None or container_breakpoint not in RESPONSIVE_CONTAINER_BREAKPOINTS:
            container_breakpoint = ''
        else:
            container_breakpoint = '-' + container_breakpoint
        class_ = 'container' + container_breakpoint
        super(ResponsiveContainer, self).__init__(children,
                                                  prefix=f"<div class='{html_escape(class_)}'>", suffix="</div>")
