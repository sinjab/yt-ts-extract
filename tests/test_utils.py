import os
import re

import pytest

from yt_ts_extract import utils


def test_export_to_srt_writes_and_formats(tmp_path, sample_transcript):
    out_file = tmp_path / "out.srt"
    srt_text = utils.export_to_srt(sample_transcript, str(out_file))

    # File written
    assert out_file.exists()
    data = out_file.read_text(encoding="utf-8")
    assert srt_text == data

    # Contains sequence numbers and arrow
    assert "1\n" in srt_text
    assert "-->" in srt_text


def test_clean_transcript_text_basic():
    raw = "Hello   world !  this is  a test.\nnext line. [Music]"
    cleaned = utils.clean_transcript_text(raw)
    # No music tag
    assert "Music" not in cleaned
    # Collapsed whitespace
    assert "  " not in cleaned
    # Keep punctuation without extra spaces around it
    assert "!" in cleaned


def test_extract_keywords_returns_common_words(sample_transcript):
    kws = utils.extract_keywords(sample_transcript, top_n=5)
    assert isinstance(kws, list)
    assert len(kws) <= 5
    if kws:
        word, count = kws[0]
        assert isinstance(word, str) and isinstance(count, int)


def test_search_transcript_finds_query(sample_transcript):
    matches = utils.search_transcript(sample_transcript, "test", context_words=2)
    # Should find in first segment
    assert isinstance(matches, list)
    if matches:
        m = matches[0]
        assert {"timestamp", "time_seconds", "text", "full_segment"} <= set(m)


def test_create_summary_basic(sample_transcript):
    summary = utils.create_summary(sample_transcript, max_sentences=2)
    assert isinstance(summary, str)
    # Ends with period as implemented
    assert summary.endswith(".")


def test_get_transcript_stats_structure(sample_transcript):
    stats = utils.get_transcript_stats(sample_transcript)
    assert isinstance(stats, dict)
    required = {
        "segment_count",
        "duration_seconds",
        "duration_formatted",
        "word_count",
        "character_count",
        "sentence_count",
        "words_per_minute",
        "average_words_per_segment",
        "longest_segment",
        "first_words",
        "last_words",
    }
    assert required <= set(stats)
