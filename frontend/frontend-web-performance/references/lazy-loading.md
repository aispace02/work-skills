# Lazy loading and facades

Deferring what the user has not reached frees bandwidth and CPU for what they are looking at.
For images this reallocates bandwidth toward LCP candidates. For `<iframe>` elements it also
helps INP, because an iframe is a whole separate document with its own subresources, and
while iframes *can* run in their own process they often share one — so their startup work
competes with your page's responsiveness.

Low effort, good return. Also easy to get exactly wrong, in one specific way (below).

## The `loading` attribute

Works on `<img>` and `<iframe>`, supported in all major browsers.

* **`eager`** — load immediately even if off-screen. **This is the default.**
* **`lazy`** — defer until within some distance of the viewport.

That distance **varies by browser**, and may take account of effective connection type and
the kind of image. Do not treat it as a fixed number, and do not design layouts that depend
on a particular threshold.

Because the attribute is universally supported, **do not reach for a JavaScript lazy-loader
for plain images and iframes.** Shipping JS to do what the browser already does costs you
main-thread time and hurts INP — you would be trading a load win for a responsiveness loss.

**With `<picture>`, put `loading` on the child `<img>`, not on `<picture>`.** The `<picture>`
element is only a container for candidates; the browser applies its choice to the `<img>`.

## Never lazy-load above the fold

This is the one that bites. A lazy image must wait for the browser to finish layout to
discover whether it is near the viewport — which means it is not requested until **all CSS
has downloaded, parsed, and applied**, instead of being fetched the moment the preload
scanner sees it in the raw markup. On an LCP candidate that is a direct, sizeable regression.

Judging position ahead of render is genuinely hard: viewport sizes, aspect ratios, and
orientation all move the fold, and a portrait tablet shows more vertical space than some
desktops. So do not try to be clever. Some cases are unambiguous — hero images, anything near
the top of the layout on any device, anything likely to be the LCP element — and those must
be `eager`.

**`loading` does not affect network priority**, and the two do not cancel out: an in-viewport
image with `fetchpriority="high"` *and* `loading="lazy"` **still waits for all the CSS**. High
priority does not rescue a lazily-discovered image. Remove the `lazy`. See
`resource-hints.md`.

## Iframes and third-party embeds

Embeds are the common case and the savings are large: lazy-loading a YouTube embed saves over
**500 KiB** on initial load, and the Facebook Like button plugin over **200 KiB** — mostly
JavaScript.

Chrome reserves space and shows a placeholder for a lazy iframe while it fetches, to avoid
shift, but **still set `width` and `height`** plus CSS. Do not rely on one engine's courtesy.
See `layout-stability.md`.

## Facades

Show a cheap stand-in and swap in the real third party on interaction. Best available move on
many content pages, because it removes an entire subresource tree from initial load rather
than reordering it.

* **Video embeds** — a static image visually matching the player. Unless the video genuinely
  must autoplay, the user was going to click anyway.
* **Chat widgets** — replace the vendor's "Start Chat" with a fake button. Trigger on a
  meaningful signal: a click, or a pointer held over it for a moment.

The key upside beyond initial load: **if the user never interacts, the resources are never
downloaded at all.** You stop guessing at what they wanted.

Do not build one from scratch first — `lite-youtube-embed`, `lite-vimeo-embed`, and React
Live Chat Loader already exist. Size the facade to match the final widget so the swap does
not shift layout. See `third-party.md`.

## Video: layer it, do not pick one

Baseline status differs sharply between the two, and that difference drives the whole
approach:

| Feature | Baseline |
|---|---|
| `loading` on `<img>` and `<iframe>` | **Widely available** — rely on it |
| `loading` on `<video>` and `<audio>` | **Limited availability** — enhancement only |

So treat video as **progressive enhancement, not a solution.** Check the current Baseline
status before relying on it; this is a moving target.

The pattern that is correct regardless of support:

    <video controls loading="lazy" preload="none" poster="placeholder.jpg">
      <source src="clip.webm" type="video/webm">
      <source src="clip.mp4" type="video/mp4">
    </video>

* **`preload="none"` does the real work today** — it stops the video data downloading in every
  browser.
* **`loading="lazy"` adds the poster deferral** where supported, and delays autoplay until the
  element nears the viewport. Browsers without support simply **ignore it**, loading the
  poster immediately and honouring `preload`. Harmless to include.
* Feature-detect if you need to branch: `"loading" in HTMLVideoElement.prototype`.

See `video.md`.

## When you do need JavaScript

Reach for `lazysizes`, `yall.js`, or your own `IntersectionObserver` for:

* images loaded via CSS `background-image`
* **autoplay video that should only start in the viewport**, in browsers without `loading`
  support — this is the case the declarative attribute does not yet cover everywhere, and the
  one where a library still earns its place
* `<video>` poster deferral where `loading` is unsupported
* anything else with no native equivalent

These use `IntersectionObserver` — plus `MutationObserver` when the page's HTML changes after
load — and swap a placeholder attribute such as `data-src` for the real `src` when the element
approaches the viewport:

    <video class="lazy" autoplay loop muted playsinline width="320" height="480">
      <source data-src="video.webm" type="video/webm">
      <source data-src="video.mp4" type="video/mp4">
    </video>

Muted autoplay video is already far cheaper than an animated GIF, but it is still real
bandwidth — lazy loading it on top is worth doing. See `video.md`.
