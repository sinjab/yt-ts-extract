#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Usage Examples
Demonstrates various ways to use the transcript extraction functionality.
"""

import sys
from main import YouTubeTranscriptExtractor


def basic_example():
    """Basic transcript extraction example"""
    print("=" * 60)
    print("BASIC EXAMPLE: Extract transcript segments")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    
    # Test with a well-known video
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley
    print(f"Extracting transcript from: {test_url}")
    
    try:
        transcript = extractor.get_transcript(test_url)
        print(f"\nSuccess! Found {len(transcript)} transcript segments")
        
        # Show first few segments
        print("\nFirst 3 segments:")
        for i, segment in enumerate(transcript[:3]):
            start_time = segment['start']
            duration = segment.get('duration', 'N/A')
            text = segment['text']
            timestamp = extractor._format_timestamp(start_time)
            print(f"  {i+1}. [{timestamp}] ({duration}s) {text}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("This might happen due to rate limiting or video restrictions.")


def plain_text_example():
    """Extract transcript as plain text"""
    print("\n" + "=" * 60)
    print("PLAIN TEXT EXAMPLE: Get full transcript as text")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    
    # Different test video
    test_url = "https://youtu.be/dQw4w9WgXcQ"  # Same video, different format
    print(f"Extracting plain text from: {test_url}")
    
    try:
        text = extractor.get_transcript_text(test_url)
        print(f"\nSuccess! Extracted {len(text)} characters")
        print(f"First 300 characters:\n{text[:300]}...")
        
        # Show some statistics
        words = text.split()
        print(f"\nText statistics:")
        print(f"  - Total characters: {len(text)}")
        print(f"  - Total words: {len(words)}")
        print(f"  - Average word length: {len(text.replace(' ', '')) / len(words):.1f}")
        
    except Exception as e:
        print(f"Error: {e}")


def timestamped_example():
    """Extract transcript with timestamps"""
    print("\n" + "=" * 60)
    print("TIMESTAMPED EXAMPLE: Get transcript with formatted timestamps")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        timestamped_text = extractor.get_transcript_with_timestamps(test_url)
        lines = timestamped_text.split('\n')
        
        print(f"Success! Generated {len(lines)} timestamped lines")
        print("\nFirst 5 lines:")
        for i, line in enumerate(lines[:5]):
            if line.strip():
                print(f"  {line}")
        
        print(f"\nLast 3 lines:")
        for line in lines[-3:]:
            if line.strip():
                print(f"  {line}")
                
    except Exception as e:
        print(f"Error: {e}")


def language_detection_example():
    """Demonstrate language detection and selection"""
    print("\n" + "=" * 60)
    print("LANGUAGE DETECTION EXAMPLE: Check available languages")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        languages = extractor.get_available_languages(test_url)
        print(f"Available languages for this video: {len(languages)}")
        
        for lang_code, lang_name in languages.items():
            print(f"  - {lang_code}: {lang_name}")
            
        # Try to extract with a specific language (if available)
        if languages:
            first_lang = list(languages.keys())[0]
            print(f"\nTrying to extract transcript in '{first_lang}'...")
            transcript = extractor.get_transcript(test_url, language_code=first_lang)
            print(f"Success! Got {len(transcript)} segments in {languages[first_lang]}")
            
    except Exception as e:
        print(f"Error: {e}")


def error_handling_example():
    """Demonstrate error handling with various problematic URLs"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLE: Test with problematic URLs")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    
    # Test various problematic scenarios
    test_cases = [
        ("Invalid URL", "not-a-youtube-url"),
        ("Non-existent video", "https://www.youtube.com/watch?v=invalidvideoid123"),
        ("Valid URL format", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),  # Should work
    ]
    
    for description, url in test_cases:
        print(f"\nTesting {description}: {url}")
        try:
            transcript = extractor.get_transcript(url)
            print(f"  ✅ Success: {len(transcript)} segments found")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def batch_processing_example():
    """Demonstrate processing multiple videos"""
    print("\n" + "=" * 60)
    print("BATCH PROCESSING EXAMPLE: Process multiple videos")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    
    # List of test URLs (using the same one to avoid rate limiting issues in demo)
    video_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",  # Same video, different format
    ]
    
    results = []
    
    for i, url in enumerate(video_urls, 1):
        print(f"\nProcessing video {i}/{len(video_urls)}: {url}")
        try:
            # Get basic info
            video_id = extractor.extract_video_id(url)
            transcript = extractor.get_transcript(url)
            
            result = {
                'url': url,
                'video_id': video_id,
                'segment_count': len(transcript),
                'success': True
            }
            
            # Calculate total duration
            if transcript:
                last_segment = transcript[-1]
                total_duration = last_segment['start'] + last_segment.get('duration', 0)
                result['duration_seconds'] = total_duration
                result['duration_formatted'] = extractor._format_timestamp(total_duration)
            
            print(f"  ✅ Success: {result['segment_count']} segments, duration: {result.get('duration_formatted', 'unknown')}")
            
        except Exception as e:
            result = {
                'url': url,
                'error': str(e),
                'success': False
            }
            print(f"  ❌ Failed: {e}")
        
        results.append(result)
    
    # Summary
    print(f"\nBatch processing summary:")
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"  - Successful: {len(successful)}/{len(results)}")
    print(f"  - Failed: {len(failed)}/{len(results)}")
    
    if successful:
        total_segments = sum(r['segment_count'] for r in successful)
        print(f"  - Total segments extracted: {total_segments}")


