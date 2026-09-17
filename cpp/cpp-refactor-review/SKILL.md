---
name: cpp-refactor-review
description: Review a C++/Qt refactor for regressions in behavior, architecture, ownership, threading, API compatibility, CMake dependencies, and tests. Use after implementation or before merging. Read-only.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++/Qt Refactor Review

Review the diff and surrounding code. Do not edit.

## Required checks

### Behavioral

- changed control flow
- error paths
- signal emission
- ordering and reentrancy
- persistence/network semantics

### Ownership

- parent changes
- raw pointer ownership
- smart-pointer transitions
- QObject lifetime
- delete/deleteLater behavior

### Threading

- affinity changes
- queued/direct connection changes
- shared state synchronization
- worker shutdown

### Architecture

- new coupling
- dependency direction
- abstraction leakage
- singleton/global-state growth
- CMake target dependency changes

### API

- source compatibility
- binary compatibility when relevant
- constness
- overload ambiguity
- public-header changes

### Tests

- existing tests affected
- missing regression tests
- build variants not covered

## Review process

1. Inspect git diff and status.
2. Trace changed symbols to callers/callees.
3. Compare old/new dependency relationships.
4. Run existing focused tests/build checks when appropriate.
5. Report only evidence-backed findings.

## Output

For each finding:

- Severity
- Confidence
- File/line
- Regression mechanism
- Evidence
- Recommended mitigation
- Suggested regression test

Finish with:

- Architecture regression: Yes/No
- Behavioral regression risk: Low/Medium/High
- Missing tests
- Merge recommendation
