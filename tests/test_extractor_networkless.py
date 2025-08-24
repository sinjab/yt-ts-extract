import types
import pytest
import requests

from yt_ts_extract.extractor import YouTubeTranscriptExtractor


class DummyResp:
    def __init__(self, text="", status_ok=True, headers=None, encoding="utf-8"):
        self.text = text
        self._ok = status_ok
        self.headers = headers or {"Content-Type": "application/json"}
        self.encoding = encoding

    def raise_for_status(self):
        if not self._ok:
            raise requests.HTTPError("bad status")

    def json(self):
        import json as _json

        return _json.loads(self.text)


def test_get_transcript_with_timestamps(monkeypatch):
    e = YouTubeTranscriptExtractor()

    fake_segments = [
        {"text": "one", "start": 0.0, "duration": 1.0},
        {"text": "two", "start": 61.0, "duration": 1.0},
    ]

    def fake_get_transcript(self, url, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
    out = e.get_transcript_with_timestamps("https://youtu.be/x", "en")
    lines = out.splitlines()
    assert lines[0].startswith("[00:00]") and "one" in lines[0]
    assert lines[1].startswith("[01:01]") and "two" in lines[1]


def test_get_video_html_raises_on_request_exception(monkeypatch):
    e = YouTubeTranscriptExtractor()

    class Sess:
        def get(self, url, timeout):
            raise requests.RequestException("boom")

    e.session = Sess()
    with pytest.raises(Exception) as ei:
        e.get_video_html("abc123def45")
    assert "Failed to fetch video page" in str(ei.value)


def test_fetch_transcript_xml_raises(monkeypatch):
    e = YouTubeTranscriptExtractor()

    class Sess:
        def get(self, url, timeout):
            raise requests.RequestException("boom")

    e.session = Sess()
    with pytest.raises(Exception) as ei:
        e.fetch_transcript_xml("http://example")
    assert "Failed to fetch transcript XML" in str(ei.value)


def test_call_innertube_api_empty_response(monkeypatch):
    e = YouTubeTranscriptExtractor()

    def fake_post(url, json, headers, timeout):
        return DummyResp(text="")

    monkeypatch.setattr("yt_ts_extract.extractor.requests.post", fake_post)
    with pytest.raises(Exception) as ei:
        e.call_innertube_api("abc123def45", "KEY")
    assert "Empty response" in str(ei.value)


def test_call_innertube_api_invalid_json(monkeypatch):
    e = YouTubeTranscriptExtractor()

    def fake_post(url, json, headers, timeout):
        return DummyResp(text="not-json")

    monkeypatch.setattr("yt_ts_extract.extractor.requests.post", fake_post)
    with pytest.raises(Exception) as ei:
        e.call_innertube_api("abc123def45", "KEY")
    assert "Invalid JSON" in str(ei.value)
