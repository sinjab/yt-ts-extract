# YouTube Transcript Extractor

A comprehensive Python implementation for extracting YouTube video transcripts using the Innertube API approach, designed to handle YouTube's 2024-2025 anti-bot systems.

## Features

- **No API key required** - Uses YouTube's internal Innertube API
- **Anti-bot protection** - Mimics legitimate browser requests with proper headers
- **Rate limiting** - Prevents IP blocking through intelligent request spacing (2+ seconds)
- **Multiple transcript formats** - Segments, plain text, timestamped, SRT subtitles
- **Language selection** - Extract transcripts in different languages with auto-detection
- **Comprehensive utilities** - Search, summarize, extract keywords, batch processing
- **CLI interface** - Easy command-line usage with multiple output options
- **Robust error handling** - Handles IP blocks, missing transcripts, invalid URLs

## Project Structure

```
youtube-transcript-extractor/
├── main.py              # Core transcript extractor class
├── examples.py          # Usage examples and demonstrations
├── utils.py             # Utility functions (SRT export, search, etc.)
├── cli.py               # Command-line interface
├── README.md            # This documentation
├── PROJECT_SUMMARY.md   # Detailed project summary
└── pyproject.toml       # Project configuration
```

## Installation

This project uses `uv` for dependency management. If you don't have `uv` installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and setup the project:

```bash
git clone <repository-url>
cd youtube-transcript-extractor
uv sync  # Install dependencies
```

## Quick Start

### Command Line Usage (Recommended)

```bash
# Extract basic transcript
uv run python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Save as SRT subtitles
uv run python cli.py -f srt -o video.srt "https://youtu.be/VIDEO_ID"

# Get transcript statistics
uv run python cli.py -f stats "https://www.youtube.com/watch?v=VIDEO_ID"

# Extract with summary and keywords
uv run python cli.py --summary 3 --keywords 10 "https://www.youtube.com/watch?v=VIDEO_ID"

# Search transcript content
uv run python cli.py --search "artificial intelligence" "https://www.youtube.com/watch?v=VIDEO_ID"

# List available languages
uv run python cli.py --list-languages "https://www.youtube.com/watch?v=VIDEO_ID"

# Batch process multiple videos
echo "https://www.youtube.com/watch?v=VIDEO1" > urls.txt
echo "https://www.youtube.com/watch?v=VIDEO2" >> urls.txt
uv run python cli.py --batch urls.txt --output-dir transcripts/

# Show all CLI examples
uv run python cli.py --examples
```

### Python API Usage

```python
from main import YouTubeTranscriptExtractor

# Initialize extractor
extractor = YouTubeTranscriptExtractor()

# Extract transcript segments
transcript = extractor.get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
for segment in transcript[:5]:
    print(f"[{segment['start']:.1f}s] {segment['text']}")

# Get plain text
text = extractor.get_transcript_text("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(text[:200] + "...")

# Get timestamped format
timestamped = extractor.get_transcript_with_timestamps("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(timestamped[:300] + "...")

# Check available languages
languages = extractor.get_available_languages("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print("Available languages:", languages)
```

### Utility Functions

```python
from utils import export_to_srt, extract_keywords, search_transcript, create_summary

# Export to SRT format
transcript = extractor.get_transcript(url)
srt_content = export_to_srt(transcript, "subtitles.srt")

# Extract keywords
keywords = extract_keywords(transcript, top_n=15)
print("Top keywords:", [word for word, count in keywords])

# Search transcript
matches = search_transcript(transcript, "machine learning", context_words=10)
for match in matches:
    print(f"[{match['timestamp']}] {match['text']}")

# Create summary
summary = create_summary(transcript, max_sentences=3)
print("Summary:", summary)

# Get comprehensive stats
from utils import get_transcript_stats
stats = get_transcript_stats(transcript)
print(f"Duration: {stats['duration_formatted']}")
print(f"Words: {stats['word_count']}, Speaking rate: {stats['words_per_minute']} WPM")
```

## Advanced Usage

### Batch Processing

Create a file with URLs (one per line):

```txt
# urls.txt
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/another_video_id
https://www.youtube.com/watch?v=yet_another_video

# Lines starting with # are comments and ignored
```

Then process all URLs:

```bash
uv run python cli.py --batch urls.txt --output-dir my_transcripts/
```

This creates multiple files for each video:
- `VIDEO_ID_segments.txt` - Timestamped segments
- `VIDEO_ID_text.txt` - Clean plain text
- `VIDEO_ID.srt` - SRT subtitle file

### Custom Processing Pipeline

```python
from main import YouTubeTranscriptExtractor
from utils import clean_transcript_text, extract_keywords, create_summary

def process_video(url):
    extractor = YouTubeTranscriptExtractor()
    
    # Extract transcript
    transcript = extractor.get_transcript(url)
    text = extractor.get_transcript_text(url)
    
    # Process content
    clean_text = clean_transcript_text(text)
    keywords = extract_keywords(transcript, 20)
    summary = create_summary(transcript, 5)
    
    # Return processed data
    return {
        'transcript': transcript,
        'clean_text': clean_text,
        'keywords': keywords,
        'summary': summary,
        'video_id': extractor.extract_video_id(url)
    }

# Use the pipeline
result = process_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

## CLI Reference

### Output Formats

```bash
-f text      # Plain text (default)
-f segments  # Timestamped segments
-f srt       # SRT subtitle format
-f stats     # Detailed statistics
```

### Content Processing

```bash
--clean              # Remove artifacts and improve formatting
--summary N          # Create N-sentence summary
--keywords N         # Extract top N keywords
--search "term"      # Search for specific text
--list-languages     # Show available languages
```

### Batch Operations

```bash
--batch file.txt         # Process URLs from file
--output-dir folder/     # Output directory for batch processing
```

## Examples and Demonstrations

Run comprehensive examples:

```bash
# Run all example scenarios
uv run python examples.py

