# Resource hints and speculative loading

Hints shape *priority* and *timing*; they do not create bandwidth. Their value comes from
being selective — over-hinting flattens the ordering the browser already computed and
delays the one resource that mattered. See the Traps list in SKILL.md.

Hints can be declared in HTML, usually early in `<head>`, or sent as HTTP headers.

## How browser priority actually works

Worth understanding before reaching for any of these, because it explains which hint helps.

Browsers load in **two phases**. Phase one is reserved for critical resources and ends once
all blocking scripts have downloaded and executed. **Low-priority resources can be held back
entirely during phase one.**

Images are fetched at low priority by default. Only *after layout*, if the image turns out to
be in the initial viewport, is it promoted to high. That post-layout promotion is the delay
`fetchpriority="high"` removes — it puts the image in phase one immediately instead of making
it wait for layout to prove it matters.

* **`preconnect`** for critical cross-origin servers, to get DNS, TCP, and TLS out of the
  way early. Add `crossorigin` for CORS fetches like fonts, or the warmed connection goes
  unused.
* **`dns-prefetch`** as the cheap option when `preconnect` would be excessive — it resolves
  the name without opening a connection. Good for outbound links the user may follow;
  tools exist that inject it via `IntersectionObserver` as such links scroll into view.
* **`preload`** only for genuinely late-discovered critical resources — fonts (though for
  fonts, inlining `@font-face` is usually the better tool; see `fonts.md`), sheets pulled
  in by `@import`, CSS `background-image` LCP candidates, anything a script loads. Three ways
  to get this wrong, all of which cause a **double download**:
  * **Missing `as`.** Required. Without it the browser cannot match the preload to the real
    request, and fetches twice.
  * **`crossorigin` mismatch.** Needed for CORS fetches such as fonts, and harmful on
    non-CORS ones. It must match what the real fetch does, in both directions:
    `<link rel="preload" href="/font.woff2" as="font" crossorigin>`
  * **Responsive images.** Use `imagesrcset`, and **omit `src`**, so browsers without
    responsive-preload support do not grab the fallback image as well.

  For images specifically, also set `fetchpriority="high"` on the preload. **Preload does not
  raise priority**, and images start low — so a preloaded LCP image without it is still
  waiting behind phase one.
* **`fetchpriority`** works on `<link>`, `<img>`, and `<script>`. Set `"high"` on the LCP
  image and `"low"` on thumbnails, below-fold images, and non-first carousel slides. For an
  LCP image already present in the HTML this is usually a bigger win than preloading, with
  none of the double-download risk — the image is discoverable, it just needed priority.
* **`<link rel="prefetch">`** at *lowest* priority for something needed soon, so it does not
  contend with the current page. Same shape as `preload`, but speculative: the bytes are
  wasted if the navigation never happens. Justify it from analytics showing a flow most users
  complete, not from a guess. It is only a hint — browsers weigh network quality and
  system-level preferences and may decline. Skip it entirely when `Save-Data` is set or the
  connection is slow. Supported everywhere modern except Safari, where it is behind a flag.

      <link rel="prefetch" as="script" href="/date-picker.js">
      <link rel="prefetch" href="/page" as="document">   <!-- whole page + subresources -->

  **Two things not to prefetch as documents**: cross-origin documents, which currently
  produce duplicate requests, and personalized same-origin documents such as authenticated
  HTML, which are not cacheable and so almost always wasted.
* **Speculation Rules API** — a JSON block declaring `prefetch` or `prerender` actions with
  a URL list, in the HTML or injected later:

      <script type="speculationrules">
      { "prefetch": [{ "source": "list", "urls": ["/page-a", "/page-b"] }] }
      </script>

  Also a hint the browser may ignore. Useful difference from the link relation:
  **`<link rel="prefetch">` stores in the HTTP cache, while speculation-rules prefetches go
  to the memory cache** and come back faster. Gate speculation on intent rather than firing
  on load — the `eagerness` field (`immediate`, `eager`, `moderate`, `conservative`) does this
  natively, with `moderate` roughly meaning hover and `conservative` meaning pointerdown, and
  libraries such as Quicklink achieve the same by acting on links as they enter the viewport.
  Either way, speculating on links the user has shown interest in beats speculating on all of
  them.

* **Prerendering** goes further than prefetch: the page and its subresources are fetched
  *and processed* in the background, then swapped to the foreground on navigation. Nearly
  instant, and expensive — **a full prerender executes the target page's JavaScript.** Use it
  sparingly and only where intent is close to certain.

  Beware `<link rel="prerender">`: since Chrome 63 it does **not** prerender. It triggers a
  NoState Prefetch, which fetches the page's resources without rendering or running scripts.
  Use Speculation Rules if you mean a real prerender.

## Precaching

Service Worker precaching is the repeat-visit and offline case rather than a first-load hint.
Covered in `delivery.md`.

## Shared caution

Prefetching, prerendering, and precaching all spend the user's bandwidth, storage, and CPU on
a prediction. When the prediction is wrong it is pure waste, paid by someone who may be on a
metered connection. Speculate narrowly and only where the data supports it.
