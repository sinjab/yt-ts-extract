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
  --proxy-list PATH      Proxy list file for rotation (space/tab separated: Address Port Username Password)
  --rotation-strategy [random|round_robin|least_used]  Proxy rotation strategy (default: random)
  --health-check         Perform health check on all proxies before starting
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

# Proxy rotation with health check
yt-transcript dQw4w9WgXcQ --proxy-list proxies.txt --health-check

# Proxy rotation with custom strategy and timeout
yt-transcript dQw4w9WgXcQ --proxy-list proxies.txt --rotation-strategy round_robin --timeout 45
```

### Proxy Support

The tool supports both single proxies and **proxy rotation** for enhanced reliability:

#### Single Proxy

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

#### 🔄 Proxy Rotation (NEW!)

Load multiple proxies from a file and automatically rotate between them:

```bash
# Basic proxy rotation
yt-transcript --proxy-list proxies.txt dQw4w9WgXcQ

# With rotation strategy
yt-transcript --proxy-list proxies.txt --rotation-strategy round_robin dQw4w9WgXcQ

# With health check
yt-transcript --proxy-list proxies.txt --health-check dQw4w9WgXcQ

# Batch processing with proxy rotation
yt-transcript --batch ids.txt --proxy-list proxies.txt --output-dir transcripts/
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

> **Note**: The above proxy list has been tested and verified to work with the YouTube transcript extractor. These proxies support HTTP authentication and are configured for reliable transcript extraction.

**Rotation Strategies:**
- `random`: Random proxy selection (default)
- `round_robin`: Cycle through proxies in order
- `least_used`: Select least recently used proxy

In Python code:

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
transcript = get_transcript_with_proxy_rotation("dQw4w9WgXcQ", "proxies.txt")
```

**Proxy Rotation Best Practices:**
- **Health Checks**: Use `--health-check` to verify proxy connectivity before processing
- **Rotation Strategy**: Use `round_robin` for even distribution, `least_used` for load balancing
- **Failover**: Failed proxies are automatically deactivated and reactivated after cooldown
- **Rate Limiting**: Each proxy respects minimum delay between requests
- **Monitoring**: Check proxy stats with `extractor.get_proxy_stats()`

**Troubleshooting:**
- If proxies fail health checks, verify credentials and connectivity
- Increase `--timeout` for slower proxy connections
- Use `--retries` to handle temporary proxy failures
- Monitor proxy health during batch processing

**Advanced Proxy Management:**
```python
from yt_ts_extract import ProxyManager

# Custom proxy manager settings
proxy_manager = ProxyManager(
    proxy_configs=ProxyManager.from_file("proxies.txt").proxy_configs,
    rotation_strategy="least_used",
    health_check_url="https://www.youtube.com",  # Custom health check URL
    health_check_timeout=15.0,
    max_failures=2,  # Deactivate after 2 failures
    failure_cooldown=300.0,  # 5 minutes cooldown
    min_delay_between_requests=2.0  # 2 seconds between requests
)

# Health monitoring
health_results = proxy_manager.health_check_all()
stats = proxy_manager.get_stats()
print(f"Active proxies: {stats['active_proxies']}/{stats['total_proxies']}")

# Manual proxy management
proxy_manager.reactivate_proxies()  # Reactivate failed proxies after cooldown
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

```http
User-Agent: com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip
X-YouTube-Client-Name: 3
X-YouTube-Client-Version: 20.10.38
Content-Type: application/json
```

This approach mimics the official Android YouTube app, making requests appear as legitimate mobile traffic.

### Dual XML Parser System
The library supports both legacy and current YouTube transcript formats:
- **Legacy format**: Direct XML transcript data
- **Current format**: API-based JSON responses with embedded XML

### Proxy Architecture
The new proxy rotation system provides enterprise-grade reliability:

```python
# Proxy rotation strategies
rotation_strategies = {
    'random': 'Random selection for load distribution',
    'round_robin': 'Sequential rotation for even usage', 
    'least_used': 'Smart selection based on usage stats'
}

# Health monitoring
- Automatic proxy health checks
- Failed proxy deactivation with cooldown
- Real-time proxy statistics and monitoring
```

### Error Handling & Recovery
- **Exponential backoff**: Prevents overwhelming servers during failures
- **Retry mechanisms**: Configurable retry logic with circuit breaking
- **Graceful degradation**: Falls back to alternative extraction methods
- **Rate limiting**: Built-in delays prevent IP-based blocking

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=yt_ts_extract --cov-report=term-missing

# Run specific test suites
uv run pytest tests/test_proxy_manager.py -v
uv run pytest tests/test_e2e_proxy.py -v

# End-to-end testing
uv run pytest tests/test_e2e_cli.py -v
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