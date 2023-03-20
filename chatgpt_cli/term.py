# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import os
from datetime import timedelta

from rich.console import Console
from rich.text import Text
from rich.progress import Progress, Task, ProgressColumn
from rich.emoji import EMOJI
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from chatgpt_cli import config


# Reference: https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
prompt_style = Style.from_dict({
    # default text
    '': '#d7af00',
    'input_key': '#d7af00',
    'session': '#5f5fff bold',
    'conversation_count': '#5fd700 bold',
    'prompt_sep': '#008700 bold',
})


console: Console
prompt: PromptSession
prompt_no_hist: PromptSession


def init():
    global console, prompt, prompt_no_hist
    config_dir = config.get_config_dir(try_create=True)
    prompt_hist_file = os.path.join(config_dir, "cli_history")
    prompt = PromptSession(history=FileHistory(prompt_hist_file), style=prompt_style)
    prompt_no_hist = PromptSession(style=prompt_style)
    console = Console()


def get_emoji(name):
    return EMOJI.get(name, name)


class TimeElapsedColumn(ProgressColumn):
    """Renders time elapsed."""

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--", style="progress.elapsed")
        delta = timedelta(seconds=int(elapsed))
        return Text(str(delta), style="progress.elapsed")


def make_progress_bar(client_console: Console) -> Progress:
    return Progress(
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=client_console,
        transient=True,
    )
