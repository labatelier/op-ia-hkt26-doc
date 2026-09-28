# hackaton-aws-bordeaux

Shared Python codebase for the `HKT` hackathon exercise. It holds a dependency-free
toolbox (`common`) and two environment packages, `npd` for non-production and `prd`
for production, that configure themselves from environment variables.

## Prerequisites

- Python 3.12 or newer (`requires-python = ">=3.12"`).
- No third-party runtime dependency: the project builds on the standard library only.
- `pytest` 8 or newer to run the tests, installed through the `test` extra.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

To also get the test tooling:

```bash
pip install -e ".[test]"
```

The build backend is `setuptools` (>= 68) and packages are discovered under `src`,
so an editable install is enough to import `common`, `npd` and `prd`.

## Usage

The packaging metadata declares two console entry points:

| Command   | Target          |
|-----------|-----------------|
| `hkt-npd` | `npd.main:main` |
| `hkt-prd` | `prd.main:main` |

Both packages re-export `main` and `build_application` from their `main` module,
which is not part of the repository yet; see *Known gaps* below.

Loading the configuration of an environment works without any entry point:

```python
from npd.config import load_settings

settings = load_settings()           # reads os.environ
settings = load_settings({})         # or any mapping, handy in tests
```

A helper script reports the number of non-empty Python lines per package:

```bash
python scripts/count_lines.py        # defaults to the current directory
python scripts/count_lines.py .      # or an explicit checkout root
```

Running the tests, once a `tests` directory exists:

```bash
pytest
```

`pyproject.toml` already sets `pythonpath = ["src"]` and `testpaths = ["tests"]`,
so `pytest` needs no extra flag.

## Project structure

```
pyproject.toml          Packaging, entry points and pytest configuration
scripts/
  count_lines.py        Counts non-empty Python lines per package
src/
  common/               Shared, dependency-free building blocks
    clock.py            Clock abstraction, system and fixed implementations
    codes.py            Numeric error and field codes
    config_base.py      Settings dataclass, environment reader, factory
    enums.py            Environment, Severity, Status, Outcome, Kind
    errors.py           DomainError and its specialisations
    events.py           Numeric log event identifiers
    identifiers.py      AccountId, TransactionId and their generator
    logging_base.py     Structured logger and its sinks
    money.py            Currency and Money value objects
    result.py           Result container with ok() and err()
    text.py             String primitives and punctuation constants
    validation.py       Composable validation rules
    vocab.py            Environment variable names, log field names, labels
  npd/
    config/settings.py  Non-production settings loader
    domain/account.py   Account aggregate and its immutable state
  prd/
    config/settings.py  Production settings loader
```

## Configuration

Every setting is optional and read from the process environment, with the
defaults below.

| Variable       | Meaning                          | Default                        |
|----------------|----------------------------------|--------------------------------|
| `HKT_ENDPOINT` | Base URL of the backend          | `common.vocab.LOCAL_ENDPOINT`  |
| `HKT_REGION`   | Region of the backend            | `common.vocab.REGION_DEFAULT`  |
| `HKT_TIMEOUT`  | Per-call timeout in seconds      | `5`                            |
| `HKT_RETRIES`  | Retries after a failed call      | `1`                            |
| `HKT_STRICT`   | Strict mode flag                 | `false`                        |

Boolean values accept `1`, `true`, `yes` and `on`, case-insensitively; anything
else is false. A non-integer `HKT_TIMEOUT` or `HKT_RETRIES` raises a
`common.errors.ConfigError` carrying the `BAD_CONFIG` code and the offending key.

Two further names exist in `common.vocab`, `HKT_ENV` and `HKT_LEVEL`, but no
loader reads them yet: the environment is hardcoded per package and the log
threshold is the module-level `DEFAULT_THRESHOLD` (`Severity.DEBUG`).

## Known gaps

The repository is a work in progress and a few modules referenced by the code are
still missing:

- `npd.main` and `prd.main`, imported by the two package `__init__.py` files and
  targeted by the `hkt-npd` and `hkt-prd` entry points.
- `npd.domain.transaction`, `npd.domain.ledger` and `npd.domain.policy`, imported
  by `npd/domain/__init__.py`.
- The `tests` directory configured in `pyproject.toml`.

Until they land, importing `npd` or `prd` directly fails; import the submodules,
for instance `npd.config.settings`, instead.
