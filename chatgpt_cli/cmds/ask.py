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
from chatgpt_cli.error import CommandError


def run_ask_cmd(question, stream_mode=True):
    session_mgr = chatapi.get_session_manager()
    current_session = session_mgr.current_session
    current_session.add_message(chatapi.ChatMessage(
        message=question,
        message_type=chatapi.ChatMessageType.USER,
    ))
    response = session_mgr.new_chat_completion(stream_mode)

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
    term.console.print("\n")
