# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import typing as t

from chatgpt_cli import term
from chatgpt_cli import config
from chatgpt_cli.cmds.base import BaseCmd, BaseMultiCmd


class ConfigCommand(BaseMultiCmd):

    name = "config"
    help = "Configure the chatgpt-cli."

    def __init__(self, *args, **kwargs):
        self.subcommands = [
            ConfigListModelCommand(),
            ConfigListPromptCommand(),
        ]
        super().__init__(*args, **kwargs)


class ConfigListPromptCommand(BaseCmd):

    name = "list-prompt"
    help = "List all prompt."

    def run(self, **kwargs) -> t.Any:
        for prompt in config.prompts():
            prefix = "  "
            prompt_text = str(config.get_prompt_message(prompt))
            prompt_name = "[green]" + prompt + "[/green]"
            surfix = ""
            if prompt == config.get_config()['CLI']['default_prompt']:
                prefix = "[underline][bold][red]:heavy_check_mark:[/red][/bold] "
                surfix = "[/underline]"
            term.console.print(prefix + prompt_name + " " + prompt_text + surfix)


class ConfigListModelCommand(BaseCmd):

    name = "list-model"
    help = "List all model."

    def run(self, **kwargs) -> t.Any:
        ...
