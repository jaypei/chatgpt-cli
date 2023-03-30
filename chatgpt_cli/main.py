# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import click

from chatgpt_cli import term
from chatgpt_cli import config
from chatgpt_cli import chatapi
from chatgpt_cli.cmds.base import load_cmd


@click.group()
def cli():
    ...


def main():
    term.init()
    config.init()
    chatapi.init()
    cli.add_command(load_cmd("ChatCommand"))
    cli.add_command(load_cmd("AskCommand"))
    cli.add_command(load_cmd("ConfigCommand"))
    cli()
