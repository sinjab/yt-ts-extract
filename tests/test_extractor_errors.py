import pytest

from yt_ts_extract.extractor import YouTubeTranscriptExtractor


def test_extract_caption_tracks_login_required():
    e = YouTubeTranscriptExtractor()
    with pytest.raises(Exception) as ei:
        e.extract_caption_tracks({"playabilityStatus": {"status": "LOGIN_REQUIRED"}})
    assert "requires login" in str(ei.value)


def test_extract_caption_tracks_unplayable():
    e = YouTubeTranscriptExtractor()
    with pytest.raises(Exception) as ei:
        e.extract_caption_tracks({"playabilityStatus": {"status": "UNPLAYABLE"}})
    assert "unplayable" in str(ei.value).lower()


def test_extract_caption_tracks_unknown_status():
    e = YouTubeTranscriptExtractor()
    with pytest.raises(Exception) as ei:
        e.extract_caption_tracks({"playabilityStatus": {"status": "SOMETHING"}})
    assert "unplayable" in str(ei.value).lower()


def test_extract_caption_tracks_no_tracks():
    e = YouTubeTranscriptExtractor()
    data = {
        "playabilityStatus": {"status": "OK"},
        "captions": {"playerCaptionsTracklistRenderer": {"captionTracks": []}},
    }
    with pytest.raises(Exception) as ei:
        e.extract_caption_tracks(data)
    assert "No transcripts available" in str(ei.value)


def test_parse_xml_transcript_malformed():
    e = YouTubeTranscriptExtractor()
    with pytest.raises(Exception) as ei:
        e.parse_xml_transcript("<not-closed>")
    assert "Failed to parse transcript XML" in str(ei.value)
