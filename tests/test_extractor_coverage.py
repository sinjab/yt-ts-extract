import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import requests

from yt_ts_extract.extractor import YouTubeTranscriptExtractor


class TestExtractorCoverage:
    """Test cases to improve extractor coverage"""
    
    def test_get_video_html_recaptcha_block(self):
        """Test handling of reCAPTCHA blocks"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = '<html><body>recaptcha</body></html>'
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception, match="IP blocked \\(reCAPTCHA\\)"):
                extractor.get_video_html("test123")
    
    def test_get_video_html_request_exception(self):
        """Test handling of request exceptions"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")
            
            with pytest.raises(Exception, match="Failed to fetch video page"):
                extractor.get_video_html("test123")
    
    def test_call_innertube_api_empty_response(self):
        """Test handling of empty API response"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.text = ""
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception, match="Empty response from Innertube API"):
                extractor.call_innertube_api("test123", "fake_key")
    
    def test_call_innertube_api_json_decode_error(self):
        """Test handling of JSON decode errors"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.text = "invalid json"
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.encoding = 'utf-8'
            mock_post.return_value = mock_response
            
            # Mock the json() method to raise JSONDecodeError
            mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "invalid json", 0)
            
            with pytest.raises(Exception, match="Invalid JSON response from Innertube API"):
                extractor.call_innertube_api("test123", "fake_key")
    
    def test_call_innertube_api_request_exception(self):
        """Test handling of request exceptions in API call"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.RequestException("Network error")
            
            with pytest.raises(Exception, match="Failed to call Innertube API"):
                extractor.call_innertube_api("test123", "fake_key")
    
    def test_select_best_track_fallback_to_first(self):
        """Test track selection fallback when language not found"""
        extractor = YouTubeTranscriptExtractor()
        
        tracks = [
            {"languageCode": "es", "name": "Spanish"},
            {"languageCode": "fr", "name": "French"}
        ]
        
        # Request English but only Spanish and French available
        result = extractor._select_best_track(tracks, "en", prefer_manual=False)
        
        # Should fallback to first available track
        assert result == tracks[0]
    
    def test_select_best_track_no_tracks_available(self):
        """Test track selection when no tracks available"""
        extractor = YouTubeTranscriptExtractor()
        
        tracks = []
        result = extractor._select_best_track(tracks, "en", prefer_manual=False)
        
        assert result is None
    
    def test_select_best_track_prefer_manual(self):
        """Test track selection with manual preference"""
        extractor = YouTubeTranscriptExtractor()
        
        tracks = [
            {"languageCode": "en", "kind": "asr", "name": "Auto English"},
            {"languageCode": "en", "kind": "manual", "name": "Manual English"}
        ]
        
        result = extractor._select_best_track(tracks, "en", prefer_manual=True)
        
        # Should prefer manual over auto-generated
        assert result["kind"] == "manual"
    
    def test_select_best_track_prefer_manual_no_manual_available(self):
        """Test track selection with manual preference but no manual tracks"""
        extractor = YouTubeTranscriptExtractor()
        
        tracks = [
            {"languageCode": "en", "kind": "asr", "name": "Auto English"}
        ]
        
        result = extractor._select_best_track(tracks, "en", prefer_manual=True)
        
        # Should fallback to auto-generated when no manual available
        assert result["kind"] == "asr"
    
    def test_get_transcript_text(self):
        """Test getting transcript as text"""
        extractor = YouTubeTranscriptExtractor()
        
        fake_segments = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "world", "start": 1.0, "duration": 1.0}
        ]
        
        with patch.object(extractor, 'get_transcript', return_value=fake_segments):
            result = extractor.get_transcript_text("test123")
            
        assert result == "Hello world"
    
    def test_get_transcript_with_timestamps(self):
        """Test getting transcript with timestamps"""
        extractor = YouTubeTranscriptExtractor()
        
        fake_segments = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "world", "start": 1.0, "duration": 1.0}
        ]
        
        with patch.object(extractor, 'get_transcript', return_value=fake_segments):
            with patch.object(extractor, '_format_timestamp', return_value="00:00"):
                result = extractor.get_transcript_with_timestamps("test123")
                
        assert result == "[00:00] Hello\n[00:00] world"
    
    def test_format_timestamp_seconds(self):
        """Test timestamp formatting for seconds"""
        extractor = YouTubeTranscriptExtractor()
        
        result = extractor._format_timestamp(45.5)
        assert result == "00:45"
    
    def test_format_timestamp_minutes(self):
        """Test timestamp formatting for minutes"""
        extractor = YouTubeTranscriptExtractor()
        
        result = extractor._format_timestamp(125.5)
        assert result == "02:05"
    
    def test_format_timestamp_hours(self):
        """Test timestamp formatting for hours"""
        extractor = YouTubeTranscriptExtractor()
        
        result = extractor._format_timestamp(3661.5)
        assert result == "01:01:01"
    
    def test_format_timestamp_zero(self):
        """Test timestamp formatting for zero"""
        extractor = YouTubeTranscriptExtractor()
        
        result = extractor._format_timestamp(0.0)
        assert result == "00:00"
    
    def test_get_transcript_track_name_extraction(self):
        """Test track name extraction in get_transcript"""
        extractor = YouTubeTranscriptExtractor()
        
        # Mock the entire transcript extraction process
        with patch.object(extractor, 'get_api_key_from_homepage', return_value="fake_key"):
            with patch.object(extractor, 'call_innertube_api') as mock_api:
                mock_api.return_value = {"some": "data"}
                
                with patch.object(extractor, 'extract_caption_tracks') as mock_tracks:
                    mock_tracks.return_value = [
                        {
                            "languageCode": "en",
                            "name": {"runs": [{"text": "English"}]},
                            "baseUrl": "http://example.com"
                        }
                    ]
                    
                    with patch.object(extractor, '_select_best_track') as mock_select:
                        mock_select.return_value = {
                            "languageCode": "en",
                            "name": {"runs": [{"text": "English"}]},
                            "baseUrl": "http://example.com"
                        }
                        
                        with patch.object(extractor, 'fetch_transcript_xml') as mock_fetch:
                            mock_fetch.return_value = "<xml>content</xml>"
                            
                            with patch.object(extractor, 'parse_xml_transcript') as mock_parse:
                                mock_parse.return_value = [{"text": "test", "start": 0.0, "duration": 1.0}]
                                
                                result = extractor.get_transcript("test123")
                                
                                assert len(result) == 1
                                assert result[0]["text"] == "test"
    
    def test_get_transcript_track_name_simple_text(self):
        """Test track name extraction with simpleText format"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch.object(extractor, 'get_api_key_from_homepage', return_value="fake_key"):
            with patch.object(extractor, 'call_innertube_api') as mock_api:
                mock_api.return_value = {"some": "data"}
                
                with patch.object(extractor, 'extract_caption_tracks') as mock_tracks:
                    mock_tracks.return_value = [
                        {
                            "languageCode": "en",
                            "name": {"simpleText": "English"},
                            "baseUrl": "http://example.com"
                        }
                    ]
                    
                    with patch.object(extractor, '_select_best_track') as mock_select:
                        mock_select.return_value = {
                            "languageCode": "en",
                            "name": {"simpleText": "English"},
                            "baseUrl": "http://example.com"
                        }
                        
                        with patch.object(extractor, 'fetch_transcript_xml') as mock_fetch:
                            mock_fetch.return_value = "<xml>content</xml>"
                            
                            with patch.object(extractor, 'parse_xml_transcript') as mock_parse:
                                mock_parse.return_value = [{"text": "hola", "start": 0.0, "duration": 1.0}]
                                
                                result = extractor.get_transcript("test123")
                                
                                assert len(result) == 1
                                assert result[0]["text"] == "hola"
    
    def test_get_transcript_no_track_available(self):
        """Test get_transcript when no track is available"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch.object(extractor, 'get_api_key_from_homepage', return_value="fake_key"):
            with patch.object(extractor, 'call_innertube_api') as mock_api:
                mock_api.return_value = {"some": "data"}
                
                with patch.object(extractor, 'extract_caption_tracks') as mock_tracks:
                    mock_tracks.return_value = [
                        {"languageCode": "es", "name": "Spanish"}
                    ]
                    
                    with patch.object(extractor, '_select_best_track') as mock_select:
                        mock_select.return_value = None
                        
                        with pytest.raises(Exception, match="No transcript available for language 'en'"):
                            extractor.get_transcript("test123", language="en")
    
    def test_get_transcript_exception_handling(self):
        """Test exception handling in get_transcript"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch.object(extractor, 'get_api_key_from_homepage') as mock_key:
            mock_key.side_effect = Exception("API key error")
            
            with pytest.raises(Exception, match="API key error"):
                extractor.get_transcript("test123")
    
    def test_rate_limiting_delay(self):
        """Test rate limiting functionality"""
        extractor = YouTubeTranscriptExtractor()
        extractor.min_delay = 0.1
        
        # First call should not delay
        start_time = extractor.last_request_time
        extractor._wait_if_needed()
        
        # Second call within delay period should wait
        with patch('time.sleep') as mock_sleep:
            extractor._wait_if_needed()
            mock_sleep.assert_called_once()
    
    def test_rate_limiting_no_delay_needed(self):
        """Test rate limiting when no delay is needed"""
        extractor = YouTubeTranscriptExtractor()
        extractor.min_delay = 0.1
        
        # Wait for delay period to pass
        import time
        time.sleep(0.2)
        
        with patch('time.sleep') as mock_sleep:
            extractor._wait_if_needed()
            mock_sleep.assert_not_called()


