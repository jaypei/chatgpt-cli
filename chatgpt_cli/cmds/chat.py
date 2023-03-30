# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys
import typing as t

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter

from chatgpt_cli import chatapi
from chatgpt_cli import term
from chatgpt_cli import error
from chatgpt_cli import config
from chatgpt_cli.cmds.base import BaseCmd
from chatgpt_cli.term import split_command_line, multiline_input_with_editor


CHAT_BANNER_LOGO = fr"""
   ________          __  __________  ______
  / ____/ /_  ____ _/ /_/ ____/ __ \/_  __/
 / /   / __ \/ __ `/ __/ / __/ /_/ / / /   
/ /___/ / / / /_/ / /_/ /_/ / ____/ / /    
\____/_/ /_/\__,_/\__/\____/_/     /_/     Version {config.VERSION}
""".lstrip("\n")
CHAT_BANNER_INTRO = """\
Welcome to ChatGPT-CLI, the command-line tool for ChatGPT!
Type '/help' to see a list of available commands.
Type '/exit' or [green]Ctrl-D[/green] to exit the program.
Press [green]F10[/green] to enter the EDITOR mode, which can edit multiple lines.
"""


class ChatCommand(BaseCmd):

    name = "chat"
    help = "Start a chat session in interactive mode."

    def run(self, **kwargs) -> t.Any:
        self.print_chat_banner()
        try:
            self.run_chat_loop()
        except error.CommandExit:
            term.console.print("\nBye!")
        except error.CommandError as e:
            term.console.print(f"[bold red]Error: {e.message}[/bold red]")
            sys.exit(e.exit_code)
        except:    # pylint: disable=broad-exception-caught, bare-except
            term.console.print_exception()

    def print_chat_banner(self):
        term.console.print(CHAT_BANNER_LOGO.format(version=config.VERSION),
                           style="bold", highlight=False)
        term.console.print(CHAT_BANNER_INTRO)

    def get_question(self):
        session_manager = chatapi.get_session_manager()
        while True:
            current_session = session_manager.current_session
            session_name = current_session.session_name
            conversation_count = str(current_session.conversation_count + 1)
            if current_session.no_context:
                conversation_count = "*"
            prompt_message :AnyFormattedText = [
                ('class:prompt_name',  f'({current_session.prompt}) '),
                ('class:session', f"{session_name} "),
                ('class:conversation_count', f'{conversation_count} '),
                ('class:prompt_sep',  '> '),
            ]

            kb = KeyBindings()

            @kb.add("f10")
            def _(event):
                event.app.current_buffer.text = multiline_input_with_editor(
                    event.app.current_buffer.text)

            question = term.prompt.prompt(
                prompt_message, completer=FuzzyCompleter(CommandCompleter()),
                key_bindings=kb)
            return question

    def ask_openai(self, question):
        session_mgr = chatapi.get_session_manager()
        session_mgr.ask(question, stream=True, console=term.console)
        term.console.print("\n")

    def run_chat_loop(self):
        while True:
            try:
                question = self.get_question()
                if question == "":
                    continue
                question_pcmd = split_command_line(question)
                for cmd in PCOMMANDS:
                    if question_pcmd[0] == cmd["match"]:
                        cmd["cls"]().run(question_pcmd[1:])  # type: ignore
                        break
                else:
                    self.ask_openai(question)
            except EOFError:
                raise error.CommandExit()
            except KeyboardInterrupt:
                term.console.print("If you want to exit, please press <Ctrl+D>.")


class PCommandBase:

    def complete(self, cmd, args) -> t.Iterator[Completion]:
        return iter([])

    def run(self, args):
        raise NotImplementedError()


class HistoryPCommand(PCommandBase):

    def run(self, args):
        session_manager = chatapi.get_session_manager()
        current_session = session_manager.current_session
        for message in current_session.histories:
            term.console.print(message.to_message_json())


class ContextPCommand(PCommandBase):

    def complete(self, cmd, args) -> t.Iterator[Completion]:
        if len(args) == 0:
            yield Completion("on", start_position=-len(args))
            yield Completion("off", start_position=-len(args))

    def run(self, args):
        session_manager = chatapi.get_session_manager()
        current_session = session_manager.current_session
        if len(args) < 1:
            return
        if args[0] == "on":
            current_session.no_context = False
        elif args[0] == "off":
            current_session.no_context = True
        else:
            term.console.print("Invalid argument.")


class PromptPCommand(PCommandBase):

    def complete(self, cmd, args) -> t.Iterator[Completion]:
        for prompt_name in config.prompts():
            yield Completion(prompt_name, start_position=-len(args))

    def run(self, args):
        session_manager = chatapi.get_session_manager()
        current_session = session_manager.current_session
        if len(args) < 1:
            return
        prompt_name = args[0]
        prompt_txt = config.get_prompt_message(prompt_name)
        if not prompt_txt:
            term.console.print(f"Prompt '{prompt_name}' is not found.")
            return
        current_session.prompt = prompt_name

class TitlePCommand(PCommandBase):

    def run(self, args):
        session_manager = chatapi.get_session_manager()
        if len(args) < 1:
            term.console.print(
                f"Current title is '{session_manager.current_session.session_name}'.")
            return
        title_name = args[0]
        session_manager.current_session.session_name = title_name


class ExitPCommand(PCommandBase):

    def run(self, args):
        raise error.CommandExit()


class HelpPCommand(PCommandBase):

    def run(self, args):
        for pcmd in PCOMMANDS:
            term.console.print(f"{pcmd['match']:12}{pcmd['desc']}")


# pylint: disable=line-too-long
PCOMMANDS = [
    { "match": "/hist", "desc": "Show history", "cls": HistoryPCommand },
    { "match": "/context", "desc": "Turn on/off context. Ex. /context <on|off>", "cls": ContextPCommand },
    { "match": "/prompt", "desc": "Change prompt. Ex. /prompt <prompt-name>", "cls": PromptPCommand },
    { "match": "/title", "desc": "Change title. Ex. /title <title-name>", "cls": TitlePCommand },
    { "match": "/exit", "desc": "Exit the program", "cls": ExitPCommand },
    { "match": "/quit", "desc": "Exit the program", "cls": ExitPCommand },
    { "match": "/help", "desc": "Show help", "cls": HelpPCommand },
]


class CommandCompleter(Completer):

    def get_completions(self, document, complete_event) -> t.Iterator[Completion]:
        if not document.text.startswith("/"):
            return
        pargs = split_command_line(document.text)
        if len(pargs) == 0:
            return
        input_cmd: str = pargs[0]
        input_args: t.List[str] = pargs[1:]
        matched_cls : t.Optional[t.Type[PCommandBase]] = None
        for cmd in PCOMMANDS:
            match: str = cmd.get("match")  # type: ignore
            if input_cmd == match:
                matched_cls: t.Type[PCommandBase] = cmd.get("cls")  # type: ignore
                break
            if match.startswith(input_cmd):
                yield Completion(
                    match,
                    start_position=-len(input_cmd),
                )
        if matched_cls is None:
            return
        pcommand = matched_cls()
        yield from pcommand.complete(input_cmd, input_args)
