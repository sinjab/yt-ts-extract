import pytest

from yt_ts_extract.extractor import YouTubeTranscriptExtractor


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00"),
        (9, "00:09"),
        (61, "01:01"),
        (3600 + 62, "01:01:02"),
    ],
)
def test_format_timestamp(seconds, expected):
    e = YouTubeTranscriptExtractor()
    assert e._format_timestamp(seconds) == expected


def test_parse_xml_transcript_text_elements():
    e = YouTubeTranscriptExtractor()
    xml = (
        "<transcript>"
        "<text start=\"0.0\" dur=\"2.5\">Hello &amp; world</text>"
        "<text start=\"2.5\" dur=\"2.5\">Again <b>there</b></text>"
        "</transcript>"
    )
    segments = e.parse_xml_transcript(xml)
    assert len(segments) == 2
    assert segments[0]["text"] == "Hello & world"
    assert pytest.approx(segments[1]["end"], 0.001) == 5.0


def test_parse_xml_transcript_p_elements_with_s_children():
    e = YouTubeTranscriptExtractor()
    xml = (
        "<timedtext><body>"
        "<p t=\"1000\" d=\"2000\"><s>Hi</s><s>there</s></p>"
        "<p t=\"4000\" d=\"1000\">Single node</p>"
        "</body></timedtext>"
    )
    segments = e.parse_xml_transcript(xml)
    assert len(segments) == 2
    assert segments[0]["start"] == 1.0
    assert segments[0]["text"] == "Hi there"
    assert segments[1]["text"].startswith("Single node")


def test_select_best_track_manual_prefers_manual():
    tracks = [
        {"languageCode": "en", "kind": "asr", "baseUrl": "auto"},
        {"languageCode": "en", "baseUrl": "manual"},
    ]
    e = YouTubeTranscriptExtractor()
    chosen = e._select_best_track(tracks, "en", prefer_manual=True)
    assert chosen["baseUrl"] == "manual"


def test_select_best_track_fallback_when_language_missing():
    tracks = [
        {"languageCode": "es", "baseUrl": "first"},
        {"languageCode": "fr", "baseUrl": "second"},
    ]
    e = YouTubeTranscriptExtractor()
    chosen = e._select_best_track(tracks, "en", prefer_manual=True)
    assert chosen is tracks[0]


def test_get_transcript_text_joins_without_network(monkeypatch):
    e = YouTubeTranscriptExtractor()

    fake_segments = [
        {"text": "one", "start": 0.0, "duration": 1.0},
        {"text": "two", "start": 1.0, "duration": 1.0},
    ]

    def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
        return fake_segments

    monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
    text = e.get_transcript_text("abc123def45", "en")
    assert text == "one two"
