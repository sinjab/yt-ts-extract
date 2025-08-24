import sys
import io
import types

import pytest

from yt_ts_extract.cli import main
from yt_ts_extract.extractor import YouTubeTranscriptExtractor


@pytest.fixture
def fake_segments():
    return [
        {"text": "alpha", "start": 0.0, "duration": 1.0},
        {"text": "beta", "start": 1.2, "duration": 2.0},
    ]


def run_cli(argv):
    old_argv = sys.argv
    sys.argv = ["yt-transcript", *argv]
    try:
        main()
    except SystemExit as e:
        # CLI may sys.exit; swallow for test
        if e.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv


def test_cli_text_output(monkeypatch, capsys, fake_segments):
    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    run_cli(["--verbose", "--clean", "https://youtu.be/vid"])  # default format text
    out = capsys.readouterr().out.lower()
    assert "alpha" in out and "beta" in out


def test_cli_segments_output(monkeypatch, capsys, fake_segments):
    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    run_cli(["-f", "segments", "https://youtu.be/vid"])  # timestamped lines
    out = capsys.readouterr().out
    assert "[00:00] alpha" in out


def test_cli_stats_output(monkeypatch, capsys, fake_segments):
    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    run_cli(["-f", "stats", "https://youtu.be/vid"])  # stats view
    out = capsys.readouterr().out
    assert out.startswith("=== TRANSCRIPT STATISTICS ===")


def test_cli_list_languages(monkeypatch, capsys):
    def fake_get_available_languages(self, url):
        return [
            {"code": "en", "name": "English", "auto_generated": False},
            {"code": "es", "name": "Español", "auto_generated": True},
        ]

    monkeypatch.setattr(
        YouTubeTranscriptExtractor,
        "get_available_languages",
        fake_get_available_languages,
    )

    run_cli(["--list-languages", "https://youtu.be/vid"])  # language listing
    out = capsys.readouterr().out
    assert "en: English" in out and "es: Español" in out
