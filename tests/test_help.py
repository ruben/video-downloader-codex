import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_help_option_succeeds():
    result = subprocess.run(
        [sys.executable, str(ROOT / "video_downloader_cli.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "optional arguments" in result.stdout
    assert "--output" in result.stdout
    assert "Examples:" in result.stdout
    assert "--list-formats" in result.stdout