def interactive_mode():
    """Interactive mode for testing custom URLs"""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE: Test your own YouTube URLs")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    
    print("Enter YouTube URLs to extract transcripts (type 'quit' to exit):")
    print("Examples:")
    print("  - https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print("  - https://youtu.be/dQw4w9WgXcQ")
    print()
    
    while True:
        try:
            url = input("Enter YouTube URL: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("Exiting interactive mode...")
                break
            
            if not url:
                continue
            
            print(f"Processing: {url}")
            
            # Extract basic info
            video_id = extractor.extract_video_id(url)
            print(f"Video ID: {video_id}")
            
            # Get available languages
            try:
                languages = extractor.get_available_languages(url)
                print(f"Available languages: {list(languages.keys())}")
            except Exception as e:
                print(f"Could not get languages: {e}")
                languages = {}
            
            # Get transcript
            transcript = extractor.get_transcript(url)
            print(f"Transcript segments: {len(transcript)}")
            
            if transcript:
                print(f"\nFirst segment:")
                first = transcript[0]
                timestamp = extractor._format_timestamp(first['start'])
                print(f"  [{timestamp}] {first['text']}")
                
                if len(transcript) > 1:
                    print(f"\nLast segment:")
                    last = transcript[-1]
                    timestamp = extractor._format_timestamp(last['start'])
                    print(f"  [{timestamp}] {last['text']}")
            
            # Offer to show more
            show_more = input("\nShow first 5 segments? (y/n): ").lower().strip()
            if show_more == 'y':
                print("\nFirst 5 segments:")
                for i, segment in enumerate(transcript[:5]):
                    timestamp = extractor._format_timestamp(segment['start'])
                    print(f"  {i+1}. [{timestamp}] {segment['text']}")
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try another URL or type 'quit' to exit.")
            print("-" * 40)


def main():
    """Run all examples"""
    print("YouTube Transcript Extractor - Examples")
    print("=" * 60)
    print("This script demonstrates various usage patterns.")
    print("Note: Examples use rate limiting, so they may take some time.")
    print()
    
    try:
        # Run all examples
        basic_example()
        plain_text_example()
        timestamped_example()
        language_detection_example()
        error_handling_example()
        batch_processing_example()
        
        # Ask if user wants interactive mode
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 60)
        
        interactive = input("\nWould you like to try interactive mode? (y/n): ").lower().strip()
        if interactive == 'y':
            interactive_mode()
        
        print("\nAll examples completed successfully! 🎉")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
