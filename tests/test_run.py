import video_downloader_cli as cli


def make_config(**overrides):
    base = dict(
        url="https://example.com/watch?v=123",
        outtmpl="%(title)s.%(ext)s",
        fmt="bestvideo*+bestaudio/best",
        quiet=False,
        audio_only=False,
        audio_format="mp3",
        keep_video=False,
        playlist=False,
        proxy=None,
        retries=3,
        metadata_only=False,
        list_formats=False,
    )
    base.update(overrides)
    return cli.DownloadConfig(**base)


def test_run_downloads_video(monkeypatch):
    record = {}

    class DummyYDL:
        def __init__(self, opts):
            record["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def download(self, urls):
            record["download_called_with"] = urls

    monkeypatch.setattr(cli, "YoutubeDL", DummyYDL)
    monkeypatch.setattr(cli, "fetch_info", lambda ydl, url: {"id": "123"})
    monkeypatch.setattr(cli, "first_entry", lambda info: info)

    config = make_config()
    exit_code = cli.run(config)

    assert exit_code == 0
    assert record["download_called_with"] == [config.url]
    assert record["opts"]["format"] == config.fmt
    assert record["opts"]["noplaylist"] is True


def test_run_lists_formats(monkeypatch):
    record = {"download_called": False, "print_formats_called": False}

    class DummyYDL:
        def __init__(self, opts):
            record["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def download(self, urls):
            record["download_called"] = True

    def fake_print_formats(info):
        record["print_formats_called"] = True
        assert info["id"] == "fmt123"

    monkeypatch.setattr(cli, "YoutubeDL", DummyYDL)
    monkeypatch.setattr(cli, "fetch_info", lambda ydl, url: {"id": "fmt123"})
    monkeypatch.setattr(cli, "first_entry", lambda info: info)
    monkeypatch.setattr(cli, "print_formats", fake_print_formats)

    config = make_config(list_formats=True)
    exit_code = cli.run(config)

    assert exit_code == 0
    assert record["print_formats_called"] is True
    assert record["download_called"] is False


def test_run_prints_metadata(monkeypatch):
    record = {"download_called": False, "print_metadata_called": False}

    class DummyYDL:
        def __init__(self, opts):
            record["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def download(self, urls):
            record["download_called"] = True

    def fake_print_metadata(info):
        record["print_metadata_called"] = True
        assert info["title"] == "Sample"

    monkeypatch.setattr(cli, "YoutubeDL", DummyYDL)
    monkeypatch.setattr(cli, "fetch_info", lambda ydl, url: {"title": "Sample"})
    monkeypatch.setattr(cli, "first_entry", lambda info: info)
    monkeypatch.setattr(cli, "print_metadata", fake_print_metadata)

    config = make_config(metadata_only=True)
    exit_code = cli.run(config)

    assert exit_code == 0
    assert record["print_metadata_called"] is True
    assert record["download_called"] is False


def test_run_returns_fetch_failure(monkeypatch):
    record = {}

    class DummyYDL:
        def __init__(self, opts):
            record["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def raising_fetch_info(ydl, url):
        raise cli.DownloadError("network down")

    monkeypatch.setattr(cli, "YoutubeDL", DummyYDL)
    monkeypatch.setattr(cli, "fetch_info", raising_fetch_info)

    config = make_config()
    exit_code = cli.run(config)

    assert exit_code == 2


def test_run_handles_empty_playlist(monkeypatch):
    record = {}

    class DummyYDL:
        def __init__(self, opts):
            record["opts"] = opts

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def download(self, urls):
            record["download_called"] = True

    playlist_info = {"_type": "playlist", "entries": [None, None]}

    monkeypatch.setattr(cli, "YoutubeDL", DummyYDL)
    monkeypatch.setattr(cli, "fetch_info", lambda ydl, url: playlist_info)

    config = make_config(playlist=True)
    exit_code = cli.run(config)

    assert exit_code == 4
    assert "download_called" not in record
