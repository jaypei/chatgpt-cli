# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys

import click

from chatgpt_cli import term
from chatgpt_cli import config
from chatgpt_cli import chatapi
from chatgpt_cli.cmds.chat import run_chat_loop
from chatgpt_cli import error


@click.group()
def cli():
    term.init()
    config.init()
    chatapi.init()


@cli.command()
def chat():
    """Asking questions to ChatGPT in interactive mode."""
    term.print_chat_banner()
    try:
        run_chat_loop()
    except error.CommandExit:
        term.console.print("\nBye!")
    except error.CommandError as e:
        term.console.print(f"[bold red]Error: {e.message}[/bold red]")
        sys.exit(e.exit_code)
    except:    # pylint: disable=broad-exception-caught, bare-except
        term.console.print_exception()


# TODO
@cli.command()
def ask():
    """One-time answer."""
    pass
