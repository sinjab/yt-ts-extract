import sys
import os
import pytest

from yt_ts_extract.cli import main

# Skip real network E2E tests on CI to avoid flakiness (e.g., age restrictions)
pytestmark = pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip real network E2E tests on CI",
)

@pytest.mark.e2e
class TestE2ECLI:
    VIDEO_ID = "fR9ClX0egTc"  # Popular video with known captions

    def run_cli(self, argv):
        old_argv = sys.argv
        sys.argv = ["yt-transcript", *argv]
        try:
            main()
        except SystemExit as e:
            # Allow sys.exit(0)
            if e.code not in (0, None):
                raise
        finally:
            sys.argv = old_argv

    def test_text_output_real_network(self, capsys):
        self.run_cli([self.VIDEO_ID, "--verbose", "--clean"])  # default format: text
        out = capsys.readouterr().out
        assert out.strip(), "Expected non-empty transcript output"

    def test_srt_output_real_network(self, capsys):
        self.run_cli(["-f", "srt", self.VIDEO_ID])
        out = capsys.readouterr().out
        # Basic SRT structure expectations
        assert "-->" in out and any(c.isdigit() for c in out), "Expected SRT formatted output"

    def test_list_languages_real_network(self, capsys):
        self.run_cli(["--list-languages", self.VIDEO_ID])
        out = capsys.readouterr().out.lower()
        # Expect at least English to be present among languages
        assert "en" in out or "english" in out, "Expected 'en' language to be listed"

    def test_segments_output_real_network(self, capsys):
        self.run_cli(["-f", "segments", self.VIDEO_ID])
        out = capsys.readouterr().out
        # Expect timestamped lines like [MM:SS] text
        assert "[00:" in out or "[01:" in out, "Expected timestamped segment lines"

    def test_search_results_real_network(self, capsys):
        # Use a common word likely to appear
        self.run_cli(["--search", "never", self.VIDEO_ID])
        out = capsys.readouterr().out.lower()
        assert "search results" in out and (
            "never" in out
        ), "Expected search results section with matches"
