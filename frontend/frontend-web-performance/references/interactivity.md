# Interactivity and the main thread (INP)

INP measures the worst interaction latency a real user experienced. It decomposes into
**input delay** (the handler cannot start because the thread is busy), **processing time**
(the handler itself), and **presentation delay** (the resulting frame has not painted).
Long tasks are the usual culprit, either blocking the start or being the handler.

## Yield

* **Break long tasks and yield to the main thread.** `await scheduler.yield()` where
  available, with a `setTimeout` fallback, so a queued click can be serviced mid-work.
  Yielding is what lets a long job coexist with a responsive UI.
* **Do the visual update the user is waiting for first**, then defer analytics, logging, and
  non-visual bookkeeping to after the next paint. The user judges the paint, not the
  bookkeeping.

## Web Workers

JavaScript is single-threaded only by default. The main thread handles scripting, HTML and
CSS parsing, and much of the rendering work; browsers use other threads (GPU, rasterizer) you
do not address directly. The Web Workers API is how you get one you can.

* **Offload genuinely expensive computation** — parsing, image metadata, large transforms,
  compression:

      const worker = new Worker('/js/worker.js');
      worker.postMessage(input);
      worker.addEventListener('message', ({ data }) => { /* update DOM here */ });

  Inside the worker the scope is **`self`**, not `window`. No direct DOM access, but plenty
  of the platform: `fetch`, the JS primitives, and a large set of other APIs. The messaging
  pipeline is the escape hatch — the worker computes, posts plain data back, and the main
  thread touches the DOM.

* **Move the library, not just the loop.** Import dependencies *inside* the worker with
  `importScripts('/js/lib.js')` (or static `import` in a module worker) and the cost of
  downloading, parsing, and compiling that library leaves the main thread too. On a heavy
  dependency this is often a larger win than the computation you moved.

* **Fetch in the worker.** Workers have `fetch`, so a request plus its response processing can
  happen entirely off-thread. Combine with a range request when you only need part of a file —
  `Range: bytes=0-65535` to read an image's metadata without downloading the whole image.

* **Weigh serialization cost first.** `postMessage` structured-clones its payload, so
  shuttling a large object to do cheap work is a net loss. Workers pay off for sustained or
  heavy computation; use transferables or `SharedArrayBuffer` for large buffers.

* **Reach for an abstraction when the pipeline gets complicated.** Raw `postMessage` is fine
  for one round trip; Comlink is worth it once there are several message types to keep
  straight.

## Handlers and rendering

* **Debounce or throttle high-frequency handlers** — `scroll`, `pointermove`, `input`.
* **Batch DOM reads before writes.** Interleaving them forces synchronous layout in a loop,
  which is the classic accidental long task.
* **In frameworks, find the large re-render**: unmemoized expensive subtrees, state lifted
  too high, long lists without virtualization. A framework's default hydration strategy is a
  frequent INP problem worth checking explicitly.

## Client-side rendering

Rendering markup with JavaScript costs more than interactivity alone. It is more likely to
generate long tasks than server-sent markup, and the cost scales with DOM size — a very large
DOM makes every JS mutation expensive, which shows up directly as interaction latency. This
is the INP half of the argument in `render-blocking.md` against client-rendering critical
content; the LCP half is late resource discovery.

## Load-time interactivity

Total Blocking Time during load correlates strongly with field INP, because users try to
interact while the page is still starting up. Reducing initial JavaScript is therefore an INP
fix as much as a load fix — see `render-blocking.md` for code splitting, and
`third-party.md`, since third-party script evaluation competes for the same thread.
