# Images

Images are usually the heaviest and most prevalent resource on a page, and the most common
LCP element. This is the highest-leverage area on most sites. Two levers: send fewer bytes,
and send bytes sized for the device that asked.

## Sizing and DPR

An image in a 500×500 CSS-pixel container is optimally 500×500 *only at DPR 1*. At DPR 2 the
optimal intrinsic size is 1000×1000, at DPR 3 it is 1500×1500. That is why one fixed image
is always wrong for someone.

Useful pragmatism: most eyes cannot resolve the difference at DPR 3, so serving below the
theoretical optimum for high-DPR devices is usually free quality-wise and saves real bytes.

## `srcset` and `sizes`

Two descriptor flavours, and mixing them up is the common bug:

* **Density descriptors** (`1x`, `2x`, `3x`) — for an image displayed at the same CSS size on
  every viewport. No `sizes` needed.

      <img src="/image-500.jpg" width="500" height="500" alt=""
           srcset="/image-500.jpg 1x, /image-1000.jpg 2x, /image-1500.jpg 3x">

* **Width descriptors** (`500w`, `1000w`) — describe each candidate's *intrinsic* width, for
  images whose layout size changes with viewport. **These require `sizes` or they do not
  work at all.** `sizes` describes the intended display size in CSS pixels.

      <img src="/image-500.jpg" width="500" height="500" alt=""
           srcset="/image-500.jpg 500w, /image-1000.jpg 1000w, /image-1500.jpg 1500w"
           sizes="(min-width: 768px) 500px, 100vw">

The browser combines `sizes` with DPR to pick: a 320 px viewport at DPR 3 needs 960 device
pixels, so it takes the `1000w` candidate. Inaccurate `sizes` therefore causes systematic
over-fetching, since the browser resolves ambiguity by assuming full viewport width.

**Always set `width` and `height`** (or a CSS `aspect-ratio`) so space is reserved before the
image lands. Most common cause of layout shift — see `layout-stability.md`.

## `<picture>`

For format fallbacks and for genuinely different art per viewport:

    <picture>
      <source type="image/avif" srcset="image.avif">
      <source type="image/webp" srcset="image.webp">
      <img src="/image.jpg" width="500" height="500" alt="">
    </picture>

The browser takes the first matching `<source>` and stops, so order best-format-first. An
`<img>` child is **required**, and its `alt`, `width`, and `height` apply no matter which
source wins — put them there, not on the sources.

Key distinction: **`srcset` is a hint the browser may override; `media` on a `<source>` is a
command it must obey.** Reach for `media` when you need control (for example capping the
image served to small viewports), and `srcset` when you want the browser to optimise.

## Formats

* **AVIF** — best compression, often 50%+ below comparable JPEG. Lossy and lossless, plus
  wide colour gamut and HDR. Support is decent but not universal, so pair with a fallback.
* **WebP** — universally supported in modern browsers, better than JPEG/PNG/GIF, lossy and
  lossless, and it keeps **alpha transparency even under lossy compression**, which JPEG
  cannot do at all.
* **SVG** — for line art, diagrams, charts, icons. Wrong choice for photographs. It is text,
  so minification and Brotli apply, and `svgo` does lossy structural optimisation.

## Choosing lossy vs lossless

Match the compression to the content, not to a global default:

* **Lossy** (JPEG, WebP, AVIF) — quantisation plus chroma subsampling. Excellent on
  photographs and noisy, detailed imagery where artifacts hide. Poor on line art, sharp
  edges, and text; high-contrast coloured text on flat colour is especially prone to chroma
  subsampling artifacts.
* **Lossless** (PNG, WebP, AVIF, GIF) — encodes pixels as differences from neighbours. Use
  where lossy artifacts would be visible.

There is no universal quality setting. Experiment per image with Squoosh or ImageOptim and
check the result actually meets your quality bar.

## Variant count is a real cost

Every extra variant is another cache entry, more origin storage and cost, another chance of
a cache miss that goes back to origin — and kilobytes of extra HTML per image. One variant
caches perfectly for everyone; twenty cache badly for everyone.

A full-bleed hero justifies more variants than a product thumbnail. Pick a reasonable number
and measure, rather than generating every permutation.

### Content negotiation instead of markup

You can serve the best format from the server without any of that HTML weight, by reading the
`Accept` request header:

    Accept contains "image/avif"  ->  serve image.avif
    Accept contains "image/webp"  ->  serve image.webp
    otherwise                     ->  serve image.jpg

Every common server and framework can do this — rewrite rules, middleware, or an edge
function. Match the idiom of whatever stack is in front of you.

**Send `Vary: Accept`** with the response, or shared caches and CDNs will hand one user's
AVIF to a client that cannot decode it. Note that `Accept` reliably advertises image support
on requests for HTML and images; do not assume it elsewhere. An image CDN does all of this
for you and is usually the better buy than maintaining a pipeline.

## Loading behaviour

* **`loading="lazy"`** on off-screen images.
* **Never lazy-load the LCP image or anything above the fold.** Lazy loading defers the
  fetch until layout runs, which is exactly the delay you are removing. See
  `lazy-loading.md`.
* **`fetchpriority="high"`** on the LCP image is often the single cheapest win — images start
  at low priority. See `resource-hints.md`.
* **`decoding`** takes `async`, `sync`, or `auto` (default). `async` permits decoding without
  blocking presentation. The effect is only measurable on very large, high-resolution images,
  so treat it as a finishing touch, not a fix. `HTMLImageElement.decode()` is the
  programmatic equivalent when inserting images from JavaScript.
