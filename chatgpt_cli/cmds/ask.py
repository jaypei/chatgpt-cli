# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys
import typing as t

import click

from chatgpt_cli import chatapi
from chatgpt_cli import term
from chatgpt_cli import error
from chatgpt_cli.cmds.base import BaseCmd


class AskCommand(BaseCmd):

    name = "ask"
    help = "One shot chat."
    opts = [
        click.Option(
            ["--no-stream"],
            is_flag=True,
            help="Disable streaming mode.",
        ),
        click.Argument(
            ["question"],
            nargs=-1,
        ),
    ]

    def run(self, **kwargs) -> t.Any:
        no_stream = kwargs.get("no_stream", False)
        question = kwargs.get("question", [])
        stream_mode = not no_stream
        question = " ".join(question)
        if question.strip() == "":
            current_context = click.get_current_context()
            click.echo(self.get_help(current_context))
            sys.exit(1)
        try:
            self.run_ask_cmd(" ".join(question), stream_mode=stream_mode)
        except error.CommandError as e:
            term.console.print(f"[bold red]Error: {e.message}[/bold red]")
            sys.exit(e.exit_code)
        # control + c
        except KeyboardInterrupt:
            term.console.print("\nBye!")
            sys.exit(2)
        except:
            term.console.print_exception()

    def run_ask_cmd(self, question, stream_mode=True):
        session_mgr = chatapi.get_session_manager()
        session_mgr.ask(question, stream=stream_mode, console=term.console)
        term.console.print("\n")
