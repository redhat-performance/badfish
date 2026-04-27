import io

from rich.console import Console

from badfish.helpers.progress import polling_progress


def _render(console_kwargs, disable):
    buf = io.StringIO()
    console = Console(file=buf, **console_kwargs)
    with polling_progress(console, 3, "Host state", disable=disable) as (progress, task_id):
        for i in range(3):
            progress.update(task_id, completed=i + 1, state="Off")
    return buf.getvalue()


def _has_progress_ui(out):
    """Progress UI is considered rendered if any bar-specific token appears.
    Rich may emit a trailing newline in no-op modes on some versions; we only
    care that no actual POLLING frame was drawn."""
    return "POLLING" in out or "\x1b[" in out or "Host state" in out


def test_disabled_emits_no_progress_ui_even_on_terminal():
    """Explicit disable=True must suppress all progress rendering."""
    out = _render({"force_terminal": True, "width": 80}, disable=True)
    assert not _has_progress_ui(out), f"unexpected progress output: {out!r}"


def test_non_terminal_emits_no_progress_ui():
    """Non-TTY console (pipe/redirect/capsys) must not render the progress bar."""
    out = _render({"force_terminal": False, "width": 80}, disable=False)
    assert not _has_progress_ui(out), f"unexpected progress output: {out!r}"


def test_terminal_renders_progress_when_enabled():
    """TTY + disable=False is the only combination that produces visible output."""
    out = _render({"force_terminal": True, "width": 80}, disable=False)
    assert "POLLING" in out
    assert "Host state" in out
    assert "\x1b[" in out  # ANSI escape sequences from Rich styling
