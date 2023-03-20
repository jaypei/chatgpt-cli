# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys
import typing as t

from prompt_toolkit.formatted_text import AnyFormattedText

from chatgpt_cli import chatapi
from chatgpt_cli import term
from chatgpt_cli import error
from chatgpt_cli import config
from chatgpt_cli.cmds.base import BaseCmd


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
Type '/exit' or <Ctrl-D> to exit the program.
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
        current_session = chatapi.get_session_manager().current_session
        while True:
            session_name = current_session.session_name
            conversation_count = current_session.conversation_count
            prompt_message :AnyFormattedText = [
                ('class:session', f"{session_name} "),
                ('class:conversation_count',  f'{conversation_count} '),
                ('class:prompt_sep',  '> '),
            ]
            question = term.prompt.prompt(prompt_message)
            yield question

    def ask_openai(self, question):
        session_mgr = chatapi.get_session_manager()
        session_mgr.ask(question, stream=True, console=term.console)
        term.console.print("\n")

    def run_chat_loop(self):
        while True:
            try:
                for question in self.get_question():
                    if question == "":
                        continue
                    if question == "/hist":
                        current_session = chatapi.get_session_manager().current_session
                        for message in current_session.histories:
                            term.console.print(message.to_message_json())
                        continue
                    if question in ("/exit", "/quit"):
                        raise error.CommandExit()
                    self.ask_openai(question)
            except EOFError:
                raise error.CommandExit()
            except KeyboardInterrupt:
                term.console.print("If you want to exit, please press <Ctrl+D>.")
