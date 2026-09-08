---
name: cmake-architecture-review
description: Audit CMake architecture in C++/Qt projects. Use when diagnosing dependency leakage, target organization, build complexity, Qt AUTOGEN, installation/export issues, or slow/inconsistent builds. Read-only.
compatibility: Codex CLI, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# CMake Architecture Review

Do not edit files.

## Inspect

- Top-level CMakeLists
- subdirectories
- CMakePresets.json
- toolchain files
- package discovery
- target declarations
- target_link_libraries
- target_include_directories
- target_compile_definitions/options/features
- generated sources
- Qt AUTOUIC/AUTOMOC/AUTORCC
- Qt6 `qt_add_*` APIs
- plugins
- install/export/package rules
- tests and test registration
- CI configure/build commands

## Rules

1. Prefer target-based configuration.
2. Check PUBLIC/PRIVATE/INTERFACE propagation.
3. Detect dependency cycles.
4. Detect directory-scope variables hiding target dependencies.
5. Detect unnecessary global include paths/definitions/options.
6. Detect Qt modules leaking through public interfaces unnecessarily.
7. Check consistency of Debug/Release and preset behavior.
8. Check reproducibility and package discovery.
9. Flag legacy qmake/Qt5 CMake idioms when the project is Qt6.
10. Do not recommend changes solely for stylistic preference.

## Output

- Target graph
- Dependency leaks
- Build-system risks
- Qt-specific issues
- Test/build isolation issues
- Installation/export issues
- Prioritized fixes with exact targets/files
