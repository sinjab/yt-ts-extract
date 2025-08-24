#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Command Line Interface
Simple CLI for easy transcript extraction with various output formats.
"""

import argparse
import sys
import os
from .extractor import YouTubeTranscriptExtractor
from .proxy_manager import ProxyManager
from .utils import (
    export_to_srt,
    clean_transcript_text,
    extract_keywords,
    search_transcript,
    create_summary,
    get_transcript_stats,
    batch_process_ids,
)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract transcripts from YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dQw4w9WgXcQ
  %(prog)s -f srt -o subtitles.srt dQw4w9WgXcQ
  %(prog)s -f stats --keywords 10 dQw4w9WgXcQ
  %(prog)s --search "artificial intelligence" dQw4w9WgXcQ
  %(prog)s --batch ids.txt --output-dir transcripts/
  
🔒 Proxy Examples:
  %(prog)s --proxy "http://user:pass@host:port" dQw4w9WgXcQ
  %(prog)s --proxy "https://host:port" --timeout 60 dQw4w9WgXcQ
  %(prog)s --proxy "socks5://host:port" --retries 5 dQw4w9WgXcQ
  %(prog)s --batch ids.txt --proxy "http://host:port" --output-dir transcripts/
        """,
    )

    # Positional arguments
    parser.add_argument("video_id", nargs="?", help="YouTube video ID (11 characters)")

    # Output format options
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "segments", "srt", "stats"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument(
        "--output-dir",
        default="transcripts/",
        help="Output directory for batch processing",
    )

    # Content options
    parser.add_argument("-l", "--language", help="Language code (e.g., en, es, fr)")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean transcript text (remove artifacts)",
    )
    parser.add_argument(
        "--summary",
        type=int,
        metavar="N",
        help="Create summary with N sentences",
    )
    parser.add_argument("--keywords", type=int, metavar="N", help="Extract top N keywords")
    parser.add_argument("--search", help="Search for specific text in transcript")

    # Batch processing
    parser.add_argument("--batch", help="Process multiple video IDs from file (one per line)")
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available languages for the video",
    )

    # Utility options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--examples", action="store_true", help="Run example demonstrations")

    # Network/resilience options
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Max HTTP retries on failure (default: 3)",
    )
    parser.add_argument(
        "--backoff",
        type=float,
        default=0.75,
        help="Exponential backoff factor (default: 0.75)",
    )
    parser.add_argument(
        "--min-delay",
        dest="min_delay",
        type=float,
        default=2.0,
        help="Minimum delay between requests for rate limiting (default: 2)",
    )
    parser.add_argument(
        "--proxy",
        help='🔒 Proxy URL for network routing (e.g., "http://user:pass@host:port", '
        '"https://host:port", "socks5://host:port")',
    )
    parser.add_argument(
        "--proxy-list",
        help="🔄 Proxy list file for rotation (space/tab separated: Address Port Username Password)",
    )
    parser.add_argument(
        "--rotation-strategy",
        choices=["random", "round_robin", "least_used"],
        default="random",
        help="🔄 Proxy rotation strategy (default: random)",
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="🔄 Perform health check on all proxies before starting",
    )

    args = parser.parse_args()

    # Handle special modes
    if args.examples:
        run_examples()
        return

    if args.batch:
        handle_batch_processing(args)
        return

    if not args.video_id:
        parser.error("VIDEO_ID is required unless using --batch or --examples")

    # Initialize extractor with resilience options
    if args.proxy_list:
        # Proxy rotation mode
        try:
            proxy_manager = ProxyManager.from_file(
                args.proxy_list, rotation_strategy=args.rotation_strategy
            )

            if args.health_check:
                print("Performing proxy health check...")
                health_results = proxy_manager.health_check_all()
                healthy_count = sum(1 for healthy in health_results.values() if healthy)
                print(
                    f"Health check complete: {healthy_count}/{len(proxy_manager)} proxies healthy"
                )

                if healthy_count == 0:
                    print("Warning: No healthy proxies found!")

            extractor = YouTubeTranscriptExtractor(
                timeout=args.timeout,
                max_retries=args.retries,
                backoff_factor=args.backoff,
                min_delay=args.min_delay,
                proxy_manager=proxy_manager,
            )

            # Show proxy stats
            stats = proxy_manager.get_stats()
            print(
                f"🔄 Using proxy rotation: {stats['active_proxies']}/{stats['total_proxies']} "
                f"proxies active, strategy: {stats['rotation_strategy']}"
            )

        except Exception as e:
            print(f"Error loading proxy list: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # Single proxy or no proxy mode
        extractor = YouTubeTranscriptExtractor(
            timeout=args.timeout,
            max_retries=args.retries,
            backoff_factor=args.backoff,
            min_delay=args.min_delay,
            proxy=args.proxy,
        )

    try:
        # List languages if requested
        if args.list_languages:
            print("Available languages:")
            languages = extractor.get_available_languages(args.video_id)
            for lang in languages:
                status = "auto-generated" if lang["auto_generated"] else "manual"
                print(f"  {lang['code']}: {lang['name']} ({status})")
            return

        # Extract transcript
        if args.verbose:
            print(f"Extracting transcript for ID: {args.video_id}")
            if args.language:
                print(f"Language: {args.language}")

        # Use 'en' as default if no language specified
        language = args.language or "en"
        transcript = extractor.get_transcript(args.video_id, language)

        if args.verbose:
            print(f"Successfully extracted {len(transcript)} segments")

        # Process based on format
        if args.format == "segments":
            output = format_segments(transcript, extractor)
        elif args.format == "srt":
            output = export_to_srt(transcript, filename=None)
        elif args.format == "stats":
            output = format_stats(transcript, args)
        else:  # text format
            # Convert existing transcript to text instead of re-extracting
            text_parts = []
            for segment in transcript:
                text_parts.append(segment["text"])
            text = " ".join(text_parts)
            output = clean_transcript_text(text) if args.clean else text

        # Handle additional content requests
        if args.summary:
            summary = create_summary(transcript, args.summary)
            output += f"\n\n--- SUMMARY ---\n{summary}"

        if args.keywords:
            keywords = extract_keywords(transcript, args.keywords)
            keyword_text = "\n".join([f"  {word}: {count}" for word, count in keywords])
            output += f"\n\n--- TOP {args.keywords} KEYWORDS ---\n{keyword_text}"

        if args.search:
            matches = search_transcript(transcript, args.search)
            if matches:
                match_text = "\n".join([f"  [{m['timestamp']}] {m['text']}" for m in matches])
                output += f"\n\n--- SEARCH RESULTS FOR '{args.search}' ---\n{match_text}"
            else:
                output += f"\n\n--- SEARCH RESULTS ---\nNo matches found for '{args.search}'"

        # Output results
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output saved to: {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_segments(transcript, extractor):
    """Format transcript as timestamped segments"""
    lines = []
    for segment in transcript:
        timestamp = extractor._format_timestamp(segment["start"])
        lines.append(f"[{timestamp}] {segment['text']}")
    return "\n".join(lines)


def format_stats(transcript, args):
    """Format transcript statistics"""
    stats = get_transcript_stats(transcript)

    lines = ["=== TRANSCRIPT STATISTICS ==="]
    for key, value in stats.items():
        formatted_key = key.replace("_", " ").title()
        lines.append(f"{formatted_key}: {value}")

    return "\n".join(lines)


def handle_batch_processing(args):
    """Handle batch processing from file"""
    if not os.path.exists(args.batch):
        print(f"Error: File '{args.batch}' not found", file=sys.stderr)
        sys.exit(1)

    # Read video IDs from file
    with open(args.batch, "r") as f:
        ids = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not ids:
        print("Error: No valid video IDs found in file", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(ids)} video IDs...")

    if args.proxy_list:
        # Use proxy rotation for batch processing
        try:
            proxy_manager = ProxyManager.from_file(
                args.proxy_list, rotation_strategy=args.rotation_strategy
            )
            results = batch_process_ids(ids, args.output_dir, proxy_manager=proxy_manager)
        except Exception as e:
            print(
                f"Error loading proxy list for batch processing: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Use single proxy or no proxy
        results = batch_process_ids(ids, args.output_dir, proxy=args.proxy)

    # Print detailed results
    print(f"\nDetailed Results:")
    print(f"Successful: {len(results['successful'])}")
    for result in results["successful"]:
        print(
            f"  ✅ {result['video_id']}: {result['stats']['duration_formatted']}, {result['stats']['word_count']} words"
        )

    print(f"Failed: {len(results['failed'])}")
    for result in results["failed"]:
        print(f"  ❌ {result['video_id']}: {result['error']}")


def run_examples():
    """Run example demonstrations"""
    print("YouTube Transcript Extractor - CLI Examples")
    print("=" * 50)

    examples = [
        ("Basic text extraction", "yt-transcript dQw4w9WgXcQ"),
        ("Save as SRT file", "yt-transcript -f srt -o video.srt dQw4w9WgXcQ"),
        ("Get transcript stats", "yt-transcript -f stats dQw4w9WgXcQ"),
        ("Extract with summary", "yt-transcript --summary 3 dQw4w9WgXcQ"),
        ("Get top keywords", "yt-transcript --keywords 10 dQw4w9WgXcQ"),
        ("Search transcript", 'yt-transcript --search "keyword" dQw4w9WgXcQ'),
        (
            "Clean text output",
            "yt-transcript --clean -o clean.txt dQw4w9WgXcQ",
        ),
        ("List languages", "yt-transcript --list-languages dQw4w9WgXcQ"),
        (
            "Batch processing",
            "yt-transcript --batch ids.txt --output-dir transcripts/",
        ),
        ("Timestamped segments", "yt-transcript -f segments dQw4w9WgXcQ"),
        ("", ""),  # Empty line for separation
        ("🔒 PROXY EXAMPLES:", ""),
        (
            "HTTP proxy with auth",
            'yt-transcript --proxy "http://user:pass@host:port" dQw4w9WgXcQ',
        ),
        (
            "HTTP proxy without auth",
            'yt-transcript --proxy "http://host:port" dQw4w9WgXcQ',
        ),
        (
            "HTTPS proxy",
            'yt-transcript --proxy "https://secure-host:8443" dQw4w9WgXcQ',
        ),
        (
            "SOCKS5 proxy",
            'yt-transcript --proxy "socks5://user:pass@host:1080" dQw4w9WgXcQ',
        ),
        (
            "Proxy with custom timeout",
            'yt-transcript --proxy "http://host:port" --timeout 60 dQw4w9WgXcQ',
        ),
        (
            "Proxy with retries",
            'yt-transcript --proxy "http://host:port" --retries 5 dQw4w9WgXcQ',
        ),
        (
            "Batch processing with proxy",
            'yt-transcript --batch ids.txt --proxy "http://host:port" --output-dir transcripts/',
        ),
        (
            "Proxy with all options",
            'yt-transcript --proxy "http://user:pass@host:port" --timeout 60 --retries 5 --min-delay 1.0 dQw4w9WgXcQ',
        ),
        ("", ""),  # Empty line for separation
        ("🔄 PROXY ROTATION EXAMPLES:", ""),
        (
            "Proxy list file",
            "yt-transcript --proxy-list proxies.txt dQw4w9WgXcQ",
        ),
        (
            "Proxy rotation with strategy",
            "yt-transcript --proxy-list proxies.txt --rotation-strategy round_robin dQw4w9WgXcQ",
        ),
        (
            "Proxy rotation with health check",
            "yt-transcript --proxy-list proxies.txt --health-check dQw4w9WgXcQ",
        ),
        (
            "Batch with proxy rotation",
            "yt-transcript --batch ids.txt --proxy-list proxies.txt --output-dir transcripts/",
        ),
    ]

    for description, command in examples:
        if description == "" and command == "":
            print()  # Empty line
        elif description.startswith("🔒"):
            print(f"\n{description}")
        else:
            print(f"\n{description}:")
            print(f"  {command}")

    print(f"\n{'=' * 50}")
    print("Create a file 'ids.txt' with YouTube video IDs (one per line) for batch processing.")
    print("Example ids.txt content:")
    print("  dQw4w9WgXcQ")
    print("  9bZkp7q19f0")
    print("  # This is a comment - lines starting with # are ignored")
    print(f"\n{'=' * 50}")
    print("🔒 PROXY USAGE TIPS:")
    print("• Use HTTPS proxies when possible for security")
    print("• Set appropriate timeouts for proxy connections")
    print("• Increase retry count for proxy connections")
    print("• Test proxy connectivity before batch processing")
    print("• Use authentication for corporate proxies")


if __name__ == "__main__":
    main()
