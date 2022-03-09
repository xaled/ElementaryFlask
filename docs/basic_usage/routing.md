# Page Routing
Page Routing is build upon [Flask routing](https://flask.palletsprojects.com/en/latest/quickstart/#routing).

Use the [route_page()](route_page) decorator to bind a function to a URL.

```python
@app.route_page('/hello_world')
@app.route_page('/hello_world/<name>')
def hello_world(name=None):
    if name:
        return 'Hello World ' + name
    return 'Hello World'
```

You can also return a [Renderable](Renderable) object instead of a string:

```python
from flaskly.components import AbstractComponent


class HelloWorldComponent(AbstractComponent)
    def __init__(name=None):
        super(HelloWorldComponent, self).__init__()
        self.name = name

    def render(self, **options):
        if self.name:
            return 'Hello World ' + self.name
        return 'Hello World'


@app.route_page('/hello_world')
@app.route_page('/hello_world/<name>')
def hello_world(name=None):
     return HelloWorldComponent(name)
```
However unlink Flask routing, the rendered string will be included in a {doc}`page_layout`:

**todo:** screenshot


## Flask Routing
You access flask app with the attribute `flask_app` and call the default [route()](https://flask.palletsprojects.com/en/latest/quickstart/#routing) decorator:

```python
@app.flask_app.route('/hello_world')
def hello_world():
    return 'hello_world'
```

## Page Layout
By default Flaskly renders the result using `'default'` {doc}`page_layout`.
You can change the page_layout to a builtin or a custom using the `page_layout` argument.

```python
@app.route_page('/hello_world', page_layout='custom_page_layout')
def hello_world():
    return 'Hello World'

```
**todo:** screenshot

## Navigation
You can include your page in the default application navigation using `navigation` and `navigation_title` arguments:

```python
@app.route_page('/hello_world', navigation=True, navigation_title="Hello World")
def hello_world():
    return 'Hello World'

```
**todo:** screenshot

```{admonition} Nota Bene
The order of navigation items is the order in which view functions are implemented and imported.
If you want to control the order of navigation, it's better to register the whole navigation map using the function xxxx:

**todo:** code example
```

## Error messages
To return an error message you can either return a tuple of status code and string message or and [PageErrorResponse](PageErrorResponse) object:
```python
@app.route_page('/error_test')
def error_test():
    return 404, "Error Test"
```

The error message will be rendered with the builtin `error` {doc}`page_layout`.

**todo:** screenshot