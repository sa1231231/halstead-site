# Studio sample videos

The `/studio` page shows a grid of sample clips. Drop your files in this folder
using the names the page expects, and prepare each one so it loads fast.

## File names

The grid reads from the `SAMPLES` array near the bottom of
`studio/index.html`. By default it expects:

| Video                  | Poster                 |
| ---------------------- | ---------------------- |
| `sample-1.mp4`         | `sample-1.jpg`         |
| `sample-2.mp4`         | `sample-2.jpg`         |
| `sample-3.mp4`         | `sample-3.jpg`         |
| `sample-4.mp4`         | `sample-4.jpg`         |

To change titles, types, or file names, edit the `SAMPLES` array in
`studio/index.html`. A tile whose file is missing shows a
"New sample coming soon" placeholder, so you can add clips one at a time.

## Targets

Keep each clip small so the grid stays quick on phones:

- **Format:** H.264 MP4 (`.mp4`), `yuv420p` pixel format for broad support.
- **Size:** 1080px on the long side or smaller.
- **Audio:** drop the audio track when it isn't needed. The tiles autoplay
  muted, so most samples do not need sound.
- **Weight:** aim for under 5 MB each.
- **Poster:** a matching `.jpg` still frame, same aspect as the video.

## ffmpeg commands

**Compress and strip audio** (scales down so the long side is at most 1080px,
keeps the aspect ratio, and removes the audio track):

```sh
ffmpeg -i input.mov \
  -vf "scale='min(1080,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 25 -preset veryslow \
  -movflags +faststart -an \
  sample-1.mp4
```

If you want to keep audio, drop the `-an` flag and add `-c:a aac -b:a 128k`.

`-movflags +faststart` moves the index to the front so playback can start
before the whole file downloads. Raise `-crf` (for example to 28) for a
smaller file, or lower it (for example to 22) for higher quality.

**Grab a poster frame** (one JPG from the first second):

```sh
ffmpeg -i sample-1.mp4 -ss 00:00:01 -frames:v 1 -q:v 3 sample-1.jpg
```

Change `-ss` to pick a different moment, and `-q:v` (2 is best, higher is
smaller) to trade quality for size.

## Check the size

```sh
ls -lh sample-*.mp4
```

If any file is over 5 MB, raise `-crf` and re-encode.
