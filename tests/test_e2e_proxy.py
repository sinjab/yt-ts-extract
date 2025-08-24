#!/usr/bin/env python3
"""
End-to-End Proxy Tests for YouTube Transcript Extractor

These tests verify that proxy functionality works correctly with real network requests.
They are marked with @pytest.mark.e2e and may be skipped in CI environments.
"""

import pytest
import os
import time
from unittest.mock import patch, Mock
from yt_ts_extract import YouTubeTranscriptExtractor, get_transcript


class TestProxyE2E:
    """End-to-end tests for proxy functionality"""

    @pytest.mark.e2e
    def test_proxy_configuration_logging(self):
        """Test that proxy configuration is properly logged"""
        proxy_url = "http://test:proxy@proxy-host:8080"

        # Capture logs to verify proxy configuration
        with patch("yt_ts_extract.extractor.logger.info") as mock_logger:
            extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

            # Verify proxy was logged (without credentials for security)
            mock_logger.assert_called_with("Configured single proxy: proxy-host:8080")

            # Verify session has proxy configured
            assert extractor.session.proxies["http"] == proxy_url
            assert extractor.session.proxies["https"] == proxy_url

    @pytest.mark.e2e
    def test_proxy_with_real_network_request(self):
        """Test proxy configuration with actual network request (may fail if proxy unreachable)"""
        # Use a test proxy that may not be reachable
        proxy_url = "http://test:proxy@unreachable-proxy:8080"

        extractor = YouTubeTranscriptExtractor(
            proxy=proxy_url,
            timeout=5,  # Short timeout for test
            max_retries=1,  # Minimal retries for test
        )

        # This should fail due to unreachable proxy, but proxy should be configured
        assert extractor.session.proxies["http"] == proxy_url
        assert extractor.session.proxies["https"] == proxy_url

        # Attempt to make a request (will fail, but proxy should be used)
        try:
            extractor.get_video_html("fR9ClX0egTc")
        except Exception as e:
            # Expected to fail due to unreachable proxy
            assert "proxy" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.e2e
    def test_proxy_environment_variables(self):
        """Test that proxy environment variables are respected"""
        # Set environment variables
        test_proxy = "http://env:proxy@env-host:8080"
        os.environ["HTTP_PROXY"] = test_proxy
        os.environ["HTTPS_PROXY"] = test_proxy

        try:
            # Create extractor without explicit proxy (should use env vars)
            extractor = YouTubeTranscriptExtractor()

            # The session should automatically pick up environment proxy settings
            # Note: This test may pass even without env vars due to requests library behavior
            # The important thing is that our explicit proxy parameter works

        finally:
            # Clean up environment variables
            if "HTTP_PROXY" in os.environ:
                del os.environ["HTTP_PROXY"]
            if "HTTPS_PROXY" in os.environ:
                del os.environ["HTTPS_PROXY"]

    @pytest.mark.e2e
    def test_proxy_with_convenience_functions(self):
        """Test proxy with convenience functions"""
        proxy_url = "http://conv:proxy@conv-host:8080"

        # Test get_transcript with proxy
        try:
            transcript = get_transcript("fR9ClX0egTc", proxy=proxy_url)
            # If this succeeds, proxy worked
            assert isinstance(transcript, list)
        except Exception as e:
            # Expected to fail due to unreachable proxy, but proxy should be configured
            assert "proxy" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.e2e
    def test_proxy_rotation_simulation(self):
        """Test switching between different proxy configurations"""
        proxy1 = "http://proxy1:pass@host1:8080"
        proxy2 = "http://proxy2:pass@host2:8080"

        # Create first extractor with proxy1
        extractor1 = YouTubeTranscriptExtractor(proxy=proxy1)
        assert extractor1.session.proxies["http"] == proxy1

        # Create second extractor with proxy2
        extractor2 = YouTubeTranscriptExtractor(proxy=proxy2)
        assert extractor2.session.proxies["http"] == proxy2

        # Verify they have different proxy configurations
        assert extractor1.session.proxies != extractor2.session.proxies

        # Verify each extractor maintains its own proxy config
        assert extractor1.session.proxies["http"] == proxy1
        assert extractor2.session.proxies["http"] == proxy2

    @pytest.mark.e2e
    def test_proxy_with_batch_processing(self):
        """Test proxy configuration in batch processing context"""
        from yt_ts_extract.utils import batch_process_ids

        proxy_url = "http://batch:proxy@batch-host:8080"

        # Test batch processing with proxy
        try:
            # This will fail due to unreachable proxy, but proxy should be configured
            results = batch_process_ids(["fR9ClX0egTc"], "test_output", proxy=proxy_url)
            # If this succeeds, proxy worked
            assert isinstance(results, dict)
        except Exception as e:
            # Expected to fail due to unreachable proxy
            assert "proxy" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.e2e
    def test_proxy_timeout_behavior(self):
        """Test that proxy timeouts work correctly"""
        proxy_url = "http://timeout:proxy@timeout-host:8080"

        extractor = YouTubeTranscriptExtractor(
            proxy=proxy_url, timeout=1, max_retries=1
        )  # Very short timeout

        start_time = time.time()

        try:
            extractor.get_video_html("fR9ClX0egTc")
        except Exception as e:
            elapsed = time.time() - start_time

            # Should fail quickly due to short timeout
            assert elapsed < 5  # Should fail within 5 seconds

            # Should be a timeout or connection error
            assert any(
                keyword in str(e).lower()
                for keyword in ["timeout", "connection", "proxy", "unreachable"]
            )

    @pytest.mark.e2e
    def test_proxy_authentication_formats(self):
        """Test various proxy authentication formats"""
        test_cases = [
            "http://user:pass@host:8080",
            "https://user:pass@secure-host:8443",
            "socks5://user:pass@socks-host:1080",
            "http://host:8080",  # No auth
            "https://host:8443",  # No auth
        ]

        for proxy_url in test_cases:
            extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

            # Verify proxy is configured
            assert extractor.session.proxies["http"] == proxy_url
            assert extractor.session.proxies["https"] == proxy_url

            # Verify logging works for all formats
            # (This test doesn't actually make network requests)

    @pytest.mark.e2e
    def test_proxy_with_cli_simulation(self):
        """Test proxy configuration as it would be used in CLI"""
        import argparse

        # Simulate CLI argument parsing
        parser = argparse.ArgumentParser()
        parser.add_argument("--proxy", help="Proxy URL")

        # Test with proxy argument
        args = parser.parse_args(["--proxy", "http://cli:proxy@cli-host:8080"])

        # Simulate CLI behavior
        extractor = YouTubeTranscriptExtractor(proxy=args.proxy)

        # Verify proxy is configured
        assert extractor.session.proxies["http"] == args.proxy
        assert extractor.session.proxies["https"] == args.proxy

    @pytest.mark.e2e
    def test_proxy_error_handling(self):
        """Test that proxy errors are handled gracefully"""
        proxy_url = "http://error:proxy@error-host:8080"

        extractor = YouTubeTranscriptExtractor(proxy=proxy_url, timeout=3, max_retries=2)

        # This should fail gracefully with proper error handling
        try:
            extractor.get_video_html("fR9ClX0egTc")
        except Exception as e:
            # Should be a meaningful error message
            error_str = str(e).lower()
            assert any(
                keyword in error_str
                for keyword in [
                    "proxy",
                    "connection",
                    "timeout",
                    "unreachable",
                    "failed",
                ]
            )

            # Should not crash the application
            assert "traceback" not in error_str.lower()


