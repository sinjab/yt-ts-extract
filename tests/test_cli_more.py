import sys
import io
import os

import pytest

from yt_ts_extract.cli import main
from yt_ts_extract.extractor import YouTubeTranscriptExtractor


def run_cli(argv):
    old_argv = sys.argv
    sys.argv = ["yt-transcript", *argv]
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv


def test_cli_text_with_summary_keywords_search(monkeypatch, capsys):
    fake_segments = [
        {"text": "alpha beta gamma", "start": 0.0, "duration": 1.5},
        {"text": "beta delta epsilon", "start": 2.0, "duration": 2.0},
    ]

    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    run_cli([
        "--summary",
        "1",
        "--keywords",
        "3",
        "--search",
        "beta",
        "https://youtu.be/vid",
    ])

    out = capsys.readouterr().out
    assert "--- SUMMARY ---" in out
    assert "--- TOP 3 KEYWORDS ---" in out
    assert "--- SEARCH RESULTS FOR 'beta' ---" in out


def test_cli_output_to_file(monkeypatch, tmp_path, capsys):
    fake_segments = [
        {"text": "alpha", "start": 0.0, "duration": 1.0},
    ]

    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    outfile = tmp_path / "out.txt"
    run_cli(["-o", str(outfile), "https://youtu.be/vid"])  # write to file

    out = capsys.readouterr().out
    assert f"Output saved to: {outfile}" in out
    assert outfile.read_text(encoding="utf-8").strip().endswith("alpha")
