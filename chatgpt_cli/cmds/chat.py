# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


from rich.live import Live
from rich.markdown import Markdown

from chatgpt_cli import chatapi
from chatgpt_cli import term
from chatgpt_cli.error import CommandExit
from chatgpt_cli import config


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


def print_chat_banner(version):
    term.console.print(CHAT_BANNER_LOGO.format(version=version), style="bold", highlight=False)
    term.console.print(CHAT_BANNER_INTRO)


def get_question():
    current_session = chatapi.get_session_manager().current_session
    while True:
        session_name = current_session.session_name
        conversation_count = current_session.conversation_count
        prompt_message = [
            ('class:session', f"{session_name} "),
            ('class:conversation_count',  f'{conversation_count} '),
            ('class:prompt_sep',  '> '),
        ]
        question = term.prompt.prompt(prompt_message)
        yield question


def ask_openai(question):
    session_mgr = chatapi.get_session_manager()
    current_session = session_mgr.current_session

    current_session.add_message(chatapi.ChatMessage(
        message=question,
        message_type=chatapi.ChatMessageType.USER,
    ))
    response = session_mgr.new_chat_completion(True)

    output = []
    with Live(console=term.console) as live:
        for chunk in response:
            delta_obj = chunk['choices'][0]['delta']
            content = delta_obj.get("content")
            if content is None:
                continue
            output.append(content)
            md = Markdown("".join(output))
            live.update(md, refresh=True)
        message = chatapi.ChatMessage(
            message="".join(output),
            message_type=chatapi.ChatMessageType.ASSISTANT,
        )
        current_session.add_message(message)

    term.console.print("\n")


def run_chat_loop():
    while True:
        try:
            for question in get_question():
                if question == "":
                    continue
                if question == "/hist":
                    current_session = chatapi.get_session_manager().current_session
                    for message in current_session.histories:
                        term.console.print(message.to_message_json())
                    continue
                if question in ("/exit", "/quit"):
                    raise CommandExit()
                ask_openai(question)
        except EOFError:
            raise CommandExit()
        except KeyboardInterrupt:
            term.console.print("If you want to exit, please press <Ctrl+D>.")
