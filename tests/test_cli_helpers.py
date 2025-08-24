import types

from yt_ts_extract.cli import format_segments, format_stats


class DummyExtractor:
    def _format_timestamp(self, seconds: float) -> str:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"


def test_format_segments(sample_transcript):
    extractor = DummyExtractor()
    out = format_segments(sample_transcript, extractor)
    lines = out.splitlines()
    assert len(lines) == len(sample_transcript)
    # Each line begins with [MM:SS]
    assert lines[0].startswith("[00:01]")
    assert sample_transcript[0]["text"] in lines[0]


class Args:
    pass


def test_format_stats(sample_transcript):
    args = Args()
    text = format_stats(sample_transcript, args)
    assert text.startswith("=== TRANSCRIPT STATISTICS ===")
    # Contains some known keys formatted
    assert "Segment Count:" in text
    assert "Duration Formatted:" in text
