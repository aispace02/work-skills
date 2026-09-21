# Layout stability (CLS)

Layout shift is mostly a matter of reserving space for things that have not arrived yet. CLS
is measured across the whole page lifespan, not just load, so late-injected content counts.

## Reserve space

* **Dimensions or `aspect-ratio`** on every image, video, `<iframe>`, and ad slot. The most
  common single cause of CLS — see `images.md`.
* **Reserve height for injected content**: banners, consent notices, promo bars. If the
  height is genuinely unknown, render it in a fixed-height container or overlay it rather
  than letting it push content down.
* **Lazy-loaded iframes still need dimensions.** Chrome reserves space and shows a
  placeholder while fetching one, but that is a single engine's behaviour, not a guarantee —
  set `width` and `height` plus CSS anyway. See `lazy-loading.md`.
* **`contain-intrinsic-size` alongside `content-visibility: auto`**, or skipped rendering
  causes scrollbar jumps as sections realise their real height.

## Fonts

Match fallback font metrics to the webfont so the swap does not reflow text:
`size-adjust`, `ascent-override`, `descent-override`, `line-gap-override` on a
`@font-face` block for the local fallback family. See `fonts.md` for the loading strategy
these pair with.

## Animation and interaction

* **Animate only `transform` and `opacity`.** Animating `width`, `height`, `top`, or `left`
  triggers layout every frame, costing both CLS and frame budget.
* **Shifts within 500 ms of a user interaction are excluded** from CLS, which is why an
  accordion expanding on click is fine and the same expansion firing on load is not.

## Regressions to watch

* Third parties that inject DOM — consent banners, A/B test flicker — show up as CLS rather
  than as bytes. See `third-party.md`.
* Losing bfcache eligibility means back-navigation re-runs the whole load, reintroducing
  every shift the user already sat through. See `delivery.md`.
