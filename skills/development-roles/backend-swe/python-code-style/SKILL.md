---
name: python-code-style
description: >-
  Python code style, linting, formatting, naming conventions, and documentation standards. Use when writing new code, reviewing style, configuring linters, writing docstrings, or establishing project standards.
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# Python Code Style & Documentation

Consistent code style and clear documentation make codebases maintainable and collaborative. This skill covers modern Python tooling, naming conventions, and documentation standards.

## When to Use This Skill

- Setting up linting and formatting for a new project
- Writing or reviewing docstrings
- Establishing team coding standards
- Configuring ruff, mypy, or pyright
- Reviewing code for style consistency
- Creating project documentation

## Core Concepts

### 1. Automated Formatting

Let tools handle formatting debates. Configure once, enforce automatically.

### 2. Consistent Naming

Follow PEP 8 conventions with meaningful, descriptive names.

### 3. Documentation as Code

Docstrings should be maintained alongside the code they describe.

### 4. Type Annotations

Modern Python code should include type hints for all public APIs.

## Quick Start

```bash
# Install modern tooling
pip install ruff mypy

# Configure in pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.mypy]
strict = true
```

## Fundamental Patterns

### Pattern 1: Modern Python Tooling

Use `ruff` as an all-in-one linter and formatter. It replaces flake8, isort, and black with a single fast tool.

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Run with:

```bash
ruff check --fix .  # Lint and auto-fix
ruff format .       # Format code
```

### Pattern 2: Type Checking Configuration

Configure strict type checking for production code.

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

Alternative: Use `pyright` for faster checking.

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
```

### Pattern 3: Naming Conventions

Follow PEP 8 with emphasis on clarity over brevity.

**Files and Modules:**

```python
# Good: Descriptive snake_case
user_repository.py
order_processing.py
http_client.py

# Avoid: Abbreviations
usr_repo.py
ord_proc.py
http_cli.py
```

**Classes and Functions:**

```python
# Classes: PascalCase
class UserRepository:
    pass

class HTTPClientFactory:  # Acronyms stay uppercase
    pass

# Functions and variables: snake_case
def get_user_by_email(email: str) -> User | None:
    retry_count = 3
    max_connections = 100
```

**Constants:**

```python
# Module-level constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
```

### Pattern 4: Import Organization

Group imports in a consistent order: standard library, third-party, local.

```python
# Standard library
import os
from collections.abc import Callable
from typing import Any

# Third-party packages
import httpx
from pydantic import BaseModel
from sqlalchemy import Column

# Local imports
from myproject.models import User
from myproject.services import UserService
```

Use absolute imports exclusively:

```python
# Preferred
from myproject.utils import retry_decorator

# Avoid relative imports
from ..utils import retry_decorator
```

## Best Practices Summary

1. **Use ruff** - Single tool for linting and formatting
2. **Enable strict mypy** - Catch type errors before runtime
3. **120 character lines** - Modern standard for readability
4. **Descriptive names** - Clarity over brevity
5. **Absolute imports** - More maintainable than relative
6. **Google-style docstrings** - Consistent, readable documentation
7. **Document public APIs** - Every public function needs a docstring
8. **Keep docs updated** - Treat documentation as code
9. **Automate in CI** - Run linters on every commit
10. **Target Python 3.10+** - For new projects, Python 3.12+ is recommended for modern language features


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

