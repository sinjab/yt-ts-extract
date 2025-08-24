import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path

from yt_ts_extract.utils import (
    batch_process_ids,
    demo_utilities,
    export_to_srt,
    clean_transcript_text,
    extract_keywords,
    search_transcript,
    create_summary,
    get_transcript_stats,
)


class TestUtilsCoverage:
    """Test cases to improve utils coverage"""

    def test_batch_process_ids_success(self, tmp_path):
        """Test successful batch processing"""
        extractor = MagicMock()

        # Mock transcript data
        fake_transcript = [{"text": "Hello world", "start": 0.0, "duration": 1.0}]

        # Mock extractor methods
        extractor.get_transcript.return_value = fake_transcript
        extractor.get_transcript_text.return_value = "Hello world"
        extractor._format_timestamp.return_value = "00:00"

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            # Mock file operations
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("yt_ts_extract.utils.export_to_srt") as mock_srt:
                    with patch("yt_ts_extract.utils.clean_transcript_text") as mock_clean:
                        mock_clean.return_value = "Hello world"

                        result = batch_process_ids(["vid1", "vid2"], str(tmp_path))

                        assert result["total_processed"] == 2
                        assert len(result["successful"]) == 2
                        assert len(result["failed"]) == 0
                        assert result["successful"][0]["video_id"] == "vid1"
                        assert result["successful"][1]["video_id"] == "vid2"

    def test_batch_process_ids_partial_failure(self, tmp_path):
        """Test batch processing with some failures"""
        extractor = MagicMock()

        # Mock extractor to fail on second video
        def mock_get_transcript(video_id, language="en", prefer_manual=True):
            if video_id == "vid1":
                return [{"text": "Hello", "start": 0.0, "duration": 1.0}]
            else:
                raise Exception("Network error")

        extractor.get_transcript.side_effect = mock_get_transcript
        extractor.get_transcript_text.return_value = "Hello"
        extractor._format_timestamp.return_value = "00:00"

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            with patch("builtins.open", mock_open()):
                with patch("yt_ts_extract.utils.export_to_srt"):
                    with patch("yt_ts_extract.utils.clean_transcript_text", return_value="Hello"):
                        result = batch_process_ids(["vid1", "vid2"], str(tmp_path))

                        assert result["total_processed"] == 2
                        assert len(result["successful"]) == 1
                        assert len(result["failed"]) == 1
                        assert result["successful"][0]["video_id"] == "vid1"
                        assert result["failed"][0]["video_id"] == "vid2"
                        assert "Network error" in result["failed"][0]["error"]

    def test_batch_process_ids_file_creation(self, tmp_path):
        """Test that batch processing creates expected files"""
        extractor = MagicMock()

        fake_transcript = [{"text": "Hello world", "start": 0.0, "duration": 1.0}]

        extractor.get_transcript.return_value = fake_transcript
        extractor.get_transcript_text.return_value = "Hello world"
        extractor._format_timestamp.return_value = "00:00"

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            # Create actual files to verify content
            result = batch_process_ids(["vid1"], str(tmp_path))

            # Check that files were created
            assert (tmp_path / "vid1_segments.txt").exists()
            assert (tmp_path / "vid1_text.txt").exists()
            assert (tmp_path / "vid1.srt").exists()

            # Check file contents
            segments_content = (tmp_path / "vid1_segments.txt").read_text(encoding="utf-8")
            assert "[00:00] Hello world" in segments_content

            text_content = (tmp_path / "vid1_text.txt").read_text(encoding="utf-8")
            assert "Hello world" in text_content

    def test_batch_process_ids_stats_included(self, tmp_path):
        """Test that batch processing includes stats in results"""
        extractor = MagicMock()

        fake_transcript = [{"text": "Hello world", "start": 0.0, "duration": 1.0}]

        extractor.get_transcript.return_value = fake_transcript
        extractor.get_transcript_text.return_value = "Hello world"
        extractor._format_timestamp.return_value = "00:00"

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            result = batch_process_ids(["vid1"], str(tmp_path))

            assert "stats" in result["successful"][0]
            stats = result["successful"][0]["stats"]
            assert "segment_count" in stats
            assert "word_count" in stats
            assert "duration_formatted" in stats

    def test_demo_utilities_success(self, capsys):
        """Test demo utilities function with successful transcript"""
        extractor = MagicMock()

        fake_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 1.0},
            {"text": "This is a test", "start": 1.0, "duration": 1.0},
        ]

        extractor.get_transcript.return_value = fake_transcript

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            demo_utilities()
            out = capsys.readouterr().out

            assert "YouTube Transcript Utilities - Demo" in out
            assert "Testing with video ID: dQw4w9WgXcQ" in out
            assert "1. Transcript Stats:" in out
            assert "2. Top Keywords:" in out
            assert "3. Sample SRT Export:" in out
            assert "4. Search Example:" in out
            assert "5. Summary:" in out

    def test_demo_utilities_exception_handling(self, capsys):
        """Test demo utilities function with exception"""
        extractor = MagicMock()
        extractor.get_transcript.side_effect = Exception("Demo error")

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            demo_utilities()
            out = capsys.readouterr().out

            assert "Demo encountered expected error: Demo error" in out
            assert "This is normal due to YouTube's anti-bot protection." in out
            assert "All utility functions are ready to use!" in out

    def test_export_to_srt_with_filename(self, tmp_path):
        """Test SRT export with filename parameter"""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "World", "start": 1.0, "duration": 1.0},
        ]

        filename = tmp_path / "test.srt"
        export_to_srt(transcript, str(filename))

        assert filename.exists()
        content = filename.read_text(encoding="utf-8")

        assert "1\n00:00:00,000 --> 00:00:01,000\nHello" in content
        assert "2\n00:00:01,000 --> 00:00:02,000\nWorld" in content

    def test_export_to_srt_without_filename(self):
        """Test SRT export without filename (returns string)"""
        transcript = [{"text": "Hello", "start": 0.0, "duration": 1.0}]

        result = export_to_srt(transcript, filename=None)

        assert isinstance(result, str)
        assert "1\n00:00:00,000 --> 00:00:01,000\nHello" in result

    def test_clean_transcript_text(self):
        """Test transcript text cleaning"""
        dirty_text = "Hello [music] world [applause] test"
        clean_text = clean_transcript_text(dirty_text)

        # The clean function removes artifacts and normalizes whitespace
        assert "[music]" not in clean_text
        assert "[applause]" not in clean_text
        assert "Hello  world  test" in clean_text  # Double spaces are normalized

    def test_extract_keywords_edge_cases(self):
        """Test keyword extraction with edge cases"""
        transcript = [
            {"text": "the the the", "start": 0.0, "duration": 1.0},
            {"text": "a a a", "start": 1.0, "duration": 1.0},
        ]

        # Test with very small number
        keywords = extract_keywords(transcript, 1)
        assert len(keywords) == 1

        # Test with number larger than available words
        keywords = extract_keywords(transcript, 100)
        assert len(keywords) > 0

    def test_search_transcript_no_context(self):
        """Test search without context words"""
        transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 1.0},
            {"text": "Goodbye world", "start": 1.0, "duration": 1.0},
        ]

        # Mock the extractor's format_timestamp method
        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor._format_timestamp.return_value = "00:00"
            mock_extractor_class.return_value = mock_extractor

            matches = search_transcript(transcript, "world", context_words=0)

            assert len(matches) == 2
            # With context_words=0, it returns just the matched word
            assert matches[0]["text"] == "world"
            assert matches[1]["text"] == "world"

    def test_search_transcript_with_context(self):
        """Test search with context words"""
        transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 1.0},
            {"text": "Goodbye world", "start": 1.0, "duration": 1.0},
        ]

        # Mock the extractor's format_timestamp method
        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor._format_timestamp.return_value = "00:00"
            mock_extractor_class.return_value = mock_extractor

            matches = search_transcript(transcript, "world", context_words=2)

            assert len(matches) == 2
            # Context should include surrounding words
            assert "Hello world" in matches[0]["text"]
            assert "Goodbye world" in matches[1]["text"]

    def test_create_summary_edge_cases(self):
        """Test summary creation with edge cases"""
        transcript = [
            {"text": "First sentence.", "start": 0.0, "duration": 1.0},
            {"text": "Second sentence.", "start": 1.0, "duration": 1.0},
        ]

        # Test with max_sentences larger than available
        summary = create_summary(transcript, max_sentences=10)
        # The summary function filters out short sentences (< 5 words)
        # "First sentence." and "Second sentence." are both < 5 words, so they get filtered out
        # This results in an empty summary, which becomes just "."
        assert summary == "."

        # Test with max_sentences = 0
        summary = create_summary(transcript, max_sentences=0)
        # When max_sentences is 0, it still processes the sentences but filters them out
        # So the result is still "."
        assert summary == "."

    def test_get_transcript_stats_edge_cases(self):
        """Test transcript stats with edge cases"""
        # Empty transcript
        empty_transcript = []
        stats = get_transcript_stats(empty_transcript)

        # Empty transcript returns empty dict
        assert stats == {}

        # Single segment
        single_transcript = [{"text": "Hello", "start": 0.0, "duration": 1.0}]
        stats = get_transcript_stats(single_transcript)

        assert stats["segment_count"] == 1
        assert stats["word_count"] == 1
        assert stats["duration_formatted"] == "00:01"


