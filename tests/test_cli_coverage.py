import sys
import io
import os
import pytest
from unittest.mock import patch, MagicMock

from yt_ts_extract.cli import main, run_examples, handle_batch_processing
from yt_ts_extract.extractor import YouTubeTranscriptExtractor


def run_cli(argv):
    """Helper to run CLI with given arguments"""
    old_argv = sys.argv
    sys.argv = ["yt-transcript", *argv]
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv


class TestCLICoverage:
    """Test cases to improve CLI coverage"""
    
    def test_cli_examples_mode(self, capsys):
        """Test --examples flag"""
        run_cli(["--examples"])
        out = capsys.readouterr().out
        
        assert "YouTube Transcript Extractor - CLI Examples" in out
        assert "Basic text extraction" in out
        assert "yt-transcript dQw4w9WgXcQ" in out
        assert "Create a file 'ids.txt'" in out
    
    def test_cli_list_languages(self, monkeypatch, capsys):
        """Test --list-languages flag"""
        fake_languages = [
            {"code": "en", "name": "English", "auto_generated": False},
            {"code": "es", "name": "Spanish", "auto_generated": True}
        ]
        
        def fake_get_available_languages(self, video_id):
            return fake_languages
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_available_languages", fake_get_available_languages)
        
        run_cli(["--list-languages", "test123"])
        out = capsys.readouterr().out
        
        assert "Available languages:" in out
        assert "en: English (manual)" in out
        assert "es: Spanish (auto-generated)" in out
    
    def test_cli_verbose_mode(self, monkeypatch, capsys):
        """Test verbose output"""
        fake_segments = [{"text": "test", "start": 0.0, "duration": 1.0}]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["-v", "test123"])
        out = capsys.readouterr().out
        
        assert "Extracting transcript for ID: test123" in out
        assert "Successfully extracted 1 segments" in out
        assert "test" in out
    
    def test_cli_verbose_with_language(self, monkeypatch, capsys):
        """Test verbose output with language specification"""
        fake_segments = [{"text": "test", "start": 0.0, "duration": 1.0}]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["-v", "-l", "es", "test123"])
        out = capsys.readouterr().out
        
        assert "Extracting transcript for ID: test123" in out
        assert "Language: es" in out
        assert "Successfully extracted 1 segments" in out
    
    def test_cli_segments_format(self, monkeypatch, capsys):
        """Test segments format output"""
        fake_segments = [
            {"text": "first", "start": 0.0, "duration": 1.0},
            {"text": "second", "start": 2.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        def fake_format_timestamp(self, seconds):
            return "00:00"
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        monkeypatch.setattr(YouTubeTranscriptExtractor, "_format_timestamp", fake_format_timestamp)
        
        run_cli(["-f", "segments", "test123"])
        out = capsys.readouterr().out
        
        assert "[00:00] first" in out
        assert "[00:00] second" in out
    
    def test_cli_srt_format(self, monkeypatch, capsys):
        """Test SRT format output"""
        fake_segments = [
            {"text": "first", "start": 0.0, "duration": 1.0},
            {"text": "second", "start": 2.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["-f", "srt", "test123"])
        out = capsys.readouterr().out
        
        assert "1\n00:00:00,000 --> 00:00:01,000\nfirst" in out
        assert "2\n00:00:02,000 --> 00:00:03,000\nsecond" in out
    
    def test_cli_stats_format(self, monkeypatch, capsys):
        """Test stats format output"""
        fake_segments = [
            {"text": "first segment", "start": 0.0, "duration": 1.0},
            {"text": "second segment", "start": 2.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["-f", "stats", "test123"])
        out = capsys.readouterr().out
        
        assert "=== TRANSCRIPT STATISTICS ===" in out
        assert "Segment Count: 2" in out
        assert "Word Count: 4" in out
    
    def test_cli_clean_text(self, monkeypatch, capsys):
        """Test clean text output"""
        fake_segments = [{"text": "test text", "start": 0.0, "duration": 1.0}]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["--clean", "test123"])
        out = capsys.readouterr().out
        
        # The clean function capitalizes sentences, so "test text" becomes "Test text"
        assert "Test text" in out
    
    def test_cli_with_summary(self, monkeypatch, capsys):
        """Test summary generation"""
        fake_segments = [
            {"text": "This is the first sentence. This is the second sentence.", "start": 0.0, "duration": 2.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["--summary", "1", "test123"])
        out = capsys.readouterr().out
        
        assert "--- SUMMARY ---" in out
    
    def test_cli_with_keywords(self, monkeypatch, capsys):
        """Test keyword extraction"""
        fake_segments = [
            {"text": "test text test", "start": 0.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["--keywords", "3", "test123"])
        out = capsys.readouterr().out
        
        assert "--- TOP 3 KEYWORDS ---" in out
        # The keyword extraction removes spaces and non-alphabetic chars, so "test text test" becomes "testtexttest"
        assert "testtexttest: 1" in out
    
    def test_cli_with_search(self, monkeypatch, capsys):
        """Test search functionality"""
        fake_segments = [
            {"text": "test text", "start": 0.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["--search", "test", "test123"])
        out = capsys.readouterr().out
        
        assert "--- SEARCH RESULTS FOR 'test' ---" in out
        # The search uses the extractor's format_timestamp method, which returns "00:00" in our mock
        assert "[00:00] test text" in out
    
    def test_cli_search_no_matches(self, monkeypatch, capsys):
        """Test search with no matches"""
        fake_segments = [
            {"text": "different text", "start": 0.0, "duration": 1.0}
        ]
        
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            return fake_segments
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        run_cli(["--search", "nonexistent", "test123"])
        out = capsys.readouterr().out
        
        assert "--- SEARCH RESULTS ---" in out
        assert "No matches found for 'nonexistent'" in out
    
    def test_cli_error_handling(self, monkeypatch, capsys):
        """Test error handling in CLI"""
        def fake_get_transcript(self, video_id, language="en", prefer_manual=True):
            raise Exception("Test error")
        
        monkeypatch.setattr(YouTubeTranscriptExtractor, "get_transcript", fake_get_transcript)
        
        with pytest.raises(SystemExit):
            run_cli(["test123"])
        
        # Error should be printed to stderr
        err = capsys.readouterr().err
        assert "Error: Test error" in err
    
    def test_cli_missing_video_id_error(self, capsys):
        """Test error when no video ID is provided"""
        with pytest.raises(SystemExit):
            run_cli([])
        
        # This should trigger the parser.error call
    
    def test_cli_batch_file_not_found(self, capsys):
        """Test batch processing with non-existent file"""
        with pytest.raises(SystemExit):
            run_cli(["--batch", "nonexistent.txt"])
        
        # Error should be printed to stderr
        err = capsys.readouterr().err
        assert "Error: File 'nonexistent.txt' not found" in err
    
    def test_cli_batch_empty_file(self, tmp_path, capsys):
        """Test batch processing with empty file"""
        ids_file = tmp_path / "empty.txt"
        ids_file.write_text("", encoding="utf-8")
        
        with pytest.raises(SystemExit):
            run_cli(["--batch", str(ids_file)])
        
        # Error should be printed to stderr
        err = capsys.readouterr().err
        assert "Error: No valid video IDs found in file" in err
    
    def test_cli_batch_only_comments(self, tmp_path, capsys):
        """Test batch processing with file containing only comments"""
        ids_file = tmp_path / "comments.txt"
        ids_file.write_text("# comment 1\n# comment 2\n", encoding="utf-8")
        
        with pytest.raises(SystemExit):
            run_cli(["--batch", str(ids_file)])
        
        # Error should be printed to stderr
        err = capsys.readouterr().err
        assert "Error: No valid video IDs found in file" in err


class TestCLIFunctionCoverage:
    """Test individual CLI functions for coverage"""
    
    def test_run_examples_function(self, capsys):
        """Test run_examples function directly"""
        run_examples()
        out = capsys.readouterr().out
        
        assert "YouTube Transcript Extractor - CLI Examples" in out
        assert "Basic text extraction" in out
        assert "yt-transcript dQw4w9WgXcQ" in out
    
    def test_handle_batch_processing_function(self, tmp_path, capsys, monkeypatch):
        """Test handle_batch_processing function directly"""
        # Prepare ID list file
        ids_file = tmp_path / "ids.txt"
        ids_file.write_text("vid1\nvid2\n", encoding="utf-8")
        
        # Mock the batch_process_ids function
        def fake_batch_process_ids(ids, output_dir, proxy=None):
            return {
                'successful': [
                    {
                        'video_id': 'vid1',
                        'stats': {'duration_formatted': '00:01:00', 'word_count': 10}
                    }
                ],
                'failed': [
                    {
                        'video_id': 'vid2',
                        'error': 'Test error'
                    }
                ],
                'total_processed': 2
            }
        
        monkeypatch.setattr("yt_ts_extract.cli.batch_process_ids", fake_batch_process_ids)
        
        # Create args object
        args = MagicMock()
        args.batch = str(ids_file)
        args.output_dir = str(tmp_path / "out")
        args.proxy_list = None  # No proxy rotation for this test
        args.proxy = None  # No single proxy for this test
        
        handle_batch_processing(args)
        out = capsys.readouterr().out
        
        assert "Processing 2 video IDs..." in out
        assert "Successful: 1" in out
        assert "Failed: 1" in out
        assert "✅ vid1: 00:01:00, 10 words" in out
        assert "❌ vid2: Test error" in out
