import pytest

import yt_ts_extract as pkg
from yt_ts_extract.extractor import YouTubeTranscriptExtractor


def test_convenience_get_transcript(monkeypatch):
    fake_segments = [{"text": "a", "start": 0.0, "duration": 1.0}]

    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)

    out = pkg.get_transcript("https://youtu.be/vidid", language="en")
    assert out == fake_segments


def test_convenience_get_transcript_text(monkeypatch):
    def fake_get_transcript_text(self, url, language="en"):
        return "joined text"

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript_text", fake_get_transcript_text)

    out = pkg.get_transcript_text("https://youtu.be/vidid", language="en")
    assert out == "joined text"


def test_convenience_get_available_languages(monkeypatch):
    langs = [
        {"code": "en", "name": "English", "auto_generated": False},
        {"code": "es", "name": "Spanish", "auto_generated": True},
    ]

    def fake_get_available_languages(self, url):
        return langs

    monkeypatch.setattr(
        YouTubeTranscriptExtractor,
        "get_available_languages",
        fake_get_available_languages,
    )

    out = pkg.get_available_languages("https://youtu.be/vidid")
    assert out == langs
