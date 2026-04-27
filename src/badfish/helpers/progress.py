from contextlib import contextmanager

from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn


@contextmanager
def polling_progress(console, total, prompt, disable=False):
    progress = Progress(
        TextColumn("- POLLING:"),
        BarColumn(bar_width=20),
        TaskProgressColumn(),
        TextColumn("- {task.fields[prompt]}: {task.fields[state]}"),
        console=console,
        transient=True,
        disable=disable or not console.is_terminal,
    )
    with progress:
        task_id = progress.add_task("", total=total, prompt=prompt, state="")
        yield progress, task_id
