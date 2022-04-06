from elementary_flask.components import NormalContainer

RESPONSIVE_CONTAINER_BREAKPOINTS = ('fluid', 'sm', 'md', 'lg', 'xl', 'xxl')


class Row(NormalContainer):
    html_tag = 'div'
    classes = 'row'

    def __init__(self, children):
        super(Row, self).__init__(children)


class Col(NormalContainer):
    html_tag = 'div'
    classes = 'col'

    def __init__(self, children, extra_classes=None):
        super(Col, self).__init__(children, extra_classes=extra_classes)


class ResponsiveContainer(NormalContainer):
    html_tag = 'div'

    def __init__(self, children, container_breakpoint=None):
        if container_breakpoint is None or container_breakpoint not in RESPONSIVE_CONTAINER_BREAKPOINTS:
            container_breakpoint = ''
        else:
            container_breakpoint = '-' + container_breakpoint
        class_ = 'container' + container_breakpoint
        super(ResponsiveContainer, self).__init__(children,
                                                  extra_classes=class_)
