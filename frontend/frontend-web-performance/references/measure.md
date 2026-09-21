# Measuring and verifying

Match the measurement to the claim. A recommendation without a verification step is a guess
the user cannot check.

## Lab vs field

**Lab** — Lighthouse, PageSpeed Insights, WebPageTest, the DevTools Performance panel. Use
for reproducing a specific bottleneck and confirming a fix. Lab INP is not measurable, since
there is no real interaction; **Total Blocking Time is the lab proxy**, and it correlates
well with field INP.

**Field** — CrUX, or RUM collected with the `web-vitals` library. This is the source of
truth. A Lighthouse score is one synthetic run on a simulated device; real users have
different hardware, networks, and interaction patterns, and only field data reflects them.
When lab and field disagree, field wins.

## Finding the cost

* **Lighthouse JS execution audit** reports time spent per script. It warns past 2 s and
  fails past 3.5 s. This is how you pick code-splitting candidates instead of guessing.
* **DevTools Coverage tool** shows which parts of those scripts and stylesheets go unused
  during load — the input for removing dead CSS and deferring unused JS.
* **Network waterfall** exposes request chains, late discovery, and redirects. Serial
  dependencies show up here and nowhere else. WebPageTest marks blocking resources with an
  orange circle and draws the start-of-render line, so you can see exactly what delayed it.
* **Lighthouse render-blocking audit** flags a resource only when it actually delayed
  rendering, so it produces fewer false positives than a waterfall — useful once you have
  already trimmed the obvious blockers.
* **Lighthouse critical request chains** audit shows resources nested under other resources
  plus total chain latency. Note it lists everything loaded at high priority, including web
  fonts, so not every entry is genuinely render-blocking.
* **Performance panel long-task view** attributes main-thread blocking to specific
  functions, which is where INP work starts.
* **`Server-Timing` headers** attribute TTFB to backend phases in the field, rather than
  leaving it as one opaque number. See `delivery.md`.

## LCP subparts

Decompose before fixing. The four parts point at different references:

| Subpart | Meaning | Read |
|---|---|---|
| Time to first byte | Server and network before any HTML | `delivery.md` |
| Resource load delay | Gap between HTML arriving and the LCP resource being discovered | `render-blocking.md` |
| Resource load duration | Downloading the LCP resource itself | `images.md`, `video.md` |
| Element render delay | Resource is present but not yet painted | `render-blocking.md`, `interactivity.md` |

A large resource load delay almost always means late discovery — the preload scanner never
saw the resource, usually because JavaScript created it or CSS hid it in an `@import`.

## What to ask for

If the user has given you nothing measurable, ask for the smallest useful thing rather than
everything: a PageSpeed Insights link (gives both lab and field in one), a DevTools network
waterfall screenshot, or the built bundle sizes. One of those is usually enough to stop
guessing.

## Guardrails

Name a build-time guardrail so a win does not silently erode: a bundle size budget in the
bundler config, a Lighthouse CI assertion on the key metric, or a size-limit check in the
pipeline.
