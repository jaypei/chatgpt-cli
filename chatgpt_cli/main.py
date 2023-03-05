# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import click

from chatgpt_cli import term
from chatgpt_cli import config
from chatgpt_cli import chatapi
from chatgpt_cli.cmds.chat import run_chat_loop


@click.group()
def cli():
    term.init()
    config.init()
    chatapi.init()


@cli.command()
def chat():
    term.print_chat_banner()
    try:
        run_chat_loop()
    except EOFError:
        term.console.print("\nBye!")
    except:    # pylint: disable=broad-exception-caught, bare-except
        term.console.print_exception()
