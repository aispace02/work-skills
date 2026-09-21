---
name: frontend-web-performance
description: Use this skill for any request to make a page, site, or frontend asset load or feel faster — Core Web Vitals (LCP, INP, CLS, TTFB), render-blocking CSS and JavaScript, oversized bundles, unoptimized images and video, web font loading, layout instability, and main-thread congestion. Trigger on that intent however it is worded — optimizing or speeding up a site, making it snappier or lighter, improving performance, reducing bundle or asset size, fixing lag, jank or stutter, slow or blank first paint, content jumping as the page loads, poor Lighthouse or PageSpeed scores, font flashes, slow third-party scripts, or work on code splitting, lazy loading, resource hints, or Web Workers — even if the user never says "performance". Also use when reviewing frontend or build code for loading and delivery problems. Scope is what ships to the browser — not database or query tuning, backend throughput, build and test-suite runtime, or algorithmic complexity, unless the fix lands in delivered frontend assets.
license: MIT
metadata:
  author: Marc Ragnar Sebastiaan Hoekstra
  version: 1.0.0
---

# Frontend Web Performance

## How to approach the work

The techniques in this skill are not equally valuable, and which ones matter depends
entirely on what is actually slow. A page can satisfy thirty rules and still feel broken
because of one 1.4 MB hero image. Applying advice top-to-bottom is how a day gets spent
moving nothing.

1. **Find the bottleneck.** Identify which metric is bad and which specific resource or
   task causes it. Load `references/measure.md` when you have a report, a URL, or no idea
   where the cost is.
2. **Rank fixes by expected impact.** Lead with what moves the metric most, not what is
   easiest to describe.
3. **Fix, and explain the mechanism.** A fix the user understands is one they keep and
   generalize. A fix they cannot explain gets reverted at the next refactor.
4. **Say what to re-measure.** Every recommendation names its verification.

If you cannot tell what is slow from what the user gave you, ask for the specific thing you
need — a Lighthouse JSON, a network waterfall, built bundle sizes, the URL. Guessing at a
bottleneck and refactoring the wrong subsystem costs more than one clarifying question.

**Scope check.** "Optimize", "speed up", and "reduce size" also describe work that has
nothing to do with browser delivery. If the real subject is a database query, CI runtime,
an algorithm, or server throughput, say so plainly and answer on its own terms rather than
bending the problem toward frontend advice. The exception is a backend change that fixes a
frontend metric, which is common for TTFB.

## Triage

Read the reference for the symptom. Do not load all of them.

| Symptom | Read |
|---|---|
| Don't know what's slow; have a report or URL | `references/measure.md` |
| High TTFB, slow server response, slow repeat visits | `references/delivery.md` |
| Blank screen, slow first paint, poor LCP | `references/render-blocking.md`, then `references/delivery.md` |
| Huge bundle, slow parse, high TBT | `references/render-blocking.md` |
| Resource discovered too late; want preload/prefetch/prerender | `references/resource-hints.md` |
| Heavy page weight; LCP is an image | `references/images.md` |
| Video: encoding, autoplay, embeds, posters | `references/video.md` |
| Deferring offscreen content; heavy embeds | `references/lazy-loading.md` |
| Flash of unstyled/invisible text, slow font swap | `references/fonts.md` |
| Content jumps, poor CLS | `references/layout-stability.md` |
| Sluggish clicks, laggy typing, freezes, poor INP | `references/interactivity.md` |
| Slowed down after adding analytics, chat, embeds, ads | `references/third-party.md` |
| Vue 3 component tree re-renders, deep watchers, reactivity cost | Switch to `vue-performance` skill |

Targets at the 75th percentile of real users: **LCP** under 2.5 s, **INP** under 200 ms,
**CLS** under 0.1.

LCP decomposes into four subparts, and knowing which dominates points at the reference:
time to first byte (`references/delivery.md`), resource load delay (`references/render-blocking.md`, `references/resource-hints.md`), resource
load duration (`references/images.md`, `references/video.md`), element render delay (`references/render-blocking.md`, `references/interactivity.md`).

