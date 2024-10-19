# bf-pypy

https://pypy.org/posts/2011/04/tutorial-writing-interpreter-with-pypy-3785910476193156295.html

## Development

requires: PyPy @ v7.3.17

```bash
# create venv
pypy -m venv .venv
# activate venv
source .venv/bin/activate
# install [dev-]dependencies and build
pip install -e '.[dev]'
# checks
mypy bf
ruff check
```
