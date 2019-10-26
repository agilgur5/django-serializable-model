# Tasks

## Prerequisites

1. `node.js` and `npm` (task runner and some tasks make use of JS ecosystem)
1. `npm i -g maid` or just run with `npx maid`

## Directions

To run any of the tasks listed below (the headers), run `maid <task>`.
You can also see a list of the tasks and their descriptions with `maid help`.

## install

Install dependencies with `poetry`

```bash
poetry install;
```

## test

Runs tests with `pytest-django` and outputs coverage

```bash
poetry run pytest tests/test_project/;
```

## clean:dist

Cleans distribution directories

```bash
rm -rf build/ dist/ *.egg-info;
```

## build:dist

Builds a source distribution and binary wheel

We use `setup.py` for releases as `poetry` does not yet fully support all the configuration we make use of.

```bash
python setup.py sdist bdist_wheel;
```

## __release:test

Uploads a release to test PyPI.
Internal use only (see `publish:test` for external usage).

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*;
```

## __release:prod

Uploads a release to production PyPI.
Internal use only (see `publish:prod` for external usage).

```bash
twine upload dist/*;
```

## publish:test

`clean:dist` -> `build:dist` -> `__release:test`

Run tasks `clean:dist`, `build:dist`, `__release:test`

## publish:prod

`clean:dist` -> `build:dist` -> `__release:prod`

Run tasks `clean:dist`, `build:dist`, `__release:prod`

## changelog

Creates a changelog from the current tag to the previous tag

```bash
# changelog-maker only gets name from package.json, so do a replace
npx @agilgur5/changelog-maker | sed 's_nodejs/node_agilgur5/django-serializable-model_';
```

## Further Reading

- [Maid Docs](https://github.com/egoist/maid)
