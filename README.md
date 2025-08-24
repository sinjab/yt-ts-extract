# yt-ts-extract

[![PyPI version](https://badge.fury.io/py/yt-ts-extract.svg)](https://badge.fury.io/py/yt-ts-extract)
[![Python Support](https://img.shields.io/pypi/pyversions/yt-ts-extract.svg)](https://pypi.org/project/yt-ts-extract/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust Python library and CLI tool for extracting YouTube video transcripts with multi-language support and proxy rotation capabilities.

## ✨ Key Features

- **Extract transcripts** from YouTube videos via video ID
- **26+ language support** (English, Spanish, French, German, Japanese, Arabic, Chinese, etc.)
- **Multiple output formats**: plain text, SRT subtitles, timestamped segments, JSON
- **Batch processing** for multiple videos
- **Anti-bot protection**: Android client implementation bypasses detection
- **Proxy rotation**: Multiple proxy support with automatic rotation strategies
- **Both CLI and Python library** interfaces

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

```bash
# Basic transcript extraction
yt-transcript fR9ClX0egTc

# Export as SRT subtitles
yt-transcript -f srt -o video.srt fR9ClX0egTc

# List available languages
yt-transcript --list-languages fR9ClX0egTc

# Batch process multiple videos
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

# Quick transcript extraction
transcript = get_transcript("fR9ClX0egTc")
print(f"Segments: {len(transcript)}")

# Export to SRT
srt_text = export_to_srt(transcript)
with open("video.srt", "w", encoding="utf-8") as f:
    f.write(srt_text)

# Plain text and languages
text = get_transcript_text("fR9ClX0egTc")
langs = get_available_languages("fR9ClX0egTc")
print(f"Languages available: {[l['code'] for l in langs]}")

# Using the class directly
extractor = YouTubeTranscriptExtractor(
    timeout=20,
    max_retries=5,
    backoff_factor=1.0,
    min_delay=1.5
)
segments = extractor.get_transcript("fR9ClX0egTc", language="en")
stats = get_transcript_stats(segments)
print(stats)
```

## 🎛️ CLI Options

```bash
yt-transcript [OPTIONS] VIDEO_ID

Options:
  -f, --format [text|srt|segments|stats]  Output format (default: text)
  -o, --output PATH                       Save output to file
  -l, --language TEXT                     Language code (e.g., 'en', 'es', 'fr')
  --list-languages                        Show available languages for video
  --batch PATH                            Process video IDs from file (one per line)
  --output-dir PATH                       Directory for batch output files
  --search TEXT                           Search for specific text in transcript
  --examples                              Show usage examples
  --timeout FLOAT                         Per-request timeout in seconds (default: 30)
  --retries INT                           Max HTTP retries on failure (default: 3)
  --backoff FLOAT                         Exponential backoff factor (default: 0.75)
  --min-delay FLOAT                       Minimum delay between requests (default: 2)
  --proxy TEXT                            Proxy URL (e.g., "http://user:pass@host:port")
  --proxy-list PATH                       Proxy list file for rotation
  --rotation-strategy [random|round_robin|least_used]  Proxy rotation strategy (default: random)
  --health-check                          Perform health check on all proxies before starting
  --help                                  Show this message and exit
```

### Network Tuning Examples

```bash
# Increase retries and timeout
yt-transcript fR9ClX0egTc --retries 5 --timeout 45

# Reduce delay for faster runs (use responsibly)
yt-transcript fR9ClX0egTc --min-delay 1.0 --backoff 0.5

# Single proxy
yt-transcript fR9ClX0egTc --proxy "http://user:pass@host:port"

# Proxy rotation with health check
yt-transcript fR9ClX0egTc --proxy-list proxies.txt --health-check

# Batch processing with proxy rotation
yt-transcript --batch ids.txt --proxy-list proxies.txt --output-dir transcripts/
```

## 🔄 Proxy Support

### Single Proxy

```bash
# HTTP proxy with authentication
yt-transcript --proxy "http://username:password@proxy-host:8080" fR9ClX0egTc

# HTTPS proxy
yt-transcript --proxy "https://proxy-host:8443" fR9ClX0egTc

# SOCKS5 proxy
yt-transcript --proxy "socks5://user:pass@proxy-host:1080" fR9ClX0egTc
```

### Proxy Rotation

Load multiple proxies from a file and automatically rotate between them:

```bash
# Basic proxy rotation
yt-transcript --proxy-list proxies.txt fR9ClX0egTc

# With rotation strategy
yt-transcript --proxy-list proxies.txt --rotation-strategy round_robin fR9ClX0egTc

# With health check
yt-transcript --proxy-list proxies.txt --health-check fR9ClX0egTc
```

**Proxy List File Format** (`proxies.txt`):
```
Address Port Username Password
23.95.150.145 6114 mhzbhrwb yj2veiaafrbu
198.23.239.134 6540 mhzbhrwb yj2veiaafrbu
45.38.107.97 6014 mhzbhrwb yj2veiaafrbu
64.137.96.74 6641 mhzbhrwb yj2veiaafrbu
216.10.27.159 6837 mhzbhrwb yj2veiaafrbu
136.0.207.84 6661 mhzbhrwb yj2veiaafrbu
```

**Rotation Strategies:**
- `random`: Random proxy selection (default)
- `round_robin`: Cycle through proxies in order
- `least_used`: Select least recently used proxy

### Python Proxy Usage

```python
from yt_ts_extract import YouTubeTranscriptExtractor, ProxyManager

# Single proxy
extractor = YouTubeTranscriptExtractor(
    proxy="http://user:pass@host:port",
    timeout=30,
    max_retries=3
)

# Proxy rotation
proxy_manager = ProxyManager.from_file("proxies.txt", rotation_strategy="round_robin")
extractor = YouTubeTranscriptExtractor(
    proxy_manager=proxy_manager,
    timeout=30,
    max_retries=3
)

# Convenience functions with proxy rotation
from yt_ts_extract import get_transcript_with_proxy_rotation
transcript = get_transcript_with_proxy_rotation("fR9ClX0egTc", "proxies.txt")
```

**Proxy Best Practices:**
- Use `--health-check` to verify proxy connectivity before processing
- Failed proxies are automatically deactivated and reactivated after cooldown
- Each proxy respects minimum delay between requests
- Monitor proxy health with `extractor.get_proxy_stats()`

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

Use `--list-languages` to see available languages for any video.

## 🔧 Advanced Usage

### Batch Processing

Create an `ids.txt` file (one video ID per line):
```
fR9ClX0egTc
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

### Advanced Python Features

```python
from yt_ts_extract import YouTubeTranscriptExtractor
from yt_ts_extract.utils import get_transcript_stats

extractor = YouTubeTranscriptExtractor()

# Get timestamped segments for an ID
segments = extractor.get_transcript("fR9ClX0egTc", language="en")
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

```http
User-Agent: com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip
X-YouTube-Client-Name: 3
X-YouTube-Client-Version: 20.10.38
Content-Type: application/json
```

### Dual XML Parser System
- **Legacy format**: Direct XML transcript data
- **Current format**: API-based JSON responses with embedded XML

### Proxy Architecture
- **Rotation strategies**: random, round_robin, least_used
- **Health monitoring**: Automatic health checks and failed proxy deactivation
- **Recovery**: Reactivation after cooldown periods

### Error Handling & Recovery
- **Exponential backoff**: Prevents overwhelming servers during failures
- **Retry mechanisms**: Configurable retry logic with circuit breaking
- **Graceful degradation**: Falls back to alternative extraction methods
- **Rate limiting**: Built-in delays prevent IP-based blocking

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=yt_ts_extract --cov-report=term-missing

# Run specific test suites
uv run pytest tests/test_proxy_manager.py -v
uv run pytest tests/test_e2e_proxy.py -v
```

### Test Categories
- **Unit tests**: Individual component testing
- **Integration tests**: CLI and API integration testing  
- **E2E tests**: Full workflow testing with real YouTube videos
- **Proxy tests**: Proxy rotation and health check testing
- **Network resilience**: Timeout and retry behavior testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/sinjab/yt-ts-extract.git
cd yt-ts-extract
uv sync  # Install dependencies
uv run pytest  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/sinjab/yt-ts-extract/issues)
- **Documentation**: This README and inline code documentation
- **Examples**: Check the `examples/` directory for usage patterns

---

**Made with ❤️ for the developer community. Happy transcript extracting!**