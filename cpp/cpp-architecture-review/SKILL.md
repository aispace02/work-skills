---
name: cpp-architecture-review
description: Review the architecture of C++/CMake/Qt projects for dependency direction, module boundaries, coupling, ownership, threading, API leakage, and testability. Use for architecture audits or before major refactors. Read-only.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++/Qt Architecture Review

Read-only. Do not edit code.

## Review dimensions

### Module boundaries

- Are responsibilities coherent?
- Are dependencies directional and acyclic?
- Is UI dependent on application/domain layers rather than the reverse?
- Are infrastructure details leaking into domain code?

### CMake architecture

- Target graph and cycles
- PUBLIC/PRIVATE/INTERFACE leakage
- Header/include exposure
- Qt module propagation
- Generated code and AUTOGEN assumptions
- Plugin boundaries
- Test target isolation

### C++ boundaries

- Stable public headers vs implementation details
- Forward declarations and include hygiene
- Ownership contracts
- Interface/implementation separation
- ABI/API exposure where relevant

### Qt architecture

- QObject parent/child ownership
- Signal/slot coupling
- QObject affinity
- UI/business separation
- Model/view boundaries
- Singleton/global QObject usage
- C++/QML boundary if QML exists

### Maintainability

- God classes
- cyclic abstractions
- service locator / hidden globals
- excessive central managers
- duplicated policy
- poor test seams

## Method

First build a dependency map. Then trace the 5–10 most central targets/classes. Validate suspected problems with symbol references and call sites.

For each finding report:

- Severity: Critical/High/Medium/Low
- Confidence: 0–100
- Evidence: files/symbols
- Why it matters
- Lowest-risk improvement
- What NOT to change

Do not propose a rewrite unless the evidence shows incremental refactoring is insufficient.

## Final output

1. Architecture overview
2. Dependency direction assessment
3. Module-boundary findings
4. CMake findings
5. Qt ownership/threading findings
6. Testability findings
7. Top 10 risks
8. Incremental refactoring roadmap
