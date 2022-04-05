from elementary_flask.components import EmptyPageLayout, render
from ._jinja2_env import jinja2_env


class AdminLTEDefaultLayout(EmptyPageLayout):
    def render_body_tag(self, **options) -> str:
        return jinja2_env.render_template('layouts/default_body.html',
                                          main=self.render_main_block(**options),
                                          body_includes=self.reduce_includes().render_body_includes()
                                          )
        # rendered_blocks = ns.rendered_blocks
        # component_includes = ns.component_includes
        #
        # body = '<body>'
        #
        # # Page content
        # body += rendered_blocks['main']
        #
        # # Body includes
        # body += component_includes.render_body_includes()
        # body += '</body>'
        # return body

    def render_main_block(self, page_response, **options):
        return render(page_response.blocks['main'])

# class AdminLTEErrorLayout(EmptyPageLayout):
#     def render_main_block(self, page_response: PageErrorResponse, **options):
#         return jinja2_env.render_template('components/error.html',
#                                           error_message=render_error.error_message,
#                                           status_code=render_error.status_code,
#                                           error_color='danger' if render_error.status_code >= 500 else 'warning',
#                                           )
