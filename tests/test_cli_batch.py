import sys
from pathlib import Path

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


def test_cli_batch_processing(monkeypatch, tmp_path, capsys):
    # Prepare URL list file
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text(
        "# comment\nhttps://youtu.be/vid1\nhttps://www.youtube.com/watch?v=vid2\n",
        encoding="utf-8",
    )

    # Stub extractor methods to avoid network and produce deterministic outputs
    def fake_extract_video_id(self, url):
        return "vid1" if "vid1" in url else "vid2"

    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return [
            {"text": f"text for {url}", "start": 0.0, "duration": 1.0},
        ]

    def fake_format_timestamp(self, seconds):
        return "00:00"

    monkeypatch.setattr(YouTubeTranscriptExtractor, "extract_video_id", fake_extract_video_id)
    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
    monkeypatch.setattr(YouTubeTranscriptExtractor, "_format_timestamp", fake_format_timestamp)

    out_dir = tmp_path / "out"
    run_cli(["--batch", str(urls_file), "--output-dir", str(out_dir)])

    out = capsys.readouterr().out
    assert "Processing 2 URLs..." in out
    # Files created by batch utils: _segments.txt, _text.txt, .srt
    assert (out_dir / "vid1_segments.txt").exists()
    assert (out_dir / "vid1_text.txt").exists()
    assert (out_dir / "vid1.srt").exists()
    assert (out_dir / "vid2_segments.txt").exists()
    assert (out_dir / "vid2_text.txt").exists()
    assert (out_dir / "vid2.srt").exists()
