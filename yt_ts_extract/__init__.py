"""
YouTube Transcript Extractor (yt_ts_extract)

A robust Python library for extracting YouTube video transcripts with multi-language support
and various output formats.

Usage:
    # SDK/API Usage
    from yt_ts_extract import YouTubeTranscriptExtractor

    extractor = YouTubeTranscriptExtractor()
    transcript = extractor.get_transcript("VIDEO_ID")

    # CLI Usage
    $ yt-transcript VIDEO_ID
    $ yt-transcript -f srt -o subtitles.srt VIDEO_ID

Features:
    - Extract transcripts from YouTube videos via video ID
    - Support for 26+ languages
    - Multiple output formats: plain text, SRT subtitles, timestamped segments, JSON
    - Batch processing for multiple videos
    - Command-line interface and Python library
    - Robust anti-bot protection bypass
"""

__version__ = "1.0.0"
__author__ = "YouTube Transcript Extractor Team"
__email__ = "support@yt-ts-extract.com"
__description__ = "YouTube transcript extraction with multi-language support"

# Main API exports
from .extractor import YouTubeTranscriptExtractor
from .proxy_manager import ProxyManager, ProxyConfig
from .utils import (
    export_to_srt,
    clean_transcript_text,
    extract_keywords,
    search_transcript,
    create_summary,
    get_transcript_stats,
    batch_process_ids,
)
from typing import Optional


# Convenience functions for common use cases
def get_transcript(
    video_id: str,
    language: str = "en",
    proxy: Optional[str] = None,
    **extractor_options,
) -> list:
    """
    Quick function to get transcript segments.

    Args:
        video_id: YouTube video ID
        language: Language code (default: 'en')
        proxy: Proxy URL in format "http://username:password@host:port" or "http://host:port" (default: None)

    Returns:
        List of transcript segments

    Example:
        transcript = get_transcript("fR9ClX0egTc")
        transcript = get_transcript("fR9ClX0egTc", proxy="http://user:pass@host:port")
    """
    extractor = YouTubeTranscriptExtractor(proxy=proxy, **extractor_options)
    return extractor.get_transcript(video_id, language)


def get_transcript_text(
    video_id: str,
    language: str = "en",
    proxy: Optional[str] = None,
    **extractor_options,
) -> str:
    """
    Quick function to get transcript as plain text.

    Args:
        video_id: YouTube video ID
        language: Language code (default: 'en')
        proxy: Proxy URL in format "http://username:password@host:port" or "http://host:port" (default: None)

    Returns:
        Transcript as a single string

    Example:
        text = get_transcript_text("fR9ClX0egTc")
        text = get_transcript_text("fR9ClX0egTc", proxy="http://user:pass@host:port")
    """
    extractor = YouTubeTranscriptExtractor(proxy=proxy, **extractor_options)
    return extractor.get_transcript_text(video_id, language)


def get_available_languages(
    video_id: str, proxy: Optional[str] = None, **extractor_options
) -> list:
    """
    Quick function to get available transcript languages.

    Args:
        video_id: YouTube video ID
        proxy: Proxy URL in format "http://username:password@host:port" or "http://host:port" (default: None)

    Returns:
        List of available language dictionaries

    Example:
        languages = get_available_languages("fR9ClX0egTc")
        for lang in languages:
            print(f"{lang['name']} ({lang['code']})")

        languages = get_available_languages("fR9ClX0egTc", proxy="http://user:pass@host:port")
    """
    extractor = YouTubeTranscriptExtractor(proxy=proxy, **extractor_options)
    return extractor.get_available_languages(video_id)


def get_transcript_with_proxy_rotation(
    video_id: str,
    proxy_list_file: str,
    language: str = "en",
    rotation_strategy: str = "random",
    **extractor_options,
) -> list:
    """
    Quick function to get transcript using proxy rotation.

    Args:
        video_id: YouTube video ID
        proxy_list_file: Path to proxy list file
        language: Language code (default: 'en')
        rotation_strategy: Proxy rotation strategy (default: 'random')

    Returns:
        List of transcript segments

    Example:
        transcript = get_transcript_with_proxy_rotation("fR9ClX0egTc", "proxies.txt")
        transcript = get_transcript_with_proxy_rotation("fR9ClX0egTc", "proxies.txt", rotation_strategy="round_robin")
    """
    proxy_manager = ProxyManager.from_file(proxy_list_file, rotation_strategy=rotation_strategy)
    extractor = YouTubeTranscriptExtractor(proxy_manager=proxy_manager, **extractor_options)
    return extractor.get_transcript(video_id, language)


def get_transcript_text_with_proxy_rotation(
    video_id: str,
    proxy_list_file: str,
    language: str = "en",
    rotation_strategy: str = "random",
    **extractor_options,
) -> str:
    """
    Quick function to get transcript as plain text using proxy rotation.

    Args:
        video_id: YouTube video ID
        proxy_list_file: Path to proxy list file
        language: Language code (default: 'en')
        rotation_strategy: Proxy rotation strategy (default: 'random')

    Returns:
        Transcript as a single string

    Example:
        text = get_transcript_text_with_proxy_rotation("fR9ClX0egTc", "proxies.txt")
        text = get_transcript_text_with_proxy_rotation("fR9ClX0egTc", "proxies.txt", rotation_strategy="round_robin")
    """
    proxy_manager = ProxyManager.from_file(proxy_list_file, rotation_strategy=rotation_strategy)
    extractor = YouTubeTranscriptExtractor(proxy_manager=proxy_manager, **extractor_options)
    return extractor.get_transcript_text(video_id, language)


# Module metadata
__all__ = [
    # Main class
    "YouTubeTranscriptExtractor",
    # Proxy management
    "ProxyManager",
    "ProxyConfig",
    # Utility functions
    "export_to_srt",
    "clean_transcript_text",
    "extract_keywords",
    "search_transcript",
    "create_summary",
    "get_transcript_stats",
    "batch_process_ids",
    # Convenience functions
    "get_transcript",
    "get_transcript_text",
    "get_available_languages",
    "get_transcript_with_proxy_rotation",
    "get_transcript_text_with_proxy_rotation",
]
