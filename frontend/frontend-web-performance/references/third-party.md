# Third-party scripts

Third-party code is frequently the dominant cost and the part the team least controls, which
makes it its own audit surface. It damages every metric at once: bytes and blocking hurt LCP,
main-thread evaluation hurts INP, and injected DOM hurts CLS.

## Inventory first

Name each third party, what it costs in bytes and main-thread time, and whether the business
still uses it. **Removals beat optimizations** — abandoned tags from old campaigns are common
and free to delete. A tag manager makes this harder to see, since one container can hide
dozens of tags; enumerate what it actually loads rather than trusting the container.

## Then defer, then facade

* **`async` or `defer` prevents parser blocking but not main-thread contention.** A deferred
  analytics bundle still competes with the user's first click.
* **Load on interaction or on idle** where the vendor allows it.
* **Facade the heavy widgets** — a static poster replacing a YouTube embed, a button
  replacing a chat widget — so the subresource tree only loads on intent. For scale: YouTube
  embeds block the main thread for over **1.7 seconds** on the median site, so this is an INP
  fix as much as a weight fix. See `lazy-loading.md` and `video.md`.
* **Self-host where licensing permits**, so you get your own caching and connection reuse
  instead of an extra origin handshake.

## Isolate what you cannot remove

* `preconnect` to the origins that remain critical, so the handshake is not on the critical
  path. See `render-blocking.md`.
* Reserve space for anything that injects DOM — consent banners, A/B test containers — or it
  lands as CLS. See `layout-stability.md`.
* Consider `<iframe>` isolation for widgets that only need to render, since script evaluation
  in a separate document does not block the main frame's thread the same way.
* Set an explicit budget. Third-party weight grows by accretion, and without a stated ceiling
  each individual addition always looks affordable.
