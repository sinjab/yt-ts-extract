import pytest
from unittest.mock import Mock, patch
from yt_ts_extract.extractor import YouTubeTranscriptExtractor


class TestYouTubeTranscriptExtractorProxy:
    """Test proxy functionality in YouTubeTranscriptExtractor"""

    def test_init_without_proxy(self):
        """Test extractor initialization without proxy"""
        extractor = YouTubeTranscriptExtractor()
        assert extractor.session.proxies == {}

    def test_init_with_proxy(self):
        """Test extractor initialization with proxy"""
        proxy_url = "http://user:pass@host:port"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        expected_proxies = {"http": proxy_url, "https": proxy_url}
        assert extractor.session.proxies == expected_proxies

    def test_init_with_proxy_no_auth(self):
        """Test extractor initialization with proxy without authentication"""
        proxy_url = "http://host:port"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        expected_proxies = {"http": proxy_url, "https": proxy_url}
        assert extractor.session.proxies == expected_proxies

    def test_init_with_proxy_https(self):
        """Test extractor initialization with HTTPS proxy"""
        proxy_url = "https://user:pass@secure-host:8443"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        expected_proxies = {"http": proxy_url, "https": proxy_url}
        assert extractor.session.proxies == expected_proxies

    def test_init_with_proxy_socks(self):
        """Test extractor initialization with SOCKS proxy"""
        proxy_url = "socks5://user:pass@host:1080"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        expected_proxies = {"http": proxy_url, "https": proxy_url}
        assert extractor.session.proxies == expected_proxies

    def test_proxy_logging(self, caplog):
        """Test that proxy configuration is logged"""
        proxy_url = "http://user:pass@host:port"
        with caplog.at_level("INFO"):
            extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        # Check that proxy is logged (without credentials for security)
        assert "Configured single proxy: host:port" in caplog.text

    def test_proxy_logging_no_auth(self, caplog):
        """Test that proxy configuration is logged without auth"""
        proxy_url = "http://host:port"
        with caplog.at_level("INFO"):
            extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        # Check that proxy is logged
        assert "Configured single proxy: http://host:port" in caplog.text

    def test_proxy_preserved_in_session(self):
        """Test that proxy configuration is preserved in the session"""
        proxy_url = "http://user:pass@host:port"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        # Verify the session has the proxy configured
        assert extractor.session.proxies["http"] == proxy_url
        assert extractor.session.proxies["https"] == proxy_url

        # Verify the session object is the same
        session = extractor.session
        assert session.proxies["http"] == proxy_url
        assert session.proxies["https"] == proxy_url

    def test_proxy_with_other_options(self):
        """Test that proxy works with other extractor options"""
        proxy_url = "http://user:pass@host:port"
        extractor = YouTubeTranscriptExtractor(
            timeout=60, max_retries=5, backoff_factor=1.0, min_delay=3.0, proxy=proxy_url
        )

        # Verify all options are set correctly
        assert extractor.timeout == 60.0
        assert extractor.max_retries == 5
        assert extractor.backoff_factor == 1.0
        assert extractor.min_delay == 3.0
        assert extractor.session.proxies["http"] == proxy_url
        assert extractor.session.proxies["https"] == proxy_url


class TestProxyIntegration:
    """Test proxy integration with actual requests"""

    @patch("requests.Session.get")
    def test_proxy_used_in_requests(self, mock_get):
        """Test that proxy is actually used in HTTP requests"""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = "Mock HTML content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        proxy_url = "http://user:pass@host:port"
        extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

        # Make a request
        extractor.get_video_html("dQw4w9WgXcQ")

        # Verify the request was made with the session (which has proxy configured)
        mock_get.assert_called_once()
        # The session should use the configured proxy automatically
        assert extractor.session.proxies["http"] == proxy_url
        assert extractor.session.proxies["https"] == proxy_url
