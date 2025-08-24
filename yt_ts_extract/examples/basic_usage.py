"""
Basic usage examples for the YouTube Transcript Extractor module
"""

import sys
from ..extractor import YouTubeTranscriptExtractor


def run_basic_examples():
    """Run basic SDK usage examples"""
    print("=" * 60)
    print("BASIC SDK EXAMPLES")
    print("=" * 60)
    
    print("\n1. Basic transcript extraction:")
    print("```python")
    print("from yt_ts_extract import get_transcript")
    print("transcript = get_transcript('https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
    print("print(f'Found {len(transcript)} segments')")
    print("```")
    
    print("\n2. Using the extractor class:")
    print("```python")
    print("from yt_ts_extract import YouTubeTranscriptExtractor")
    print("extractor = YouTubeTranscriptExtractor()")
    print("transcript = extractor.get_transcript(url)")
    print("```")
    
    print("\n3. Getting plain text:")
    print("```python")
    print("from yt_ts_extract import get_transcript_text")
    print("text = get_transcript_text('https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
    print("print(text[:200])  # First 200 characters")
    print("```")


def run_advanced_examples():
    """Run advanced SDK usage examples"""
    print("\n" + "=" * 60)
    print("ADVANCED SDK EXAMPLES")
    print("=" * 60)
    
    print("\n1. Multi-language support:")
    print("```python")
    print("extractor = YouTubeTranscriptExtractor()")
    print("languages = extractor.get_available_languages(url)")
    print("transcript = extractor.get_transcript(url, language='es')  # Spanish")
    print("```")
    
    print("\n2. Export to SRT:")
    print("```python")
    print("from yt_ts_extract.utils import export_to_srt")
    print("transcript = get_transcript(url)")
    print("srt_content = export_to_srt(transcript)")
    print("with open('subtitles.srt', 'w') as f:")
    print("    f.write(srt_content)")
    print("```")
    
    print("\n3. Batch processing:")
    print("```python")
    print("from yt_ts_extract.utils import batch_process_urls")
    print("urls = ['url1', 'url2', 'url3']")
    print("results = batch_process_urls(urls, output_dir='transcripts/')")
    print("```")


def run_live_example():
    """Run a live example with actual video"""
    print("\n" + "=" * 60)
    print("LIVE EXAMPLE: Extract from actual video")
    print("=" * 60)
    
    extractor = YouTubeTranscriptExtractor()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"Extracting transcript from: {test_url}")
        transcript = extractor.get_transcript(test_url)
        
        print(f"✅ Success! Found {len(transcript)} segments")
        
        # Show first few segments
        print("\nFirst 3 segments:")
        for i, segment in enumerate(transcript[:3]):
            timestamp = extractor._format_timestamp(segment['start'])
            print(f"  {i+1}. [{timestamp}] {segment['text']}")
        
        # Show available languages
        languages = extractor.get_available_languages(test_url)
        print(f"\nAvailable languages: {len(languages)}")
        for lang in languages[:5]:  # Show first 5
            status = "(auto)" if lang['auto_generated'] else "(manual)"
            print(f"  - {lang['code']}: {lang['name']} {status}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might happen due to rate limiting or video restrictions.")


def run_all_examples():
    """Run all examples"""
    print("YouTube Transcript Extractor - SDK Examples")
    print("=" * 60)
    
    run_basic_examples()
    run_advanced_examples()
    run_live_example()
    
    print("\n" + "=" * 60)
    print("CLI USAGE EXAMPLES")
    print("=" * 60)
    
    cli_examples = [
        ("Basic extraction", "yt-transcript 'https://www.youtube.com/watch?v=VIDEO_ID'"),
        ("Save as SRT", "yt-transcript -f srt -o video.srt 'URL'"),
        ("Get statistics", "yt-transcript -f stats 'URL'"),
        ("Extract with summary", "yt-transcript --summary 3 'URL'"),
        ("Get keywords", "yt-transcript --keywords 10 'URL'"),
        ("Search content", "yt-transcript --search 'keyword' 'URL'"),
        ("List languages", "yt-transcript --list-languages 'URL'"),
        ("Batch processing", "yt-transcript --batch urls.txt"),
    ]
    
    for description, command in cli_examples:
        print(f"\n{description}:")
        print(f"  {command}")
    
    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
