#!/usr/bin/env python3
"""
Proxy Usage Examples for YouTube Transcript Extractor

This example demonstrates how to use proxies with the YouTube transcript extractor
for network routing, bypassing geo-restrictions, or using corporate networks.
"""

from yt_ts_extract import (
    YouTubeTranscriptExtractor,
    get_transcript,
    get_transcript_text,
    get_available_languages,
)


def demonstrate_proxy_usage():
    """Demonstrate various proxy usage patterns"""

    print("YouTube Transcript Extractor - Proxy Usage Examples")
    print("=" * 60)

    # Example 1: HTTP proxy with authentication
    print("\n1. HTTP Proxy with Authentication:")
    print("   proxy = 'http://username:password@proxy-host:8080'")

    try:
        extractor = YouTubeTranscriptExtractor(
            proxy="http://username:password@proxy-host:8080", timeout=30, max_retries=3
        )
        print("   ✅ Extractor configured with authenticated proxy")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Example 2: HTTP proxy without authentication
    print("\n2. HTTP Proxy without Authentication:")
    print("   proxy = 'http://proxy-host:8080'")

    try:
        extractor = YouTubeTranscriptExtractor(proxy="http://proxy-host:8080", timeout=30)
        print("   ✅ Extractor configured with unauthenticated proxy")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Example 3: HTTPS proxy
    print("\n3. HTTPS Proxy:")
    print("   proxy = 'https://secure-proxy:8443'")

    try:
        extractor = YouTubeTranscriptExtractor(proxy="https://secure-proxy:8443")
        print("   ✅ Extractor configured with HTTPS proxy")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Example 4: SOCKS5 proxy
    print("\n4. SOCKS5 Proxy:")
    print("   proxy = 'socks5://user:pass@proxy-host:1080'")

    try:
        extractor = YouTubeTranscriptExtractor(proxy="socks5://user:pass@proxy-host:1080")
        print("   ✅ Extractor configured with SOCKS5 proxy")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Example 5: Convenience functions with proxy
    print("\n5. Convenience Functions with Proxy:")
    print("   Using get_transcript() with proxy")

    try:
        # This won't actually make a request since we're using a fake proxy
        transcript = get_transcript("dQw4w9WgXcQ", proxy="http://fake-proxy:8080")
        print("   ✅ Convenience function configured with proxy")
    except Exception as e:
        print(f"   ❌ Error (expected with fake proxy): {e}")

    # Example 6: Batch processing with proxy
    print("\n6. Batch Processing with Proxy:")
    print("   Using batch_process_ids() with proxy")

    try:
        from yt_ts_extract.utils import batch_process_ids

        # This would process multiple videos through the proxy
        # results = batch_process_ids(
        #     ["dQw4w9WgXcQ", "9bZkp7q19f0"],
        #     "transcripts/",
        #     proxy="http://proxy-host:8080"
        # )
        print("   ✅ Batch processing function supports proxy parameter")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def proxy_environment_variables():
    """Show how to use environment variables for proxy configuration"""

    print("\n" + "=" * 60)
    print("Proxy Configuration via Environment Variables")
    print("=" * 60)

    print("\nYou can also configure proxies using environment variables:")
    print("export HTTP_PROXY=http://user:pass@proxy:8080")
    print("export HTTPS_PROXY=http://user:pass@proxy:8080")
    print("export NO_PROXY=localhost,127.0.0.1")

    print("\nThen use the extractor normally:")
    print("extractor = YouTubeTranscriptExtractor()  # Will use env vars")


def proxy_best_practices():
    """Show proxy usage best practices"""

    print("\n" + "=" * 60)
    print("Proxy Usage Best Practices")
    print("=" * 60)

    practices = [
        "Always use HTTPS proxies when possible for security",
        "Set appropriate timeouts when using proxies (--timeout 60)",
        "Increase retry count for proxy connections (--retries 5)",
        "Use authentication for corporate proxies",
        "Test proxy connectivity before batch processing",
        "Consider proxy rotation for high-volume usage",
        "Monitor proxy performance and switch if needed",
    ]

    for i, practice in enumerate(practices, 1):
        print(f"{i}. {practice}")


def main():
    """Main function to run all examples"""
    demonstrate_proxy_usage()
    proxy_environment_variables()
    proxy_best_practices()

    print("\n" + "=" * 60)
    print("Note: These examples show configuration, not actual network requests.")
    print("Replace proxy URLs with your actual proxy server details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
