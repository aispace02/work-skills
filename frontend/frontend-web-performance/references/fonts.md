# Web fonts

Fonts affect both load and render. Large files delay FCP; the wrong `font-display` value
causes visible reflow. They are small in bytes but sit on the critical path for text.

## Discovery

A `@font-face` declaration tells the browser where a font lives, but **the browser does not
download it until layout proves the current page needs it** — a font declared and never used
costs nothing. That is a feature, and it is why blanket preloading of a whole font family is
wasteful.

Because `@font-face` usually lives in an external stylesheet, fonts are **late-discovered**:
nothing happens until that sheet arrives and parses. Two ways to fix that, with different
trade-offs:

* **`preload`** the font file. Earliest possible fetch, does not wait for the stylesheet, and
  does not wait for the font to be needed. That last part is the risk — preload a font the
  page does not use and you have spent bandwidth for nothing.

      <!-- crossorigin is mandatory for fonts, even self-hosted ones -->
      <link rel="preload" as="font" href="/fonts/OpenSans-Regular.woff2" crossorigin>

* **Inline the `@font-face` declarations** in a `<style>` block in `<head>`. Discovered
  without waiting for an external sheet, and it keeps the browser's own needs-based logic, so
  unused fonts are never fetched. Usually the better default.

**Important caveat on inlining**: the browser only starts font downloads once *all*
render-blocking resources have loaded. Inlining `@font-face` while the rest of your CSS sits
in an external sheet means the fonts still wait for that sheet. The win only lands if the
critical CSS is inline too. See `render-blocking.md`.

**Do not base64-inline the font files themselves.** The encoding inflates the payload, and a
large inline blob delays the preload scanner from finding everything else.

## Delivery

* **WOFF2 only.** Up to 30% better compression than WOFF, supported everywhere that matters.
  WOFF, EOT, and TTF are for legacy browsers exclusively; if you do not support those, extra
  formats are pure waste.
* **Self-host where you can.** A third-party font service means an extra connection before
  any font can download. Self-hosting removes it — provided you serve over a CDN with HTTP/2
  or HTTP/3 and correct cache headers.
* **If you use a font service, warm both origins**, since providers often split CSS and font
  binaries across domains:

      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

  Omitting `crossorigin` on the binary origin means the browser opens a second connection and
  the warmed one goes unused. See `resource-hints.md`.

## Subsetting

Fonts ship glyphs for languages you do not serve. Cutting them is often the single biggest
font win.

* Self-hosted: generate subsets with `glyphhanger` or `subfont`, and declare `unicode-range`.
* Google Fonts: `&subset=latin` on the CSS URL.
* Extreme case: `&text=` with only the characters you actually render — for a display face
  used on one word, this is a colossal reduction.

## `font-display`

Four values, and the choice is a real trade-off rather than a best practice:

| Value | Behaviour |
|---|---|
| `block` (default) | Blocks text rendering. Chromium and Firefox block up to ~3 s then use a fallback; **Safari blocks indefinitely**. |
| `swap` | No block. Renders in a fallback immediately, swaps when the font arrives. Most widely used. |
| `fallback` | Very short block, then fallback, then swap. Good on fast networks — the real font often makes the first paint. |
| `optional` | Font is used only if it arrives within 100 ms. Otherwise the fallback is used for this whole navigation while the font downloads into cache, so later navigations get it immediately. |

**Correct a common misconception here.** `swap` is often blamed for CLS, but it is not
usually worse than `block`: `block` also lays the page out using fallback metrics, it just
hides the text while doing so, so both are exposed to the same shift. `swap` is more
*visually jarring*, not necessarily worse for the metric.

The real CLS fix in either case is matching your fallback's metrics to the webfont —
`size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`. See
`layout-stability.md`. `optional` is the option that avoids the shift outright, at the cost of
some users not seeing your typeface on first visit.
