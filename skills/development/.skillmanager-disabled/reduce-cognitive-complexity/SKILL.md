---
name: reduce-cognitive-complexity
description: Refactor functions and methods to reduce cognitive complexity — the mental effort it takes to read and follow a piece of code's control flow. Use this skill whenever refactoring code for readability, responding to a linter or code-review flag about complexity or nesting, breaking apart a function that has accumulated too many branches or loops, or when the user describes code as hard to follow, too nested, or spaghetti, or asks to clean up, simplify, or refactor a function. Covers extracting complex conditions into named functions, breaking large functions down by responsibility, replacing deep nesting with early returns, and replacing long branch chains with lookup tables.
---

# Reduce Cognitive Complexity

Cognitive complexity measures how hard code is to read and hold in your head — not how much code there is, but how many times a reader has to track a new branch, remember a condition they're still inside, or untangle mixed logic. It's the idea behind SonarSource's Cognitive Complexity metric and similar linter rules (e.g. `sonarjs/cognitive-complexity` for ESLint), which many teams wire into their code-review gates.

It was designed as a response to cyclomatic complexity, which counts every branch equally regardless of how deep it's nested. Cognitive complexity instead penalizes nesting on top of the branch itself, so a condition three levels deep costs more than the same condition at the top of a function — which tracks much closer to what a reader actually experiences as "this function is a mess."

## Before you refactor

Refactoring changes structure, not behavior. If nothing covers the function under test, write a test first, or flag that as a gap before proceeding — without one, there's no way to confirm the restructuring didn't quietly change what the code does.

Then find the actual hotspot: usually the deepest nesting, the longest condition, or the function juggling the most distinct responsibilities. Fix that first — taking one bad spot to zero is worth more than shaving a point off five mediocre ones.

The four techniques below are ordered roughly by how often they apply. Use the smallest one that fixes the problem: a function chopped into many tiny, oddly-named pieces can be just as hard to follow as the nested version it replaced (see Pitfalls).

## 1. Extract a complex condition into a named function

A condition that mixes `and`/`or`, or bundles several unrelated checks, costs a reader twice — they have to parse the boolean logic *and* figure out what it means. Naming it does both jobs at once: the name documents the meaning, and the call site reads like a sentence.

### Noncompliant

```python
def process_eligible_users(users):
    for user in users:              # +1 (for)
        if ((user.is_active and     # +1 (if) +1 (nested) +1 (multiple conditions)
             user.has_profile) or   # +1 (mixed operator)
            user.age > 18):
            user.process()
```

### Compliant

```python
def process_eligible_users(users):
    for user in users:              # +1 (for)
        if is_eligible_user(user):  # +1 (if) +1 (nested)
            user.process()

def is_eligible_user(user):
    return (user.is_active and user.has_profile) or user.age > 18  # +1 (multiple conditions) +1 (mixed operators)
```

The total complexity of the program hasn't changed — it moved into `is_eligible_user`, where it's cheaper because it isn't nested inside a loop. `process_eligible_users` now reads at a glance, and the extracted predicate can be tested and reasoned about on its own. If the condition is only used once and a full function feels like overkill, a well-named local variable (`is_eligible = (...)`) buys most of the same clarity for less ceremony.

## 2. Break a large function into smaller ones by responsibility

A function that branches on more than one thing at once (active/inactive *and* has-profile/no-profile) forces the reader to hold every combination in their head simultaneously. Splitting on the first branch turns one function with a complexity of 8 into four small ones, none of which nest more than one level.

### Noncompliant

```python
def process_user(user):
    if user.is_active():             # +1 (if)
        if user.has_profile():       # +1 (if) +1 (nested)
            ...  # process active user with profile
        else:                        # +1 (else)
            ...  # process active user without profile
    else:                            # +1 (else)
        if user.has_profile():       # +1 (if) +1 (nested)
            ...  # process inactive user with profile
        else:                        # +1 (else)
            ...  # process inactive user without profile
```

### Compliant

```python
def process_user(user):
    if user.is_active():             # +1 (if)
        process_active_user(user)
    else:                            # +1 (else)
        process_inactive_user(user)

def process_active_user(user):
    if user.has_profile():           # +1 (if) +1 (nested)
        ...  # process active user with profile
    else:                            # +1 (else)
        ...  # process active user without profile

def process_inactive_user(user):
    if user.has_profile():           # +1 (if) +1 (nested)
        ...  # process inactive user with profile
    else:                            # +1 (else)
        ...  # process inactive user without profile
```

`process_user` now has a complexity of 2 and reads as a table of contents; each helper is small enough to verify by inspection, and the split usually lines up with how the tests want to be organized too.

## 3. Return early instead of nesting

Every `if` that wraps the rest of a function adds a level the reader has to keep in mind for everything below it — including the parts that have nothing to do with that condition. Handling the exceptional case first and returning removes that tax for the remainder of the function.

### Noncompliant

```python
def calculate(data):
    if data is not None:    # +1 (if)
        total = 0
        for item in data:   # +1 (for) +1 (nested)
            if item > 0:    # +1 (if) +2 (nested)
                total += item * 2
        return total
```

### Compliant

```python
def calculate(data):
    if data is None:        # +1 (if)
        return None
    total = 0
    for item in data:       # +1 (for)
        if item > 0:        # +1 (if) +1 (nested)
            total += item * 2
    return total
```

The logic is identical, but nothing after the guard clause is nested inside a condition the reader has to keep carrying.

## 4. Replace long branch chains with a lookup table

A long `if`/`elif` chain that maps an input to a result adds a point for every branch, and a reader has to scan the whole thing to find the one they care about. When each branch is just "for this input, return or call that," a dictionary (or a `match` statement) says the same thing without the accumulating cost.

### Noncompliant

```python
def shipping_cost(method):
    if method == "standard":      # +1 (if)
        return 5.00
    elif method == "express":     # +1 (elif)
        return 12.00
    elif method == "overnight":   # +1 (elif)
        return 25.00
    else:                         # +1 (else)
        raise ValueError(f"Unknown method: {method}")
```

### Compliant

```python
SHIPPING_COSTS = {
    "standard": 5.00,
    "express": 12.00,
    "overnight": 25.00,
}

def shipping_cost(method):
    if method not in SHIPPING_COSTS:  # +1 (if)
        raise ValueError(f"Unknown method: {method}")
    return SHIPPING_COSTS[method]
```

This pays off when branches are simple lookups or dispatches. If each branch runs meaningfully different logic rather than returning a different value or calling a different function, forcing it into a dict usually makes it harder to follow, not easier — reach for technique 2 instead.

## Language note

The metric and the techniques above are language-agnostic — cognitive complexity is computed the same way in Python, JavaScript/TypeScript, Java, Go, and elsewhere. The examples use Python for clarity, but the same moves translate directly: guard clauses, extracted predicates, decomposed handlers, and dictionary dispatch (or a `switch`/`match` where the language has one).

## Pitfalls

- **No tests, no refactor.** Restructuring without a test covering current behavior is a rewrite wearing a refactor's clothes.
- **Over-extraction.** Five three-line helpers that are each called exactly once don't reduce complexity, they relocate it and add an indirection tax on top. Extract when the piece has a name clearer than its body, not by default.
- **Don't chase the score.** The number is a proxy for "will a human find this confusing," not the goal itself. A function that scores well but reads awkwardly — an extracted predicate with a vaguer name than the inline condition it replaced, say — isn't an improvement.
