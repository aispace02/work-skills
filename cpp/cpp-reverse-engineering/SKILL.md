---
name: cpp-reverse-engineering
description: Reverse-engineer an unfamiliar C++/Qt application without modifying it. Use when the user needs startup flow, runtime architecture, object lifetimes, threading, communication paths, or a system-level understanding of legacy code.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++/Qt Reverse Engineering

Never edit source files.

## Questions to answer

1. What happens from process start to the first usable UI/service?
2. Which targets and modules are central?
3. What are the main runtime objects?
4. Who owns them and how long do they live?
5. Which threads/event loops exist?
6. Which objects cross thread boundaries?
7. How do modules communicate?
8. Where is state stored?
9. Which code paths handle I/O, persistence, networking, and errors?
10. Which classes are architectural bottlenecks?
11. Which parts are well tested?
12. Where is behavior surprising or implicit?

## Tracing strategy

Start with:
- CMake target graph
- `main`
- application/bootstrap classes
- major QObject constructors
- factories/singletons
- signal/slot connections
- worker threads
- persistence/network entry points

Trace both callers and callees for critical symbols.

## Output artifacts

Write the report in the response unless the user explicitly asks for files:
- Runtime startup sequence
- Static module graph
- Runtime communication graph
- Thread map
- Ownership/lifetime map
- State/data-flow map
- Risk map
- Glossary of important classes
- Recommended reading order for a new developer

Use confidence labels and cite concrete evidence.