# Run utility function demos
uv run python utils.py

# Show CLI examples
uv run python cli.py --examples
```

## API Reference

### YouTubeTranscriptExtractor Class

#### Methods

- `get_transcript(url, language_code=None)` → List[Dict]
  - Returns transcript segments with start time, duration, and text
- `get_transcript_text(url, language_code=None)` → str
  - Returns transcript as plain text
- `get_transcript_with_timestamps(url, language_code=None)` → str
  - Returns transcript with formatted timestamps
- `get_available_languages(url)` → Dict[str, str]
  - Returns available language codes and names
- `extract_video_id(url)` → str
  - Extracts video ID from various YouTube URL formats

#### Transcript Segment Format

```python
{
    'start': 15.5,           # Start time in seconds (float)
    'duration': 2.84,        # Duration in seconds (float)
    'text': 'Hello world!'   # Transcript text (string)
}
```

### Utility Functions

- `export_to_srt(transcript, filename)` - Convert to SRT format
- `clean_transcript_text(text)` - Remove artifacts and improve formatting
- `extract_keywords(transcript, top_n)` - Get most common words
- `search_transcript(transcript, query, context_words)` - Search with context
- `create_summary(transcript, max_sentences)` - Extractive summarization
- `get_transcript_stats(transcript)` - Comprehensive statistics
- `batch_process_urls(urls, output_dir)` - Process multiple URLs

## Error Handling

The extractor handles various scenarios:

- **Invalid URLs**: Validates YouTube URL format
- **Missing transcripts**: Clear error message when no transcript available
- **Age restrictions**: Handles age-gated content
- **Language issues**: Falls back to available languages
- **Network problems**: Timeout and connection error handling
- **Anti-bot detection**: Recognizes reCAPTCHA and IP blocks

### Common Issues and Solutions

#### "Could not extract Innertube API key"

This is YouTube's anti-bot protection in action. Solutions:
- Wait longer between requests (increase delay)
- Use a VPN or different IP address
- Try residential proxies for production use
- Implement user-agent rotation

#### Rate Limiting

The extractor includes built-in rate limiting (2+ seconds between requests):
```python
extractor = YouTubeTranscriptExtractor()
extractor.min_delay = 5  # Increase to 5 seconds
```

#### IP Blocking

If you get blocked:
- Change your IP address (VPN)
- Wait several hours before trying again
- Use residential proxies
- Reduce request frequency

## Technical Implementation

### Anti-Bot Protection Features

- **Browser mimicry**: Proper User-Agent and headers
- **Session persistence**: Maintains cookies and session state
- **Rate limiting**: Configurable delays between requests
- **Request signing**: Uses YouTube's internal API properly

### Headers Used

```python
{
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Connection': 'keep-alive',
    # ... additional headers for authenticity
}
```

### XML Parsing

The extractor handles YouTube's XML transcript format:
- Parses timestamps and text content
- Handles HTML entities and special characters
- Supports both manual and auto-generated transcripts

## Dependencies

- **Python**: ≥3.8
- **requests**: ≥2.31.0 for HTTP requests
- **Standard library**: xml.etree.ElementTree, json, re, time, logging

## Development

### Running Tests

```bash
# Test core functionality
uv run python main.py

# Test examples
uv run python examples.py

# Test utilities
uv run python utils.py

# Test CLI
uv run python cli.py --examples
```

### Adding Features

The modular structure makes it easy to add new features:
- Core extraction: Modify `main.py`
- Processing utilities: Add to `utils.py`
- CLI commands: Extend `cli.py`
- Examples: Add to `examples.py`

## Production Considerations

### Scaling and Reliability

For production use, consider:

1. **Proxy rotation** for higher success rates
2. **Request caching** to avoid repeated API calls
3. **Database storage** for transcript persistence
4. **Queue system** for batch processing
5. **Monitoring** for API changes

### Legal and Ethical Usage

- Respect YouTube's Terms of Service
- Use transcripts for legitimate purposes only
- Consider rate limiting impact on YouTube's servers
- Credit original content creators when using transcripts

## Troubleshooting

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

extractor = YouTubeTranscriptExtractor()
```

Or use CLI verbose mode:
```bash
uv run python cli.py -v "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid YouTube URL" | Malformed URL | Check URL format |
| "Could not extract Innertube API key" | Anti-bot protection | Use VPN, increase delays |
| "No transcript found" | Video has no transcript | Try different video |
| "Language not available" | Requested language missing | Check available languages first |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect YouTube's Terms of Service and content creators' rights.

## Support

For issues and questions:
1. Check the troubleshooting guide above
2. Run the examples to verify functionality
3. Review the PROJECT_SUMMARY.md for technical details

---

**Note**: This implementation may occasionally encounter YouTube's anti-bot measures, which is expected behavior. The error handling is designed to gracefully manage these situations and provide clear feedback about what's happening.
