# YouTube Transcript Extractor

## Project Status: ✅ Complete & Operational

A robust Python tool for extracting YouTube video transcripts with multi-language support and various output formats.

## Key Features

**Core Functionality**
- Extract transcripts from YouTube videos via URL
- Support for 26+ languages (English, Spanish, French, German, Japanese, Arabic, Chinese, etc.)
- Multiple output formats: plain text, SRT subtitles, timestamped segments, JSON
- Batch processing for multiple videos
- Command-line interface and Python library

**Technical Highlights**
- Android client implementation bypasses anti-bot measures
- Dual XML parser handles both legacy and current YouTube formats
- Robust API key extraction with fallback system
- Built-in rate limiting prevents IP blocking
- Comprehensive error handling

## Installation & Usage

```bash
# Navigate to project directory
cd /Users/khs/Documents/projects/yt_ts_extract

# Basic transcript extraction
uv run python cli.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Export as SRT subtitles
uv run python cli.py -f srt -o subtitles.srt "VIDEO_URL"

# List available languages
uv run python cli.py --list-languages "VIDEO_URL"

# Run examples
uv run python examples.py
```

## Project Structure

```
├── main.py              # Core extractor (451 lines)
├── cli.py               # Command line interface (224 lines)
├── utils.py             # Utility functions (440 lines)
├── examples.py          # Demo scripts (321 lines)
├── README.md            # Documentation
└── pyproject.toml       # Dependencies
```

## Testing Results

**Test Video 1**: Physics lecture (`wIwCTQZ_xFE`)
- 377 transcript segments extracted
- 26 language tracks available
- Complete lecture content captured

**Test Video 2**: Music video (`dQw4w9WgXcQ`)
- 61 transcript segments extracted
- 6 language tracks available
- Perfect SRT format export

## Technical Architecture

**Android Client Approach**
```python
headers = {
    'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14)',
    'X-YouTube-Client-Name': '3',
    'X-YouTube-Client-Version': '20.10.38',
}
```

**Dual XML Format Support**
- Legacy format: `<text start="160" dur="2800">content</text>`
- Current format: `<p t="160" d="2800"><s>content</s></p>`

## Advanced Features

- **Multi-language detection**: Automatic discovery of available caption tracks
- **Format flexibility**: Text, SRT, timestamped, JSON output options
- **Search functionality**: Find specific content within transcripts
- **Analytics**: Word count, duration, keyword extraction
- **Batch processing**: Handle multiple videos simultaneously

## Success Metrics

| Feature | Target | Achieved | Status |
|---------|--------|----------|---------|
| Transcript extraction | Working | ✅ 377 segments | Complete |
| Language support | Multiple | ✅ 26 languages | Complete |
| Output formats | 3+ formats | ✅ 4+ formats | Complete |
| Error handling | Robust | ✅ Comprehensive | Complete |
| CLI interface | User-friendly | ✅ Full featured | Complete |

## Future Maintenance

- Multiple API key fallbacks for reliability
- Flexible headers for easy Android client updates
- Rate limiting prevents service blocking
- Comprehensive logging for debugging
- Test videos for validation

## Documentation

- Complete installation and usage guide
- Working code examples
- CLI help system
- Inline code documentation
- Technical implementation details

---

**Status**: Production-ready tool successfully extracting YouTube transcripts with full multi-language support and robust error handling.