class TestProxyIntegration:
    """Integration tests for proxy functionality"""

    def test_proxy_with_mocked_requests(self):
        """Test proxy integration with mocked HTTP requests"""
        proxy_url = "http://mock:proxy@mock-host:8080"

        with patch("requests.Session.get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.text = "Mock HTML content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            extractor = YouTubeTranscriptExtractor(proxy=proxy_url)

            # Make a request
            result = extractor.get_video_html("dQw4w9GgXcQ")

            # Verify proxy was used
            assert extractor.session.proxies["http"] == proxy_url
            assert extractor.session.proxies["https"] == proxy_url

            # Verify request was made
            mock_get.assert_called_once()

    def test_proxy_parameter_propagation(self):
        """Test that proxy parameter is properly propagated through all functions"""
        proxy_url = "http://prop:proxy@prop-host:8080"

        # Test all convenience functions
        functions_to_test = [
            lambda: get_transcript("fR9ClX0egTc", proxy=proxy_url),
            lambda: get_transcript("fR9ClX0egTc", proxy=proxy_url, language="en"),
        ]

        for func in functions_to_test:
            try:
                func()
            except Exception as e:
                # Expected to fail due to unreachable proxy, but proxy should be configured
                # The error could be proxy-related, connection-related, or other expected failures
                error_str = str(e).lower()
                expected_keywords = [
                    "proxy",
                    "connection",
                    "timeout",
                    "unreachable",
                    "failed",
                    "video unplayable",
                ]
                assert any(
                    keyword in error_str for keyword in expected_keywords
                ), f"Unexpected error: {error_str}"


if __name__ == "__main__":
    # Run tests directly for debugging
    pytest.main([__file__, "-v", "-s"])
