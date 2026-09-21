# ⏱ Frontend Web Performance <sub><sup>for AI & LLMs</sup></sub> <picture><img alt="Markdown" src="https://img.shields.io/badge/Markdown-083fa1"></picture> <picture><img alt="AI" src="https://img.shields.io/badge/AI-9635db"></picture>

An advanced AI/LLM skill orchestrator designed to meticulously diagnose and resolve frontend web performance bottlenecks, targeting Core Web Vitals and browser delivery efficiency.

## Index

* ✨ [Features](#-features)
* 🚀 [Usage](#-usage)
* 🏆 [Attribution](#-attribution)
* ❤ [Support](#-support)
* ⚖ [License](#-license)

## ✨ Features

* Diagnoses root causes from the evidence you supply — a Lighthouse report, network waterfall, or bundle sizes — decomposing Core Web Vitals (LCP, INP, CLS, TTFB) to locate the bottleneck instead of guessing at it.
* Condenses and prioritizes solutions based on measurable real-world impact rather than arbitrary scores.
* Routes each symptom through a triage table to the knowledge domain that fits it (render-blocking, lazy-loading, resource-hints, and more), loading only the reference the problem needs.
* Enforces an evidence-driven, diagnose-before-fixing architectural workflow.

## 🚀 Usage

This skill is designed to be triggered by natural language requests related to speeding up a site or improving frontend performance.

To get the most accurate optimizations, provide the skill with specific diagnostic data such as a URL, a Lighthouse JSON report, a network waterfall, or built bundle sizes.

> [!TIP]
> You do not need to explicitly say "performance" to trigger this skill. Simply asking to make a site "snappier," "lighter," or fixing "content jumping" is enough to engage the performance orchestrator.

### Example Prompts

* *Can you audit this frontend code to reduce my bundle size?*
* *How do I implement code splitting and lazy loading for this component?*
* *My Lighthouse score says I have slow third-party scripts and poor LCP. Here is the report.*
* *The page feels laggy when typing. Can you help fix the INP?*

### Scope Boundary

This skill is refined to only trigger on performance optimization requests that are targeting frontend tasks.

> [!IMPORTANT]
> This skill's scope is strictly limited to what ships to the browser. It will not assist with database query tuning, backend throughput, algorithmic complexity, or test-suite runtime unless those changes directly resolve a frontend delivery metric like TTFB.

## 🏆 Attribution

### Third-party content

#### Source and required attribution

The technical guidance in this skill draws substantially on the [**Learn Performance**](https://web.dev/learn/performance) course published on web.dev by Google.

> Portions of this page are modifications based on work created and [shared by Google](https://developers.google.com/readme/policies) and used according to terms described in the [Creative Commons 4.0 Attribution License](https://creativecommons.org/licenses/by/4.0/).

Code samples derived from this content are licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). Those portions remain under their own terms, which require that attribution be preserved.

#### Modifications

The material has been reorganised, rewritten, condensed, and extended for use as an agent skill. Any errors introduced in that process are the maintainer's, not Google's. This skill is not endorsed by or affiliated with Google, and no Google trademark or brand feature is licensed by the above.

### Independently authored content

#### Additional original topics

Two topics that are not covered by the Learn Performance course were created and added:

| Topic | Location |
|---|---|
| Cumulative Layout Shift | `layout-stability.md` |
| Third-party script auditing | `third-party.md` |

#### Original method and organisation

These parts were written from scratch rather than adapted from the course. Some are methods, some are written content, some are conventions — the Kind column says which:

| Element | Kind | Location |
|---|---|---|
| Diagnose-before-fixing workflow | Method | `SKILL.md` |
| Scope boundary | Definition of what is out of scope | `SKILL.md`, and the `description` frontmatter |
| Triage table | Navigation — symptom to reference | `SKILL.md` |
| "What usually dominates" ordering | Original judgement | `SKILL.md` |
| Baseline availability reporting | Convention | `SKILL.md`, applied in `lazy-loading.md` and `video.md` |
| Traps section | Original content | `SKILL.md` |
| Reconciliation of conflicting source modules | Editorial judgement | `lazy-loading.md`, `video.md` |

The reconciliation row covers `loading="lazy"` on `<video>`. The lazy-loading module (last updated 2023-11-01) and the video module (last updated 2026-04-02) contradict each other because the attribute arrived between the two revisions, and neither matches current support:

| Change | Why | Location |
|---|---|---|
| A JS lazy-loader is no longer presented as the only option. Replaced with a layered pattern: `preload="none"` does the work, `loading="lazy"` is added as enhancement, support is feature-detected | The source predates the attribute and states that deferring video is not a browser-level feature. A library is now only needed for autoplay-in-viewport where support is missing | `lazy-loading.md` |
| `loading="lazy"` labelled Baseline Limited availability and layered on top of `preload` rather than replacing it | The source introduces it without any support caveat. Browsers without support ignore the attribute and fall back to `preload` behaviour | `video.md` |
| For offscreen autoplay downloads, `loading="lazy"` is named as the intended fix but `poster` plus `IntersectionObserver` is kept as the reliable route | Support is still arriving, so a declarative-only recommendation would not work today | `video.md` |

#### Third-party topic expansion

The course covers the topics these belong to but not the features themselves. Some are documented elsewhere on web.dev or Chrome for Developers, which the modules link to for material outside their scope. The guidance here is original:

| Feature | Location |
|---|---|
| `103 Early Hints` | `delivery.md` |
| `content-visibility`, `contain-intrinsic-size` | `render-blocking.md`, `layout-stability.md` |
| `scheduler.yield()` | `interactivity.md` |
| Back/forward cache eligibility | `delivery.md` |
| `@font-face` metric overrides (`size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`) | `fonts.md`, `layout-stability.md` |
| Speculation Rules `eagerness` field — the course shows only `source: list`, and gets intent-based speculation from the Quicklink library instead | `resource-hints.md` |

## ❤ Support

If this project saved you some time, please consider giving it a ⭐ **Star** on GitHub; it helps others discover the repository!

If you would like to support my work further, please check out the **Sponsor this project** section on this repository page. Even a small contribution makes a big difference!

## ⚖ License

Distributed under the [MIT License](LICENSE.md).

> [!IMPORTANT]
> The license under which this skill is distributed covers the original authorship only. The third-party content above remains under its own terms, which require that attribution be preserved by anyone redistributing this skill. The MIT grant does not and cannot relicense it.
>
> Keep this file alongside `LICENSE.md`.

| License | Covers | Terms |
|---|---|---|
| MIT | Original authorship in this skill | [LICENSE.md](LICENSE.md) |
| CC-BY-4.0 | Third-party prose and technical guidance | <https://creativecommons.org/licenses/by/4.0/> |
| Apache-2.0 | Third-party code samples | <https://www.apache.org/licenses/LICENSE-2.0> |
