# Video

## Containers, streams, codecs

The file extension (`.mp4`, `.webm`) is the **container**. A container holds **streams**,
usually one video and one audio. Each stream is compressed with a **codec**. `video.webm`
might be a WebM container with a VP9 video stream and a Vorbis audio stream.

This matters because the container is not what determines size — the codec and its settings
are. WebM can carry **AV1** (best compression, narrower support) or **VP9** (wider support,
compresses less well).

    ffmpeg -i input.mov output.webm          # smaller, works in modern browsers
    ffmpeg -i input.mov -an output.webm      # ...and drop the audio stream entirely

**`-an` strips all audio.** Do this whenever audio is not needed — a GIF replacement, a
background loop. It shrinks the file even when the source audio is already silent.

For finer control, `-crf` (Constant Rate Factor) sets the compression level for H.264 and
VP9 — one integer trading size against quality.

## Multiple sources

    <video poster="poster.jpg">
      <source src="video.webm" type="video/webm">
      <source src="video.mp4" type="video/mp4">
    </video>

**Order is priority, not preference.** The browser takes the first source it can play, so an
MP4 listed first will be used even by browsers that support something far more efficient.
List modern formats first and MP4/H.264 last as the universal fallback.

## Poster images and LCP

`poster` gives the user something immediately, and it is a valid LCP candidate.

Worth knowing: a video without a poster used to be excluded from LCP candidacy, but that was
fixed — the **first painted video frame now counts too**. So the choice is no longer
"poster or no LCP", it is which one you can paint sooner. If the video does not autoplay, use
a poster. If it does, make sure the video itself starts fast, because the first frame is now
your LCP.

If the poster *is* your LCP element you can promote it:

    <link rel="preload" as="image" href="poster.jpg" fetchpriority="high">

But only then. If the video is not the largest element in the viewport, preloading its poster
creates bandwidth contention and can push LCP *later*. See `resource-hints.md`.

## Autoplay

For GIF replacements and background video: `autoplay muted loop playsinline`. Without `muted`
and `playsinline`, mobile browsers refuse to autoplay at all. Animated GIFs routinely run to
several megabytes; the video equivalent is dramatically smaller, so this is usually a large
straightforward win.

**Autoplay videos start downloading immediately, even when outside the initial viewport.**
That is easy to miss and expensive. `loading="lazy"` is designed to fix exactly this by
delaying autoplay until the element nears the viewport — but support is still arriving, so
today the reliable route is `poster` plus `IntersectionObserver`, attaching the source only as
the element approaches. Cost of that approach: the user sees the poster briefly before
playback begins.

Autoplay is also an experience decision, not just a performance one, and browsers apply their
own eligibility criteria — a video with audio that starts unbidden is hostile. Use it only
where the page genuinely calls for it.

## Deferring user-initiated video

By default the browser starts fetching as soon as the parser sees the `<video>` element,
which is wasted data for a video most visitors never play.

* **`preload="none"`** — fetch nothing up front. The right default for click-to-play video.
* **`preload="metadata"`** — fetch duration and similar cursory data only.
* **`loading="lazy"`** — where supported, defers the poster and delays autoplay until the
  element nears the viewport. **Baseline: Limited availability** on `<video>`, unlike on
  `<img>` and `<iframe>` where it is Widely available. Add it on top of `preload`, never
  instead of it: browsers lacking it ignore the attribute and fall back to `preload`
  behaviour. See `lazy-loading.md`.

`preload` is a *hint*: browsers may ignore it, and behaviour differs between engines and
between mobile and desktop. Do not build logic that depends on it being obeyed.

## Third-party embeds

Offloading to YouTube or Vimeo solves encoding and delivery, and imports a large JavaScript
payload in exchange. YouTube embeds block the main thread for over **1.7 seconds** on the
median site, which is an INP problem as much as a load problem.

The compromise is a **facade**: ship a static poster and swap in the real embed on
interaction. See `lazy-loading.md` and `third-party.md`.
