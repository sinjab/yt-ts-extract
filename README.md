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
extractor = YouTubeTranscriptExtractor(
    timeout=20,        # per-request timeout (seconds)
    max_retries=5,     # HTTP retries on transient failures
    backoff_factor=1.0,# exponential backoff factor
    min_delay=1.5      # minimum delay between requests (rate limiting)
)
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
  --timeout FLOAT        Per-request timeout in seconds (default: 30)
  --retries INT          Max HTTP retries on failure (default: 3)
  --backoff FLOAT        Exponential backoff factor (default: 0.75)
  --min-delay FLOAT      Minimum delay between requests for rate limiting (default: 2)
  --proxy TEXT           Proxy URL (e.g., "http://user:pass@host:port" or "http://host:port")
  --help                 Show this message and exit
```

### Network resilience tuning

You can tune network behavior to improve reliability in flaky environments or speed up trusted CI environments:

```bash
# Increase retries and timeout
yt-transcript dQw4w9WgXcQ --retries 5 --timeout 45

# Reduce delay for faster runs (use responsibly)
yt-transcript dQw4w9WgXcQ --min-delay 1.0 --backoff 0.5

# Use proxy for network routing
yt-transcript dQw4w9WgXcQ --proxy "http://user:pass@host:port"

# Proxy with custom timeout
yt-transcript dQw4w9WgXcQ --proxy "http://host:port" --timeout 60
```

### Proxy Support

The tool supports HTTP, HTTPS, and SOCKS proxies for network routing:

```bash
# HTTP proxy with authentication
yt-transcript --proxy "http://username:password@proxy-host:8080" dQw4w9WgXcQ

# HTTPS proxy
yt-transcript --proxy "https://proxy-host:8443" dQw4w9WgXcQ

# SOCKS5 proxy
yt-transcript --proxy "socks5://user:pass@proxy-host:1080" dQw4w9WgXcQ

# Batch processing with proxy
yt-transcript --batch ids.txt --proxy "http://host:port" --output-dir transcripts/
```

In Python code:

```python
from yt_ts_extract import YouTubeTranscriptExtractor

# Initialize with proxy
extractor = YouTubeTranscriptExtractor(
    proxy="http://user:pass@host:port",
    timeout=30,
    max_retries=3
)

# Use convenience functions with proxy
from yt_ts_extract import get_transcript
transcript = get_transcript("dQw4w9WgXcQ", proxy="http://host:port")
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

```
```