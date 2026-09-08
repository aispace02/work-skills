# C++/Qt Codex Skills Pack

A focused Codex CLI skills pack for C++ / CMake / Qt 6 projects.

## Included skills

- `cpp-codebase-analysis` — read-only codebase reconnaissance
- `cpp-language-review` — language-level idioms, ownership/RAII, and type-safety review
- `cpp-architecture-review` — architecture/dependency/Qt boundary review
- `cpp-reverse-engineering` — unfamiliar/legacy project reverse engineering
- `cmake-architecture-review` — target/dependency/build-system audit
- `cpp-refactor-review` — post-refactor regression review
- `cpp-performance-review` — evidence-driven performance audit
- `cpp-test-review` — test architecture and coverage review

## Install

Copy the whole pack into a project:

```bash
cp -r cpp-qt-codex-skills-pack/* .agents/skills/
```

Or install globally:

```bash
cp -r cpp-qt-codex-skills-pack/* ~/.codex/skills/
```

If your Codex version uses another discovery path, `~/.agents/skills/` is also a supported fallback.

Restart Codex after installation.

## Suggested workflow

For a new project:

```text
$cpp-codebase-analysis
$cpp-architecture-review
$cmake-architecture-review
```

Before a major refactor:

```text
$cpp-codebase-analysis
$cpp-architecture-review
```

After implementation:

```text
$cpp-refactor-review
$cpp-test-review
```

For non-trivial C++ source changes, run this before the post-refactor checks:

```text
$cpp-language-review
```

For performance work:

```text
$cpp-performance-review
```

## Qt official skills

This pack intentionally complements rather than duplicates Qt's official skills. Recommended companion skills:

- `qt-cpp-review`
- `qt-cmake-project`
- `qt-cpp-docs`
- QML skills when the project uses QML

Official repository:
https://github.com/TheQtCompanyRnD/agent-skills

The official Qt repository currently documents Codex CLI support and the `SKILL.md` directory format.

## Notes

These custom skills are deliberately read-only for analysis/review tasks. They are designed to make an agent gather evidence before proposing changes.

For build verification, let Codex use the project's existing CMake presets and build/test commands rather than hard-coding a generator or build directory.
