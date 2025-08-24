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
    # Prepare ID list file
    ids_file = tmp_path / "ids.txt"
    ids_file.write_text(
        "# comment\nvid1\nvid2\n",
        encoding="utf-8",
    )

    # Stub extractor methods to avoid network and produce deterministic outputs
    def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
        return [
            {"text": f"text for {video_id}", "start": 0.0, "duration": 1.0},
        ]

    def fake_format_timestamp(self, seconds):
        return "00:00"

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
    monkeypatch.setattr(YouTubeTranscriptExtractor, "_format_timestamp", fake_format_timestamp)

    out_dir = tmp_path / "out"
    run_cli(["--batch", str(ids_file), "--output-dir", str(out_dir)])

    out = capsys.readouterr().out
    assert "Processing 2 video IDs..." in out
    # Files created by batch utils: _segments.txt, _text.txt, .srt
    assert (out_dir / "vid1_segments.txt").exists()
    assert (out_dir / "vid1_text.txt").exists()
    assert (out_dir / "vid1.srt").exists()
    assert (out_dir / "vid2_segments.txt").exists()
    assert (out_dir / "vid2_text.txt").exists()
    assert (out_dir / "vid2.srt").exists()
