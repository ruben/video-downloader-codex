#!/usr/bin/env python3
"""
Simple command-line YouTube (and supported sites) video downloader built on yt-dlp.

Usage examples:
  python video_downloader_cli.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
  python video_downloader_cli.py URL --audio-only --audio-format mp3
  python video_downloader_cli.py URL --list-formats

The script requires the `yt-dlp` package (`pip install yt-dlp`) and ffmpeg for
audio conversions.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:  # pragma: no cover - handled gracefully at runtime
    YoutubeDL = None
    DownloadError = Exception


@dataclass
class DownloadConfig:
    url: str
    outtmpl: str
    fmt: str
    quiet: bool
    audio_only: bool
    audio_format: str
    keep_video: bool
    playlist: bool
    proxy: Optional[str]
    retries: int
    metadata_only: bool
    list_formats: bool


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a single video (or optionally a playlist) using yt-dlp."
    )
    parser.add_argument("url", help="Video or playlist URL to download.")
    parser.add_argument(
        "-o",
        "--output",
        default="%(title)s.%(ext)s",
        help="Output filename template. Defaults to '%%(title)s.%%(ext)s'.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write the downloaded file into. Defaults to current directory.",
    )
    parser.add_argument(
        "-f",
        "--format",
        default=None,
        help="Explicit yt-dlp format string (overrides audio-only selection).",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Download audio only (best quality). Requires ffmpeg for conversion.",
    )
    parser.add_argument(
        "--audio-format",
        default="mp3",
        help="Preferred audio format when using --audio-only. Defaults to mp3.",
    )
    parser.add_argument(
        "--keep-video",
        action="store_true",
        help="Keep the original downloaded video file after extracting audio.",
    )
    parser.add_argument(
        "--playlist",
        action="store_true",
        help="Allow playlist downloads. By default only the first video is downloaded.",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List the available formats for the URL and exit.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show metadata for the URL and exit without downloading.",
    )
    parser.add_argument(
        "--proxy",
        help="Use the specified HTTP/HTTPS/SOCKS proxy.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce yt-dlp output to warnings/errors only.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of download retries on failure. Defaults to 3.",
    )

    args = parser.parse_args(argv)

    if args.audio_only and args.format:
        parser.error("--audio-only cannot be combined with --format.")

    return args


def ensure_output_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def build_config(args: argparse.Namespace) -> DownloadConfig:
    output_dir = Path(args.output_dir).expanduser()
    ensure_output_dir(output_dir)
    outtmpl = str(output_dir / args.output)

    if args.audio_only:
        fmt = "bestaudio/best"
    else:
        fmt = args.format or "bestvideo*+bestaudio/best"

    return DownloadConfig(
        url=args.url,
        outtmpl=outtmpl,
        fmt=fmt,
        quiet=args.quiet,
        audio_only=args.audio_only,
        audio_format=args.audio_format,
        keep_video=args.keep_video,
        playlist=args.playlist,
        proxy=args.proxy,
        retries=max(args.retries, 0),
        metadata_only=args.info,
        list_formats=args.list_formats,
    )


def make_ydl_opts(config: DownloadConfig) -> dict:
    opts: dict = {
        "outtmpl": config.outtmpl,
        "format": config.fmt,
        "quiet": config.quiet,
        "noplaylist": not config.playlist,
        "ignoreerrors": False,
        "retries": config.retries,
    }

    if config.proxy:
        opts["proxy"] = config.proxy

    if config.audio_only:
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": config.audio_format,
            }
        ]
        opts["keepvideo"] = config.keep_video

    return opts


def fetch_info(ydl: YoutubeDL, url: str) -> dict:
    return ydl.extract_info(url, download=False)


def first_entry(info: dict) -> dict:
    if info.get("_type") != "playlist":
        return info
    entries = info.get("entries") or []
    for entry in entries:
        if entry:  # skip None entries that yt-dlp can yield
            return entry
    raise ValueError("Playlist has no downloadable entries.")


def print_formats(info: dict) -> None:
    formats = info.get("formats") or []
    if not formats:
        print("No formats available.")
        return

    header = f"{'itag':>6}  {'ext':>5}  {'res':>7}  {'fps':>4}  {'vcodec':>10}  {'acodec':>10}  {'filesize':>10}"
    print(header)
    print("-" * len(header))
    for fmt in formats:
        itag = fmt.get("format_id", "n/a")
        ext = fmt.get("ext", "n/a")
        resolution = fmt.get("resolution") or fmt.get("height") or "audio"
        fps = fmt.get("fps") or ""
        vcodec = fmt.get("vcodec") or ""
        acodec = fmt.get("acodec") or ""
        filesize = fmt.get("filesize") or fmt.get("filesize_approx") or 0
        if isinstance(resolution, int):
            resolution = f"{resolution}p"
        if filesize:
            filesize_mb = filesize / (1024 * 1024)
            filesize_str = f"{filesize_mb:>7.2f}MB"
        else:
            filesize_str = "   n/a"
        print(
            f"{itag:>6}  {ext:>5}  {str(resolution):>7}  {str(fps):>4}  {vcodec:>10}  {acodec:>10}  {filesize_str:>10}"
        )


def print_metadata(info: dict) -> None:
    title = info.get("title", "Unknown Title")
    uploader = info.get("uploader") or info.get("channel")
    duration = info.get("duration")
    view_count = info.get("view_count")
    webpage_url = info.get("webpage_url")

    print(f"Title     : {title}")
    if uploader:
        print(f"Uploader  : {uploader}")
    if duration:
        minutes, seconds = divmod(duration, 60)
        print(f"Duration  : {minutes}m{seconds:02d}s")
    if view_count is not None:
        print(f"Views     : {view_count}")
    if webpage_url:
        print(f"URL       : {webpage_url}")


def require_dependency() -> None:
    if YoutubeDL is None:
        print(
            "Error: yt-dlp is not installed. Install it with 'pip install yt-dlp'.",
            file=sys.stderr,
        )
        sys.exit(1)


def run(config: DownloadConfig) -> int:
    require_dependency()

    opts = make_ydl_opts(config)
    with YoutubeDL(opts) as ydl:
        try:
            info = fetch_info(ydl, config.url)
        except DownloadError as err:
            print(f"Failed to retrieve info: {err}", file=sys.stderr)
            return 2

        try:
            display_info = first_entry(info)
        except ValueError as err:
            print(f"{err}", file=sys.stderr)
            return 4

        if config.list_formats:
            print_formats(display_info)
            return 0

        if config.metadata_only:
            print_metadata(display_info)
            return 0

        try:
            ydl.download([config.url])
        except DownloadError as err:
            print(f"Download failed: {err}", file=sys.stderr)
            return 3

    return 0


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    config = build_config(args)
    return run(config)


if __name__ == "__main__":
    sys.exit(main())
