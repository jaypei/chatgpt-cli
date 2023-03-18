# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import re
import typing as t
import importlib
from gettext import gettext as _

from click import Command, Context, Parameter

from chatgpt_cli import term


class BaseCmd(Command):

    name: str = "base_cmd"
    help: str = "Base command."
    opts: t.Optional[t.List[Parameter]] = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("name", self.name)
        kwargs.setdefault("help", self.help)
        super().__init__(*args, **kwargs)
        self.params.extend(self.opts or [])

    def invoke(self, ctx: Context) -> t.Any:
        if self.deprecated:
            message = _(
                "DeprecationWarning: The command {name!r} is deprecated."
            ).format(name=self.name)
            term.console.print(message, style="bold red", highlight=False)
        return ctx.invoke(self.run, **ctx.params)

    def run(self, **kwargs) -> t.Any:
        raise NotImplementedError


def load_cmd(cmd_name: str) -> BaseCmd:
    # remove "Command" suffix
    if not cmd_name.endswith("Command"):
        raise ValueError(f"Invalid command name {cmd_name}")
    lower_cmd_name = cmd_name[:cmd_name.index("Command")]
    # CamelCase to snake_case
    lower_cmd_name = lower_cmd_name[0].lower() + lower_cmd_name[1:]
    lower_cmd_name = re.sub(r"([A-Z])", r"_\1", lower_cmd_name).lower()
    module_name = f"chatgpt_cli.cmds.{lower_cmd_name}"
    try:
        module = importlib.import_module(module_name)
        cmd_cls = getattr(module, cmd_name)
        return cmd_cls()
    except ModuleNotFoundError:
        raise ValueError(f"No such module {cmd_name}")
    except AttributeError:
        raise ValueError(f"No such command {cmd_name}")