class TestUtilsErrorCoverage:
    """Test error handling scenarios for better coverage"""

    def test_batch_process_ids_file_write_error(self, tmp_path):
        """Test batch processing with file write errors"""
        extractor = MagicMock()

        fake_transcript = [{"text": "Hello world", "start": 0.0, "duration": 1.0}]

        extractor.get_transcript.return_value = fake_transcript
        extractor.get_transcript_text.return_value = "Hello world"
        extractor._format_timestamp.return_value = "00:00"

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            # Mock file operations to raise errors
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                result = batch_process_ids(["vid1"], str(tmp_path))

                assert len(result["failed"]) == 1
                assert "Permission denied" in result["failed"][0]["error"]

    def test_batch_process_ids_extractor_error(self, tmp_path):
        """Test batch processing with extractor errors"""
        extractor = MagicMock()
        extractor.get_transcript.side_effect = Exception("Extractor failed")

        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor_class.return_value = extractor

            result = batch_process_ids(["vid1"], str(tmp_path))

            assert len(result["failed"]) == 1
            assert "Extractor failed" in result["failed"][0]["error"]

    def test_search_transcript_case_sensitivity(self):
        """Test search case sensitivity"""
        transcript = [{"text": "Hello WORLD", "start": 0.0, "duration": 1.0}]

        # Mock the extractor's format_timestamp method
        with patch("yt_ts_extract.extractor.YouTubeTranscriptExtractor") as mock_extractor_class:
            mock_extractor = MagicMock()
            mock_extractor._format_timestamp.return_value = "00:00"
            mock_extractor_class.return_value = mock_extractor

            # Search is case insensitive by default
            matches = search_transcript(transcript, "world")
            assert len(matches) == 1  # Should match due to case insensitivity

    def test_create_summary_with_punctuation(self):
        """Test summary creation with various punctuation"""
        transcript = [
            {"text": "First sentence! Second sentence?", "start": 0.0, "duration": 1.0},
            {"text": "Third sentence. Fourth sentence...", "start": 1.0, "duration": 1.0},
        ]

        summary = create_summary(transcript, max_sentences=2)

        # The summary function filters out short sentences (< 5 words)
        # All these sentences are < 5 words, so they get filtered out
        # This results in an empty summary, which becomes just "."
        assert summary == "."
