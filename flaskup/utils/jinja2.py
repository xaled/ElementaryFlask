from jinja2 import Environment


class Jinja2Env:
    def __init__(self, jinja2_env: Environment):
        self.jinja2_env = jinja2_env

    def render_template(self, template_name, **options):
        return self.jinja2_env.get_template(template_name).render(**options)
