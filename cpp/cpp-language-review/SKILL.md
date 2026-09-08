---
name: cpp-language-review
description: Review non-trivial C++ source changes for modern language idioms, ownership, RAII, type safety, and Qt-compatible lifetime rules. Use after implementation or before merging. Read-only.
compatibility: Codex CLI, C++17/20/23, Qt 6, CMake
metadata:
  author: custom
  version: "1.0"
---

# C++ Language Review

Review the language-level implementation of changed C++ files. Do not edit code.

## Review process

1. Read the diff and inspect surrounding declarations and call sites.
2. Confirm the project style before judging naming or formatting; do not impose a different convention.
3. For each finding, cite the file/line, explain the concrete failure mode, and propose a minimal mitigation.
4. Keep severity and confidence explicit. Do not report taste-only issues as defects.

## Ownership and lifetime

- Prefer ownership shown by the declaration: `std::unique_ptr` for exclusive owning resources, `std::shared_ptr` only for genuinely shared lifetimes, and `std::weak_ptr` to break cycles.
- Prefer stack, member, container, value semantic, or `unique_ptr` storage over raw owning pointers.
- A non-owning pointer/reference may be acceptable for views, optional lookups, interoperability, or performance-sensitive iteration, but its lifetime must be visible at the use site.
- In Qt/C++ boundary code, do not replace QObject parent-child ownership with smart pointers unless a transfer-of-ownership comment or API contract proves that is intended.
- Do not use `delete`/`deleteLater` from another thread. Prefer parent destruction, queued deletion, worker shutdown semantics, or an explicitly synchronized cleanup path.

## RAII and resource safety

- Represent lock, transaction, handle, file, socket, and memory scopes with RAII objects instead of paired acquire/release calls.
- Check exception and early-return paths when resources are acquired manually.
- Avoid implicit conversion between incompatible resource types and avoid two mechanisms owning the same resource.
- Return local values by move construction by default; apply `std::move` only where it actually transfers ownership or avoids a proven copy.

## Modern type safety

- Use `enum class`, scoped constants, `std::array`, containers, spans/views, `std::optional`, and narrow casts deliberately.
- Replace unchecked integer assumptions and C-style casts on modified lines when this is behavior-preserving.
- Ensure signedness, narrowing, overflow, truncation, and unit changes are intentional and locally obvious.
- Preserve API compatibility when public headers are involved; prefer private implementation detail over broad ABI churn.

## Concurrency and side effects

- Verify thread affinity of QObjects, network replies, timers, UI properties, and file/image work.
- Check that mutexes protect all accesses to shared state, but do not require redundant locking around immutable or single-affinity data.
- Keep signal emission outside mutex-protected regions unless an exact reentrancy model explains why direct emission cannot reenter the same lock.
- Validate long-running work stays off UI-critical paths and shutdown does not leak callbacks into destroyed owners.

## Review output

For each finding:

- Severity: Critical / High / Medium / Low / Info
- Confidence: 0-100
- File/line
- Failure mechanism
- Evidence from the diff or adjacent code
- Recommended mitigation
- Suggested focused test where applicable

Finish with:

- Top fixes in priority order
- Platform-specific risks (MSVC, MinGW, Linux/macOS if relevant)
- Whether follow-up refactor/performance/test reviews are recommended

## Boundaries

- This skill reviews language-level quality only and must not modify source files.
- Defer dependency architecture to `cpp-architecture-review`.
- Defer build/target issues to `cmake-architecture-review`.
- Defer runtime profiling evidence to `cpp-performance-review`.
- Defer post-refactor regression scope to `cpp-refactor-review`.
- Defer coverage architecture to `cpp-test-review`.
