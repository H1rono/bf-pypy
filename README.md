# bf-pypy

https://pypy.org/posts/2011/04/tutorial-writing-interpreter-with-pypy-3785910476193156295.html

## Development

requires: [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers)

```bash
# within devcontainer:
./scripts/setup.sh
```

run rpython translation:

```bash
./scripts/translate.sh translate/run.py
# or
./scripts/translate.sh --opt=jit translate/run.py
```

execute translation output:

```bash
./translate/run-c
```
