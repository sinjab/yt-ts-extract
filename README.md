# yt-ts-extract

[![PyPI version](https://badge.fury.io/py/yt-ts-extract.svg)](https://badge.fury.io/py/yt-ts-extract)
[![Python Support](https://img.shields.io/pypi/pyversions/yt-ts-extract.svg)](https://pypi.org/project/yt-ts-extract/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust Python library and CLI tool for extracting YouTube video transcripts with multi-language support and various output formats.

## ✨ Key Features

### 🎯 Core Functionality
- **Extract transcripts** from YouTube videos via video ID
- **26+ language support** (English, Spanish, French, German, Japanese, Arabic, Chinese, etc.)
- **Multiple output formats**: plain text, SRT subtitles, timestamped segments, JSON
- **Batch processing** for multiple videos
- **Both CLI and Python library** interfaces

### 🛡️ Technical Highlights
- **Anti-bot protection**: Android client implementation bypasses detection
- **Dual XML parser**: Handles both legacy and current YouTube formats
- **Robust extraction**: API key extraction with fallback systems
- **Rate limiting**: Built-in protection prevents IP blocking
- **Error handling**: Comprehensive error handling and recovery

## 🚀 Installation
```bash
# Install from PyPI
pip install yt-ts-extract

# Or install in development mode
git clone https://github.com/sinjab/yt-ts-extract.git
cd yt-ts-extract
pip install -e .
```

## 📖 Quick Start

### Command Line Interface

After installation, use the `yt-transcript` command:

```bash
# Basic transcript extraction (pass a video ID)
yt-transcript dQw4w9WgXcQ

# Export as SRT subtitles
yt-transcript -f srt -o video.srt dQw4w9WgXcQ

# List available languages
yt-transcript --list-languages dQw4w9WgXcQ

# Batch process multiple videos (file of IDs)
yt-transcript --batch ids.txt --output-dir ./transcripts/

# Get help
yt-transcript --help
```

### Python Library

```python
from yt_ts_extract import (
    get_transcript,
    get_transcript_text,
    get_available_languages,
    YouTubeTranscriptExtractor,
)
from yt_ts_extract.utils import export_to_srt, get_transcript_stats

# Quick transcript extraction (ID only)
transcript = get_transcript("dQw4w9WgXcQ")
print(f"Segments: {len(transcript)}")

# Export to SRT
srt_text = export_to_srt(transcript)
with open("video.srt", "w", encoding="utf-8") as f:
    f.write(srt_text)

# Plain text and languages
text = get_transcript_text("dQw4w9WgXcQ")
langs = get_available_languages("dQw4w9WgXcQ")
print(f"Languages available: {[l['code'] for l in langs]}")

# Or using the class directly
extractor = YouTubeTranscriptExtractor()
segments = extractor.get_transcript("dQw4w9WgXcQ", language="en")
stats = get_transcript_stats(segments)
print(stats)
```

## 🎛️ CLI Options

```bash
yt-transcript [OPTIONS] VIDEO_ID

Options:
  -f, --format [text|srt|segments|stats]
                          Output format (default: text)
  -o, --output PATH      Save output to file
  -l, --language TEXT    Language code (e.g., 'en', 'es', 'fr')
  --list-languages       Show available languages for video
  --batch PATH           Process video IDs from file (one per line)
  --output-dir PATH      Directory for batch output files
  --search TEXT          Search for specific text in transcript
  --examples             Show usage examples
  --help                 Show this message and exit
```

## 📊 Output Formats

### 1. Plain Text (`text`)
```
Hello everyone and welcome to this tutorial.
In this video we'll be covering the basics of...
```

### 2. SRT Subtitles (`srt`)
```
1
00:00:00,000 --> 00:00:03,200
Hello everyone and welcome to this tutorial.

2
00:00:03,200 --> 00:00:07,840
In this video we'll be covering the basics of...
```

### 3. Timestamped Segments (`segments`)
```json
[
  {
    "start": 0.0,
    "end": 3.2,
    "duration": 3.2,
    "text": "Hello everyone and welcome to this tutorial."
  },
  {
    "start": 3.2,
    "end": 7.84,
    "duration": 4.64,
    "text": "In this video we'll be covering the basics of..."
  }
]
```

### 4. Statistics (`stats`)
```json
{
  "total_segments": 245,
  "total_duration": 1823.4,
  "word_count": 2156,
  "average_words_per_segment": 8.8,
  "languages_available": ["en", "es", "fr", "de"]
}
```

## 🌍 Language Support

Supports 26+ languages with automatic detection:

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | `en` | Spanish | `es` |
| French | `fr` | German | `de` |
| Italian | `it` | Portuguese | `pt` |
| Russian | `ru` | Japanese | `ja` |
| Korean | `ko` | Chinese (Simplified) | `zh-Hans` |
| Chinese (Traditional) | `zh-Hant` | Arabic | `ar` |
| Hindi | `hi` | Dutch | `nl` |
| Polish | `pl` | Turkish | `tr` |

And many more! Use `--list-languages` to see available languages for any video.

## 🔧 Advanced Usage

### Batch Processing

Create an `ids.txt` file (one video ID per line):
```
dQw4w9WgXcQ
9bZkp7q19f0
wIwCTQZ_xFE
```

Process all videos:
```bash
yt-transcript --batch ids.txt --format srt --output-dir ./subtitles/
```

### Search Within Transcripts

```bash
# Find mentions of specific topics
yt-transcript --search "machine learning" VIDEO_ID
```

### Python Library Advanced Features

```python
from yt_ts_extract import YouTubeTranscriptExtractor
from yt_ts_extract.utils import get_transcript_stats

extractor = YouTubeTranscriptExtractor()

# Get timestamped segments for an ID
segments = extractor.get_transcript("dQw4w9WgXcQ", language="en")
for seg in segments[:5]:
    print(f"{seg['start']:.1f}s: {seg['text']}")

# Get statistics about the transcript
stats = get_transcript_stats(segments)
print(f"Duration: {stats['duration_seconds']:.1f} seconds")
print(f"Word count: {stats['word_count']} words")
```

## 🏗️ Technical Architecture

### Android Client Implementation
The extractor uses Android YouTube client headers to bypass anti-bot measures:

```python
headers = {
    'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14)',
    'X-YouTube-Client-Name': '3',
    'X-YouTube-Client-Version': '20.10.38',
}
```

### Dual XML Format Support
Handles both YouTube's legacy and current transcript formats:

- **Legacy**: `<text start="160" dur="2800">content</text>`
- **Current**: `<p t="160" d="2800"><s>content</s></p>`

### Rate Limiting & Error Handling
- Built-in delays prevent IP blocking
- Multiple API key extraction methods
- Graceful fallbacks for various error conditions
- Comprehensive logging for debugging

## 🧪 Testing

### Running the tests

```bash
# Using uv (recommended)
uv run pytest -q

# Or using your environment directly
pytest -q

# Run a specific test file or test
uv run pytest tests/test_cli_batch.py -q
uv run pytest -q -k test_get_transcript_text_joins_without_network

# With coverage summary
uv run pytest --maxfail=1 --disable-warnings -q --cov=yt_ts_extract --cov-report=term
```

Note: The suite assumes the package accepts only YouTube video IDs (not full URLs) in both library and CLI usage.

The library has been tested with various video types:

### Test Results

**Physics Lecture Video** (`wIwCTQZ_xFE`)
- ✅ 377 transcript segments extracted
- ✅ 26 language tracks detected
- ✅ Complete lecture content captured

**Music Video** (`dQw4w9WgXcQ`)
- ✅ 61 transcript segments extracted
- ✅ 6 language tracks available
- ✅ Perfect SRT format export

**Educational Content** (`9bZkp7q19f0`)
- ✅ Multiple language support verified
- ✅ Batch processing functionality confirmed
- ✅ Search functionality working

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/sinjab/yt-ts-extract.git
cd yt-ts-extract

# Install in development mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black yt_ts_extract/
isort yt_ts_extract/
```

### Project Structure

```
yt_ts_extract/
├── __init__.py          # Public API exports
├── extractor.py         # Core transcript extraction logic
├── utils.py             # Utility functions
├── cli.py               # Command-line interface
└── examples/
    ├── __init__.py
    └── basic_usage.py   # Usage examples
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## 📚 Examples

Check out the `examples/` directory for more detailed usage examples:

```python
# Run built-in examples
from yt_ts_extract.examples import run_examples
run_examples()
```

Or from CLI:
```bash
yt-transcript --examples
```

## ⚠️ Limitations & Considerations

- **YouTube Terms of Service**: Ensure your usage complies with YouTube's ToS
- **Rate Limiting**: Built-in delays prevent blocking, but excessive usage may trigger limits
- **Video Availability**: Some videos may not have transcripts or may be geo-blocked
- **Language Detection**: Auto-generated transcripts may have varying quality

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built to provide a robust alternative to existing YouTube transcript tools
- Implements advanced anti-detection techniques for reliable operation
- Designed with both developer and end-user experience in mind

## 📞 Support

- **Documentation**: Check this README and built-in help (`yt-transcript --help`)
- **Issues**: [GitHub Issues](https://github.com/sinjab/yt-ts-extract/issues)
- **Examples**: Run `yt-transcript --examples` for interactive examples

---

**Status**: Production-ready library for extracting YouTube transcripts with comprehensive multi-language support and robust error handling.