## What usually dominates

When you have no measurement and must guess an order to investigate, this is the usual
ranking by size of win on a typical content or commerce page:

1. Images — largest share of bytes, most common LCP element.
   Video embeds belong here too; a YouTube embed is heavier than most pages.
2. Third-party scripts — often the biggest main-thread cost, and the least owned.
3. Render-blocking CSS and synchronous JS in `<head>`.
4. First-party JavaScript payload.
5. TTFB and delivery configuration.
6. Fonts.

Say out loud that this is a prior, not a finding, and replace it with real data as soon as
there is any.

## Output format

Match the response to what was asked. Forcing every question into an audit template makes
the answer worse.

**Auditing code, a URL, or a report** — findings ordered by expected impact, each naming
the metric affected, the mechanism, and the fix. Then corrected code. Then anything needing
infrastructure or product decisions rather than a code change. Say explicitly if the
dominant problem is something you cannot see from what was shared.

**Implementing or configuring** — the code, the reasoning behind non-obvious choices, and
what to measure afterward.

**Explaining or advising** — just answer the question well. No violations list.

**Support status.** Where a technique's availability matters, name its Baseline status —
Widely available, Newly available, or Limited availability — rather than asserting it works.
Treat any status written in these references as possibly stale and worth re-checking; the
pattern each reference describes is durable, the support figures are not. A Limited
availability feature belongs in a response as progressive enhancement layered over something
Widely available, never as the load-bearing fix.

Always be honest about magnitude. "This saves maybe 20 ms; your real problem is the hero
image" is worth more than a list of equal-looking bullets.

When the user needs to justify the work to someone else, connect the metric to the outcome
it drives — retention, bounce rate, conversion — rather than reporting the metric alone. A
stakeholder does not act on "LCP is 4.1 s"; they act on what that costs.

## Traps

These apply regardless of which reference you loaded. Things that look like optimizations
and often are not:

* **Preloading everything.** Priority is relative. Marking many resources high-priority
  flattens the ordering the browser already computed and delays the one that mattered.
* **Lazy-loading above the fold.** Directly regresses LCP.
* **Inlining all CSS.** Trades a cacheable parallel request for a bigger, uncacheable HTML
  document on every navigation.
* **Score chasing.** Optimizing a Lighthouse number while field CLS or INP stays bad is
  optimizing for a simulated user.
* **Micro-optimizing.** Tree-shaking 8 KB while a 900 KB PNG sits above the fold.
* **Workers for cheap work.** `postMessage` structured-clones its payload; shuttling a
  large object to do small work is a net loss.
* **`will-change` everywhere.** Promotes elements to their own layers and consumes GPU
  memory; applied broadly it slows things down.
* **Long-caching personalized HTML.** A correctness and privacy bug, not a performance win.
* **Trusting framework defaults.** Hydration strategy and router prefetching are frequent
  INP and bandwidth problems worth checking explicitly.
* **Splitting more and more.** Chunk size is a balance, not a direction — see
  `references/render-blocking.md`.

## References

| File | Load when |
|---|---|
| `references/measure.md` | Diagnosing, or choosing what to verify afterward |
| `references/delivery.md` | Server response, compression, CDN, caching, repeat visits, bfcache |
| `references/render-blocking.md` | Critical path, CSS/JS blocking, code splitting, streaming compilation |
| `references/resource-hints.md` | preconnect, preload, fetchpriority, prefetch, Speculation Rules |
| `references/images.md` | Formats, sizing, srcset/sizes, picture, compression |
| `references/video.md` | Codecs, sources, poster, autoplay, video embeds |
| `references/lazy-loading.md` | loading=lazy and facades |
| `references/fonts.md` | Web font loading and swap behaviour |
| `references/layout-stability.md` | Layout shift and CLS |
| `references/interactivity.md` | INP, long tasks, event handlers, Web Workers |
| `references/third-party.md` | Analytics, chat, embeds, ads, tag managers |

References cross-link where a fix spans two of them. Follow those links rather than
guessing at the neighbouring detail.
