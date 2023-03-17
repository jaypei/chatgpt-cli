# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys

import click

from chatgpt_cli import term
from chatgpt_cli import config
from chatgpt_cli import chatapi
from chatgpt_cli.cmds.ask import run_ask_cmd
from chatgpt_cli.cmds.chat import run_chat_loop, print_chat_banner
from chatgpt_cli import error


@click.group()
def cli():
    term.init()
    config.init()
    chatapi.init()


@cli.command()
def chat():
    """Asking questions to ChatGPT in interactive mode."""
    print_chat_banner(config.VERSION)
    try:
        run_chat_loop()
    except error.CommandExit:
        term.console.print("\nBye!")
    except error.CommandError as e:
        term.console.print(f"[bold red]Error: {e.message}[/bold red]")
        sys.exit(e.exit_code)
    except:    # pylint: disable=broad-exception-caught, bare-except
        term.console.print_exception()


@cli.command()
@click.argument('question', nargs=-1)
@click.option("--no-stream", is_flag=True, help="Disable streaming mode.")
def ask(question, no_stream):
    """One-time answer."""
    stream_mode = not no_stream
    question = " ".join(question)
    if question.strip() == "":
        current_context = click.get_current_context()
        click.echo(cli.get_help(current_context))
        sys.exit(1)
    try:
        run_ask_cmd(" ".join(question), stream_mode=stream_mode)
    except error.CommandError as e:
        term.console.print(f"[bold red]Error: {e.message}[/bold red]")
        sys.exit(e.exit_code)
    # control + c
    except KeyboardInterrupt:
        term.console.print("\nBye!")
        sys.exit(2)
    except:
        term.console.print_exception()
