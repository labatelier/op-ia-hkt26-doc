# Changelog

Documentation changes proposed by the documentation agent, newest first.

This file is maintained automatically: an entry is prepended each time the agent
opens a pull request. The agent never reviews or rewrites it.

## 2026-09-28 16:01 UTC — run 8af84fac

Triggered by `push` on `main`, targeting `main`.

Add Google-style docstrings to every module, class and function of the shared toolbox and the npd/prd packages, which had none, and add a README covering prerequisites, installation, usage, structure and the HKT_* configuration.

- `README.md` — documentation: repository had no readme at all
- `scripts/count_lines.py` — docstrings: module and three helpers had no docstring
- `src/common/__init__.py` — docstrings: package re-exports were undocumented
- `src/common/clock.py` — docstrings: clock classes and methods had no docstrings
- `src/common/codes.py` — docstrings: code enums and retry helper were undocumented
- `src/common/config_base.py` — docstrings: settings reader and factory lacked docstrings
- `src/common/enums.py` — docstrings: shared enumerations had no docstrings
- `src/common/errors.py` — docstrings: error classes and accessors were undocumented
- `src/common/events.py` — docstrings: event enum had no docstring
- `src/common/identifiers.py` — docstrings: identifier types and generator lacked docstrings
- `src/common/logging_base.py` — docstrings: logger and sinks had no docstrings
- `src/common/money.py` — docstrings: money value object and helper were undocumented
- `src/common/result.py` — docstrings: result container and constructors lacked docstrings
- `src/common/text.py` — docstrings: text helpers had no docstrings
- `src/common/validation.py` — docstrings: validation rules and builders were undocumented
- `src/common/vocab.py` — docstrings: constant module had no docstring
- `src/npd/__init__.py` — docstrings: package had no docstring
- `src/npd/config/__init__.py` — docstrings: config package had no docstring
- `src/npd/config/settings.py` — docstrings: settings loader and defaults were undocumented
- `src/npd/domain/__init__.py` — docstrings: domain package had no docstring
- `src/npd/domain/account.py` — docstrings: account aggregate and its guards lacked docstrings
- `src/prd/__init__.py` — docstrings: package had no docstring
- `src/prd/config/__init__.py` — docstrings: config package had no docstring
- `src/prd/config/settings.py` — docstrings: settings loader and defaults were undocumented
