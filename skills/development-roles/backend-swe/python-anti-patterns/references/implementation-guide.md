# Python Anti-Patterns Checklist - Implementation Guide & Code Recipes

## Architecture Anti-Patterns

### Exposed Internal Types

```python
# BAD: Leaking ORM model to API
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:  # SQLAlchemy model
    return db.query(UserModel).get(id)
```

**Fix:** Use DTOs/response models.

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.from_orm(user)
```

### Mixed I/O and Business Logic

```python
# BAD: SQL embedded in business logic
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    # Business logic mixed with data access
    if len(orders) > 10:
        return 0.15
    return 0.0
```

**Fix:** Repository pattern. Keep business logic pure.

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    # Pure business logic, easily testable
    if len(orders) > 10:
        return 0.15
    return 0.0
```

## Error Handling Anti-Patterns

### Bare Exception Handling

```python
# BAD: Swallowing all exceptions
try:
    process()
except Exception:
    pass  # Silent failure - bugs hidden forever
```

**Fix:** Catch specific exceptions. Log or handle appropriately.

```python
# GOOD
try:
    process()
except ConnectionError as e:
    logger.warning("Connection failed, will retry", error=str(e))
    raise
except ValueError as e:
    logger.error("Invalid input", error=str(e))
    raise BadRequestError(str(e))
```

### Ignored Partial Failures

```python
# BAD: Stops on first error
def process_batch(items):
    results = []
    for item in items:
        result = process(item)  # Raises on error - batch aborted
        results.append(result)
    return results
```

**Fix:** Capture both successes and failures.

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

### Missing Input Validation

```python
# BAD: No validation
def create_user(data: dict):
    return User(**data)  # Crashes deep in code on bad input
```

**Fix:** Validate early at API boundaries.

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## Resource Anti-Patterns

### Unclosed Resources

```python
# BAD: File never closed
def read_file(path):
    f = open(path)
    return f.read()  # What if this raises?
```

**Fix:** Use context managers.

```python
# GOOD
def read_file(path):
    with open(path) as f:
        return f.read()
```

### Blocking in Async

```python
# BAD: Blocks the entire event loop
async def fetch_data():
    time.sleep(1)  # Blocks everything!
    response = requests.get(url)  # Also blocks!
```

**Fix:** Use async-native libraries.

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

## Type Safety Anti-Patterns

### Missing Type Hints

```python
# BAD: No types
def process(data):
    return data["value"] * 2
```

**Fix:** Annotate all public functions.

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### Untyped Collections

```python
# BAD: Generic list without type parameter
def get_users() -> list:
    ...
```

**Fix:** Use type parameters.

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## Testing Anti-Patterns

### Only Testing Happy Paths

```python
# BAD: Only tests success case
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

**Fix:** Test error conditions and edge cases.

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None

def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)

def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### Over-Mocking

```python
# BAD: Mocking everything
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
    # Test doesn't verify real behavior
```

**Fix:** Use integration tests for critical paths. Mock only external services.
