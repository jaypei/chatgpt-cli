# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import openai
from rich.live import Live
from rich.markdown import Markdown

from chatgpt_cli import config
from chatgpt_cli import chatapi
from chatgpt_cli import term
from chatgpt_cli.error import CommandError, CommandExit


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
    current_session = chatapi.get_session_manager().current_session

    current_session.add_message(chatapi.ChatMessage(
        message=question,
        message_type=chatapi.ChatMessageType.USER,
    ))
    try:
        response = openai.ChatCompletion.create(
            model=config.get_config().get('DEFAULT', 'CHATGPT_MODEL'),
            messages=current_session.generate_query_messages(),
            temperature=0,
            stream=True,
        )
    except openai.error.RateLimitError as e:
        term.console.print(f"[bold red]Rate limit exceeded: {e}[/bold red]")
        raise CommandError("Rate limit exceeded", 2)

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
