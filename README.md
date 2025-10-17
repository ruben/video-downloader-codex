# Video Downloader CLI

Lightweight command-line wrapper around `yt-dlp` that simplifies downloading videos and audio from YouTube and hundreds of other supported sites.

## Prerequisites

- Python 3.9+
- `yt-dlp` (`pip install -r requirements.txt`)
- `ffmpeg` (only required when extracting audio with `--audio-only`)

## Usage

```bash
python video_downloader_cli.py <URL> [options]
```

Common examples:

- Download best available video + audio:
  ```bash
  python video_downloader_cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  ```
- Extract audio as MP3:
  ```bash
  python video_downloader_cli.py "https://youtu.be/dQw4w9WgXcQ" --audio-only
  ```
- List available formats:
  ```bash
  python video_downloader_cli.py "https://youtu.be/dQw4w9WgXcQ" --list-formats
  ```

Run `python video_downloader_cli.py --help` to view all flags (output directory, retries, proxy, quiet mode, playlist support, etc.).

## Notes

- The script defaults to downloading a single video even when given a playlist. Pass `--playlist` to enable bulk downloads.
- When using `--audio-only`, yt-dlp will invoke ffmpeg; ensure it is available on your PATH.
