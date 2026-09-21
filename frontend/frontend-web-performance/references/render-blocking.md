# Critical rendering path and JavaScript payload

The browser needs the DOM and the CSSOM before it can build a render tree and paint. CSS in
the `<head>` blocks rendering; synchronous JavaScript blocks the parser itself.

## What the initial render actually waits for

HTML is processed as a stream: the browser starts work on the first bytes and will often
render well before the whole document arrives. Rendering is deliberately blocked on a
minimum set of resources, because painting too early shows a broken page that then jumps.

**Waits for**: part of the HTML, render-blocking CSS in `<head>`, render-blocking JS in
`<head>`.

**Does not wait for**: the rest of the HTML, fonts, images, non-blocking JS below `<head>`,
and CSS whose `media` value does not match the current viewport.

That second list is why fonts and images are late-arriving content that gets filled in on a
later pass — and why unreserved space for them becomes layout shift rather than a slow
render. See `layout-stability.md`.

## Blocking: render vs parser

**Render-blocking** (CSS by default): the browser pauses painting but keeps *processing*
HTML and looking for other work. The reason is FOUC — a flash of unstyled content, where the
page appears raw and then snaps into place. Blocking is not the enemy here; a long block is. Modern Chrome and Firefox only block content *below* the
resource, which is exactly why `<head>` resources matter — they block the whole page.

**Parser-blocking** (synchronous JS): the parser cannot continue at all until the script is
fetched and executed, because the script may change the DOM or CSSOM. This is strictly worse
than render-blocking, and it is effectively render-blocking too, since content after the
script cannot be reached. To limit the damage the browser runs a **preload scanner** — a
secondary parser that scans ahead for resources to fetch while the primary parser is stuck.
It cannot execute anything, but it keeps the network busy.

A parser-blocking script also has to wait for any **in-flight render-blocking CSS** to arrive
and parse before it can execute, since it might read computed styles. So a slow stylesheet
delays your scripts too, which is not obvious from the markup.

### What the preload scanner cannot see

Anything not in the server-sent HTML is late-discovered:

* Images referenced from CSS `background-image`.
* `<script>` elements injected into the DOM by JavaScript, and modules pulled in by
  dynamic `import()`.
* Markup rendered client-side, since it lives inside JS strings.
* Stylesheets pulled in by CSS `@import`.

Note the tension with code splitting: dynamic `import()` is the right tool for cutting
initial payload, and it is also invisible to the scanner. That is fine for
interaction-triggered chunks and a problem for anything needed early — in which case pair it
with a hint from `resource-hints.md`.

Two attributes worth knowing:

* **`media`** turns CSS non-blocking when the value cannot match:
  `<link rel="stylesheet" href="..." media="print">` is the classic way to load
  non-critical CSS off the critical path.
* **`blocking=render`** (Chrome 105+) does the opposite deliberately: mark a `<link>`,
  `<script>`, or `<style>` as render-blocking until processed, while letting the parser
  continue. Use when something genuinely must be in place before first paint.

## Unblocking the parser and the paint

* **Replace CSS `@import` with `<link rel="stylesheet">`.** An `@import` is only discovered
  after its parent stylesheet downloads and parses, creating a serial request chain the
  preload scanner cannot see through. Multiple `<link>` elements download concurrently;
  `@import`s download consecutively. Two exceptions worth knowing before you flag it:
  preprocessor `@import` (SASS, LESS) is resolved at build time into one sheet and carries
  no runtime penalty, and where runtime `@import` is unavoidable — cascade layers, some
  third-party sheets — preloading the imported sheet mitigates the delay.
* **Inline the CSS for above-the-fold content**, load the rest asynchronously — but treat
  this as a considered project, not a quick win. Inlined CSS is not cached, so subsequent
  pages that would have reused the external sheet pay for it again, and the bigger HTML
  response eats into the time it was meant to save. Extraction is also genuinely hard:
  which styles count as critical, which viewport you target, whether it can be automated,
  and what the user sees if they scroll before the rest arrives. Worth it on some sites,
  prohibitive on others — say which you think it is.
* **Minify CSS and JS.** For JS, minification goes further than stripping whitespace: it
  also shortens symbols (uglification), so `scriptElement` becomes `t`. Bundlers do this on
  production builds; Terser's defaults are usually the right balance.
* **Remove unused CSS.** Two wins, not one: less to download, and fewer rules for render
  tree construction. Do not expect to eliminate all of it — find the big blocks, and either
  move them to a separate sheet for the page that needs them or delete them as dead. Chrome
  DevTools Coverage identifies them.
* **`defer`** for scripts needing the parsed DOM, **`async`** for independent ones
  (analytics, feature detection). Both unblock the parser, but the execution semantics differ
  and it matters: `async` runs the moment it arrives and may run **out of order**, so it can
  still preempt rendering and cannot be used where scripts depend on each other. `defer` runs
  after parsing completes, at `DOMContentLoaded`, and **in document order**.
* **`type="module"` is deferred by default**, so it needs no `defer`. Conversely a `<script>`
  injected into the DOM by JavaScript behaves like `async`, whether you intended that or not.
* **Apply `content-visibility: auto` with `contain-intrinsic-size`** to long off-screen
  sections to skip their rendering work. Without the intrinsic size hint it causes scrollbar
  jumps — see `layout-stability.md`.

## Late discovery

The preload scanner reads raw HTML ahead of the parser to start fetches early. Anything it
cannot see is discovered late:

* **Avoid client-side rendering for critical content, especially the LCP element.** Markup
  that exists only after JS runs is invisible to the scanner, so its resources are fetched
  late no matter how well everything else is tuned.
* CSS background images, `@import`ed stylesheets, and JS-injected elements are all invisible
  to it. If one of them is critical, `preload` is the remedy — see Resource hints below.

## Code splitting

Split with dynamic `import()` so the initial load ships only what the first view needs. This
is the main lever on Total Blocking Time. Bundlers (webpack, Rollup, Vite, Parcel, esbuild)
create a separate chunk per dynamic import; esbuild requires opting in. React's
`React.lazy` wraps dynamic `import()` and still relies on the bundler to split.

**Chunk size is a balance, not a direction.** Larger bundles compress better but produce
longer evaluation tasks and invalidate more cache when one dependency changes; smaller ones
cache better across visits but compress worse and add round trips. Splitting more is not
monotonically better. In webpack, `SplitChunksPlugin` with `chunks: async | initial | all`
controls which imports split, and `maxSize` breaks oversized chunks into smaller evaluation
tasks.

**Bundle rather than shipping raw module trees.** Every unbundled module is its own HTTP
request, and complex trees delay interactivity. `<link rel="modulepreload">` mitigates this
but bundling remains the better loading strategy.

## Streaming compilation

V8 compiles chunks of JS as they arrive from the network. It applies this to any script that
does **not** use JavaScript modules, so the first option is to have the bundler target a
non-module syntax for production. If you do ship modules, **use the `.mjs` extension** —
there is no separate content type for module versus non-module JavaScript, so shipping
modules as `.js` effectively opts out of streaming compilation, and the extension is the only
signal V8 has. Separately, confirm the server sends `.mjs` as `text/javascript`; some default
to `application/octet-stream`, which stops the script executing at all.

For getting late-discovered resources fetched earlier, and for shaping priority, see
`resource-hints.md`.
