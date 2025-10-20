# Repository Guidelines

## Project Structure & Module Organization
- `video_downloader_cli.py` houses the CLI, configuration dataclass, argument parsing, and yt-dlp integration. Keep CLI helpers cohesive and prefer expanding existing functions (`parse_args`, `make_ydl_opts`) before creating new modules.
- `requirements.txt` lists runtime dependencies; pin versions and note optional tools in-line. Expand documentation in `README.md`, introducing a `docs/` folder only if usage guides outgrow the main file.

## Build, Test, and Development Commands
- `python -m pip install -r requirements.txt` installs yt-dlp and supporting libraries; use a virtual environment to keep the workspace clean.
- `python video_downloader_cli.py --help` verifies argument wiring and prints current options after code changes.
- `python video_downloader_cli.py "<url>" --list-formats` exercises metadata fetching without downloading; treat it as a quick smoke test.
- `python video_downloader_cli.py "<url>" --audio-only --audio-format mp3` is the reference flow for validating post-processing and ffmpeg usage.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and line length <= 88 characters; preserve the existing type hints and dataclass patterns.
- Use descriptive `snake_case` for functions and variables, reserving `CamelCase` for future classes or dataclasses.
- Format code with `python -m black video_downloader_cli.py` and lint with `python -m ruff check .` before sending changes.

## Testing Guidelines
- Prefer `pytest` for new coverage; store tests in `tests/`, mirroring CLI entry points (e.g., `tests/test_parse_args.py`).
- Mock `YoutubeDL` to cover option building, retries, and error handling without invoking the network.
- Run `python -m pytest` locally and document any manual CLI checks performed for complex scenarios.

## Commit & Pull Request Guidelines
- Use short, imperative commit subjects (e.g., `Add quiet flag validation`) and expand on behavioral changes in the body when needed.
- Summaries should note why the change matters, what commands were run, and any new flags or configuration expectations. Link issues when available and attach terminal output or screenshots for user-facing updates.
