#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Command Line Interface
Simple CLI for easy transcript extraction with various output formats.
"""

import argparse
import sys
import os
from main import YouTubeTranscriptExtractor
from utils import (
    export_to_srt, clean_transcript_text, extract_keywords, 
    search_transcript, create_summary, get_transcript_stats, batch_process_urls
)


def main():
    parser = argparse.ArgumentParser(
        description="Extract transcripts from YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s -f srt -o subtitles.srt "https://youtu.be/dQw4w9WgXcQ"
  %(prog)s -f stats --keywords 10 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s --search "artificial intelligence" "https://www.youtube.com/watch?v=VIDEO_ID"
  %(prog)s --batch urls.txt --output-dir transcripts/
        """
    )
    
    # Positional arguments
    parser.add_argument('url', nargs='?', help='YouTube video URL')
    
    # Output format options
    parser.add_argument('-f', '--format', choices=['text', 'segments', 'srt', 'stats'], 
                        default='text', help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('--output-dir', default='transcripts/', 
                        help='Output directory for batch processing')
    
    # Content options
    parser.add_argument('-l', '--language', help='Language code (e.g., en, es, fr)')
    parser.add_argument('--clean', action='store_true', 
                        help='Clean transcript text (remove artifacts)')
    parser.add_argument('--summary', type=int, metavar='N', 
                        help='Create summary with N sentences')
    parser.add_argument('--keywords', type=int, metavar='N', 
                        help='Extract top N keywords')
    parser.add_argument('--search', help='Search for specific text in transcript')
    
    # Batch processing
    parser.add_argument('--batch', help='Process multiple URLs from file (one per line)')
    parser.add_argument('--list-languages', action='store_true',
                        help='List available languages for the video')
    
    # Utility options
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Enable verbose output')
    parser.add_argument('--examples', action='store_true',
                        help='Run example demonstrations')
    
    args = parser.parse_args()
    
    # Handle special modes
    if args.examples:
        run_examples()
        return
    
    if args.batch:
        handle_batch_processing(args)
        return
    
    if not args.url:
        parser.error("URL is required unless using --batch or --examples")
    
    # Initialize extractor
    extractor = YouTubeTranscriptExtractor()
    
    try:
        # List languages if requested
        if args.list_languages:
            print("Available languages:")
            languages = extractor.get_available_languages(args.url)
            for lang in languages:
                status = "auto-generated" if lang['auto_generated'] else "manual"
                print(f"  {lang['code']}: {lang['name']} ({status})")
            return
        
        # Extract transcript
        if args.verbose:
            print(f"Extracting transcript from: {args.url}")
            if args.language:
                print(f"Language: {args.language}")
        
        # Use 'en' as default if no language specified
        language = args.language or 'en'
        transcript = extractor.get_transcript(args.url, language)
        
        if args.verbose:
            print(f"Successfully extracted {len(transcript)} segments")
        
        # Process based on format
        if args.format == 'segments':
            output = format_segments(transcript, extractor)
        elif args.format == 'srt':
            output = export_to_srt(transcript, filename=None)
        elif args.format == 'stats':
            output = format_stats(transcript, args)
        else:  # text format
            text = extractor.get_transcript_text(args.url, language)
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
            with open(args.output, 'w', encoding='utf-8') as f:
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
        timestamp = extractor._format_timestamp(segment['start'])
        lines.append(f"[{timestamp}] {segment['text']}")
    return "\n".join(lines)


def format_stats(transcript, args):
    """Format transcript statistics"""
    stats = get_transcript_stats(transcript)
    
    lines = ["=== TRANSCRIPT STATISTICS ==="]
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        lines.append(f"{formatted_key}: {value}")
    
    return "\n".join(lines)


def handle_batch_processing(args):
    """Handle batch processing from file"""
    if not os.path.exists(args.batch):
        print(f"Error: File '{args.batch}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read URLs from file
    with open(args.batch, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("Error: No valid URLs found in file", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(urls)} URLs...")
    results = batch_process_urls(urls, args.output_dir)
    
    # Print detailed results
    print(f"\nDetailed Results:")
    print(f"Successful: {len(results['successful'])}")
    for result in results['successful']:
        print(f"  ✅ {result['video_id']}: {result['stats']['duration_formatted']}, {result['stats']['word_count']} words")
    
    print(f"Failed: {len(results['failed'])}")
    for result in results['failed']:
        print(f"  ❌ {result['url']}: {result['error']}")


def run_examples():
    """Run example demonstrations"""
    print("YouTube Transcript Extractor - CLI Examples")
    print("=" * 50)
    
    examples = [
        ("Basic text extraction", 'python cli.py "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Save as SRT file", 'python cli.py -f srt -o video.srt "https://youtu.be/VIDEO_ID"'),
        ("Get transcript stats", 'python cli.py -f stats "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Extract with summary", 'python cli.py --summary 3 "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Get top keywords", 'python cli.py --keywords 10 "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Search transcript", 'python cli.py --search "keyword" "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Clean text output", 'python cli.py --clean -o clean.txt "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("List languages", 'python cli.py --list-languages "https://www.youtube.com/watch?v=VIDEO_ID"'),
        ("Batch processing", 'python cli.py --batch urls.txt --output-dir transcripts/'),
        ("Timestamped segments", 'python cli.py -f segments "https://www.youtube.com/watch?v=VIDEO_ID"'),
    ]
    
    for description, command in examples:
        print(f"\n{description}:")
        print(f"  {command}")
    
    print(f"\n{'='*50}")
    print("Create a file 'urls.txt' with YouTube URLs (one per line) for batch processing.")
    print("Example urls.txt content:")
    print("  https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print("  https://youtu.be/another_video_id")
    print("  # This is a comment - lines starting with # are ignored")


if __name__ == "__main__":
    main()
