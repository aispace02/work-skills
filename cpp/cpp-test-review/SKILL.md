---
name: cpp-test-review
description: Review C++/Qt test coverage and test architecture. Use after changes, during refactors, or when assessing whether behavior, threading, QObject lifetimes, models, networking, and CMake targets are adequately tested. Read-only.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++/Qt Test Review

Do not edit tests unless the user explicitly asks for implementation.

## Inspect

- CTest registration
- Qt Test / QTest usage
- unit/integration boundaries
- fixtures and test data
- QObject lifetime tests
- signal/slot assertions
- model contract tests
- threading tests
- network failure tests
- persistence/error tests
- test isolation
- flaky timing constructs
- missing CMake test dependencies

## Priorities

Prefer deterministic tests. Avoid sleeps when signal spies, wait conditions, or explicit synchronization can be used.

Check whether tests validate observable behavior rather than implementation details.

## Output

- Coverage map by module
- Critical untested behaviors
- Flaky-test risks
- Missing regression tests
- Test architecture problems
- Prioritized test plan
