---
name: cpp-performance-review
description: Analyze performance risks in C++/Qt applications, including allocations, copies, Qt implicit sharing, hot loops, model/view updates, I/O, locking, and event-loop behavior. Use for performance audits or suspected regressions. Read-only.
compatibility: Codex CLI, C++17/20/23, CMake, Qt 6
metadata:
  author: custom
  version: "1.0"
---

# C++/Qt Performance Review

Do not optimize blindly. Establish likely hot paths from call frequency, loops, startup paths, UI update paths, or user-provided profiling evidence.

## Inspect

- allocation/copy patterns
- Qt implicit sharing detach
- container access
- repeated conversions
- regular expressions
- model/view updates
- signal storms
- event-loop blocking
- synchronous I/O
- lock contention
- thread oversubscription
- repeated filesystem/network operations
- unnecessary serialization/deserialization

## Evidence hierarchy

1. Profiling data
2. Repeated execution in hot loops
3. Complexity analysis
4. Allocation/copy reasoning
5. General code smell

Never label a micro-optimization as important without evidence.

## Output

- Suspected hotspots
- Complexity
- Allocation/copy risks
- Qt-specific costs
- UI/event-loop risks
- Thread/lock risks
- Measurement plan
- Safe optimizations
- Optimizations that require profiling first