class TestExtractorErrorCoverage:
    """Test error handling scenarios for better coverage"""
    
    def test_get_transcript_language_fallback(self):
        """Test language fallback behavior"""
        extractor = YouTubeTranscriptExtractor()
        
        with patch.object(extractor, 'get_api_key_from_homepage', return_value="fake_key"):
            with patch.object(extractor, 'call_innertube_api') as mock_api:
                mock_api.return_value = {"some": "data"}
                
                with patch.object(extractor, 'extract_caption_tracks') as mock_tracks:
                    mock_tracks.return_value = [
                        {"languageCode": "en", "name": "English", "baseUrl": "http://example.com"}
                    ]
                    
                    with patch.object(extractor, '_select_best_track') as mock_select:
                        mock_select.return_value = {
                            "languageCode": "en", "name": "English", "baseUrl": "http://example.com"
                        }
                        
                        with patch.object(extractor, 'fetch_transcript_xml') as mock_fetch:
                            mock_fetch.return_value = "<xml>content</xml>"
                            
                            with patch.object(extractor, 'parse_xml_transcript') as mock_parse:
                                mock_parse.return_value = [{"text": "hello", "start": 0.0, "duration": 1.0}]
                                
                                # This should work with English
                                result = extractor.get_transcript("test123", language="en")
                                
                                assert len(result) == 1
                                assert result[0]["text"] == "hello"
