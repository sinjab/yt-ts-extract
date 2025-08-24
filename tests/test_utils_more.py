import os
import re

import pytest

from yt_ts_extract import utils


def test_export_to_srt_millisecond_formatting(tmp_path):
    transcript = [
        {"text": "edge", "start": 0.123, "duration": 0.888},
    ]
    out_file = tmp_path / "edge.srt"
    srt = utils.export_to_srt(transcript, str(out_file))
    # Expect HH:MM:SS,mmm with proper millis rounding/truncation
    assert re.search(r"00:00:00,123\s+-->\s+00:00:01,011", srt)


def test_clean_transcript_text_punctuation_spacing():
    raw = "What  is  this ?yes!no ?  maybe!  [Laughter]"
    cleaned = utils.clean_transcript_text(raw)
    # No laughter tag
    assert "Laughter" not in cleaned
    # No spaces before punctuation, one after sentence punctuation when followed by lowercase
    assert "?y" not in cleaned
    assert "? y" in cleaned or "? Y" in cleaned
    assert "!n" not in cleaned


def test_search_transcript_context_and_multiword():
    transcript = [
        {
            "text": "alpha beta gamma delta epsilon zeta eta",
            "start": 5.0,
            "duration": 2.0,
        },
    ]
    matches = utils.search_transcript(transcript, "beta gamma", context_words=2)
    assert matches and "beta" in matches[0]["text"]


def test_create_summary_with_short_sentences():
    transcript = [
        {
            "text": "Hi. Short sentence here. Another one appears.",
            "start": 0.0,
            "duration": 3.0,
        }
    ]
    summary = utils.create_summary(transcript, max_sentences=1)
    assert isinstance(summary, str) and summary.endswith(".")


def test_get_transcript_stats_empty_and_truncation():
    assert utils.get_transcript_stats([]) == {}

    # Long text to test truncations
    txt = "words " * 100
    transcript = [{"text": txt, "start": 0.0, "duration": 10.0}]
    stats = utils.get_transcript_stats(transcript)
    assert stats["first_words"].endswith("...")
    assert stats["longest_segment"].endswith("...")
