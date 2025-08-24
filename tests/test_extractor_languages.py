import pytest

from yt_ts_extract.extractor import YouTubeTranscriptExtractor


def test_get_available_languages_stubs_innertube(monkeypatch):
    e = YouTubeTranscriptExtractor()

    def fake_get_api_key_from_homepage(self):
        return "FAKE_KEY"

    def fake_call_innertube_api(self, video_id, api_key):
        assert video_id == "fR9ClX0egTc"
        assert api_key == "FAKE_KEY"
        return {
            "playabilityStatus": {"status": "OK"},
            "captions": {
                "playerCaptionsTracklistRenderer": {
                    "captionTracks": [
                        {
                            "languageCode": "en",
                            "name": {"simpleText": "English"},
                            "baseUrl": "http://example/en",
                        },
                        {
                            "languageCode": "es",
                            "name": {"runs": [{"text": "Español"}]},
                            "kind": "asr",
                            "baseUrl": "http://example/es",
                        },
                    ]
                }
            },
        }

    monkeypatch.setattr(
        YouTubeTranscriptExtractor,
        "get_api_key_from_homepage",
        fake_get_api_key_from_homepage,
    )
    monkeypatch.setattr(YouTubeTranscriptExtractor, "call_innertube_api", fake_call_innertube_api)

    langs = e.get_available_languages("fR9ClX0egTc")
    assert langs == [
        {"code": "en", "name": "English", "auto_generated": False},
        {"code": "es", "name": "Español", "auto_generated": True},
    ]
