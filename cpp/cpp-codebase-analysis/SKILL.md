---
name: cpp-codebase-analysis
description: Analyze a C++/CMake/Qt codebase before modification. Use when the user asks to understand an unfamiliar project, map modules, dependencies, startup flow, ownership, threading, or technical debt. Read-only and evidence-driven.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++ Codebase Analysis

Perform a read-only reconnaissance of the repository. Do not modify source files.

## Workflow

1. Identify build entry points: `CMakeLists.txt`, presets, toolchain files, CI, tests.
2. Inventory targets and map `add_library`, `add_executable`, `qt_add_*`, plugins and tests.
3. Trace `target_link_libraries` and classify PUBLIC/PRIVATE/INTERFACE dependencies.
4. Identify application entry points (`main`, startup services, dependency injection/bootstrap).
5. Map major modules and their responsibilities from symbols and call sites, not filenames alone.
6. Trace important QObject ownership and lifetime paths.
7. Identify threads, event loops, queued/direct connections, and cross-thread state.
8. Identify global state, singleton/service-locator patterns, and hidden dependencies.
9. Identify public API boundaries and include/dependency hotspots.
10. Inspect tests and build/CI coverage.
11. Rank architectural risks by evidence and impact.

## Evidence rules

- Prefer repository evidence over assumptions.
- Cite concrete files, symbols, and line ranges.
- Distinguish confirmed facts from hypotheses.
- Do not recommend refactoring merely because a pattern is unfamiliar.
- Never modify files.

## Output

Produce:

- Executive summary
- Build/target map
- Module/dependency map
- Startup flow
- Ownership/lifetime model
- Threading model
- Communication model (signals/slots/callbacks)
- Test/build coverage
- Architecture risks
- Technical-debt hotspots
- Suggested investigation order

For large repositories, use targeted searches and sample representative modules rather than pretending every line was exhaustively inspected.
