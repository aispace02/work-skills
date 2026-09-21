# Delivery, caching, and TTFB

TTFB is everything before the first byte of HTML arrives. It sets a floor under every other
metric — no amount of frontend tuning recovers a 1.2 s server response.

## Connection and transport

* **Eliminate redirect chains.** Each hop is a full round trip before any useful byte.
  Same-origin redirects are entirely yours to fix — the trailing-slash pattern
  (`example.com/page/` to `example.com/page`) is the usual offender, and the fix is to
  correct the *internal links* so they point at the final URL rather than to keep serving
  the redirect. Cross-origin redirects come from ads, URL shorteners, and other third
  parties and are largely outside your control, but still check for stacked chains: an ad
  linking to an HTTP page that redirects to HTTPS and then triggers a same-origin redirect
  is three round trips before your server does any work.
* **Serve over HTTP/2 or HTTP/3.** Head-of-line blocking on HTTP/1.1 penalises the many
  small requests a modern page makes.
* **Use a CDN.** Most TTFB for a geographically distant user is propagation delay, and only
  an edge server fixes that.
* **Consider `103 Early Hints`** to start critical asset fetches during backend
  think-time — useful when the server has unavoidable work before it can stream HTML.

## Compression

Compress text responses — HTML, JS, CSS, SVG — with **Brotli**, which runs about 15–20%
better than gzip and is supported everywhere. Keep gzip as fallback for legacy clients;
any compression beats none.

* **Static compression** for assets that do not change per request (JS, CSS, SVG): compress
  at build time so no latency is spent compressing during the response.
* **Dynamic compression** for HTML, especially when generated per authenticated user.
* **Very small files barely compress.** Under about 1 KiB there is not enough data for the
  algorithm to find redundancy in, and it may not compress at all.
* **Do not inflate files because large ones compress better.** Large JS and CSS cost
  significantly more to parse and evaluate *after* decompression, and they invalidate cache
  more often, since any change produces a new hash.

## Caching

* **Static assets**: hashed filenames plus `Cache-Control: public, max-age=31536000,
  immutable`. The hash makes the URL content-addressed, so the cache never needs revalidation.
* **Non-personalized HTML**: a short window — five minutes is a safe default — with `ETag`
  or `Last-Modified`. The value is partly at the CDN, which absorbs origin requests, and
  partly in the browser, where a match on `If-None-Match` yields a `304 Not Modified` that
  is far smaller than the document. Weigh it honestly though: revalidation still costs a
  round trip, so not caching HTML at all is a legitimate choice rather than a failure.
* **Authenticated or personalized HTML**: do not cache at all. Two reasons, and the second
  is the one people forget: leaking one user's HTML to another is worse than a slow page,
  and once a response is in a user's browser cache you have no way to invalidate it.
* **Caveat on HTML caching generally**: the document references fingerprinted subresources,
  so a cached HTML file can outlive the build it was made for and point at assets that no
  longer exist. Keep the window short enough that a deploy cannot strand users.
* **Service Worker precaching**: a **cache-only** strategy — eligible resources are fetched
  from the network once, during service worker **installation**, and afterwards served from
  the cache without touching the network. Once installed they are available to every page the
  worker controls.

  Workbox is worth using over a hand-rolled worker mainly for **versioning**: it maintains a
  **precache manifest**, and on worker update it evicts expired entries for you.

      [{ url: 'script.ffaa4455.js', revision: null },
       { url: '/index.html',        revision: '518747aa' }]

  `revision: null` is correct for a file whose name already contains a content hash; unhashed
  files need a revision generated at build time. Never precache a URL that is neither
  content-addressed nor revisioned, or users get pinned to a stale build.

  **The `Cache` interface is not the HTTP cache.** `Cache` is a high-level store you control
  from JavaScript; the HTTP cache is low-level and driven by `Cache-Control`. They coexist and
  behave differently.

  Precache too little rather than too much — an oversized manifest spends bandwidth, storage,
  and CPU at install time. Fill the rest in with runtime caching.

## Back/forward cache

Keeping the page bfcache-eligible makes back-navigation effectively instant, and losing
eligibility is a common accidental regression:

* Use `pagehide` and `visibilitychange` instead of `unload`. An `unload` handler alone
  disqualifies the page.
* Do not send `Cache-Control: no-store` on the main document.
* Close open `IndexedDB` transactions and avoid in-flight `fetch` at navigation time.

## Where TTFB actually goes

If the response is not cached, TTFB is mostly your hosting and backend stack. Two things
worth naming to the user:

* **Shared hosting is a common cause of high TTFB.** Dedicated or managed alternatives cost
  more; that is a budget conversation, not a code change, and worth stating as such.
* **Moving data fetching to the client does not remove the work, it relocates it** from a
  predictable server to an unpredictable device. A spinner plus client-side fetch usually
  makes user-centric metrics worse, not better, even though it improves TTFB in isolation.
  Beware optimizing the metric rather than the experience.

## Attribution

Emit **`Server-Timing`** headers for backend phases so field TTFB can be attributed instead
of guessed at:

    Server-Timing: auth;dur=55.5, db;dur=220

Each entry is a name and a duration in milliseconds — here 55.5 ms authenticating and 220 ms
in the database. Collect it from real users via the Navigation Timing API. Without this, a
slow TTFB in CrUX is a number with no explanation attached.
