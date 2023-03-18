# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import datetime
import enum
from typing import List, Dict

import attrs
import openai
from rich.live import Live
from rich.markdown import Markdown

from chatgpt_cli import config, term
from chatgpt_cli.error import CommandError


# define a enum type for ChatMessageType
class ChatMessageType(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ActMode(enum.Enum):
    ASSISTANT = "Assistant"
    TRANSLATOR = "Translator"


def system_content_by_act_mode(act_mode: ActMode) -> str:
    if act_mode == ActMode.ASSISTANT:
        return "You are a friendly and helpful teaching assistant."
    if act_mode == ActMode.TRANSLATOR:
        return "You are an English translator, spelling corrector and improver."
    raise ValueError("Invalid act_mode")

# pylint: disable=line-too-long
messages = [
    {"role": "system", "content": "You are a helpful, pattern-following assistant that translates corporate jargon into plain English."},
    {"role": "system", "name":"example_user", "content": "New synergies will help drive top-line growth."},
    {"role": "system", "name": "example_assistant", "content": "Things working well together will increase revenue."},
    {"role": "system", "name":"example_user", "content": "Let's circle back when we have more bandwidth to touch base on opportunities for increased leverage."},
    {"role": "system", "name": "example_assistant", "content": "Let's talk later when we're less busy about how to do better."},
    {"role": "user", "content": "This late pivot means we don't have time to boil the ocean for the client deliverable."},
]


@attrs.define
class ChatMessage:
    message : str
    message_type : ChatMessageType = attrs.field(validator=attrs.validators.in_(ChatMessageType))
    timestamp : int = attrs.field(factory=lambda: int(datetime.datetime.now().timestamp()))

    def to_message_json(self) -> dict:
        return {
            "role": self.message_type.value,
            "content": self.message,
        }


class ChatSession:

    histories : List[ChatMessage] = attrs.field(factory=list)

    def __init__(self, session_name: str, act_mode: ActMode):
        self.session_name : str = session_name
        self.act_mode : ActMode = act_mode
        self.histories : List[ChatMessage] = []
        self.conversation_count : int = 0
        self.histories.append(ChatMessage(
            message=system_content_by_act_mode(self.act_mode),
            message_type=ChatMessageType.SYSTEM,
        ))

    def generate_query_messages(self) -> list:
        query_messages = []
        for message in self.histories:
            query_messages.append(message.to_message_json())
        return query_messages

    def add_message(self, message: ChatMessage):
        self.histories.append(message)
        if message.message_type == ChatMessageType.USER:
            self.conversation_count += 1


class ChatSessionManager:

    def __init__(self):
        self.sessions : Dict[str, ChatSession] = {}
        self.current_session : ChatSession

    def get_session(self, session_name: str) -> ChatSession:
        if session_name not in self.sessions:
            self.sessions[session_name] = ChatSession(session_name, act_mode=ActMode.ASSISTANT)
        return self.sessions[session_name]

    def switch(self, session_name: str) -> ChatSession:
        self.current_session = self.get_session(session_name)
        return self.current_session

    def rename(self, old_name: str, new_name: str):
        if old_name in self.sessions:
            self.sessions[new_name] = self.sessions[old_name]
            del self.sessions[old_name]

    def create(self, session_name: str, auto_switch: bool=True) -> ChatSession:
        new_session = ChatSession(session_name, act_mode=ActMode.ASSISTANT)
        self.sessions[session_name] = new_session
        if auto_switch:
            self.switch(session_name)
        return new_session

    def _new_chat_completion(self, stream: bool) -> openai.ChatCompletion:
        try:
            response = openai.ChatCompletion.create(
                model=config.get_config().get('DEFAULT', 'CHATGPT_MODEL'),
                messages=self.current_session.generate_query_messages(),
                temperature=0,
                stream=stream,
            )
            return response
        except openai.error.RateLimitError as e:
            term.console.print(f"[bold red]Rate limit exceeded: {e}[/bold red]")
            raise CommandError("Rate limit exceeded", 2)

    def _single_output(self, console: term.Console, response: openai.ChatCompletion) -> str:
        output = []
        for chunk in response:
            delta_obj = chunk['choices'][0]['delta']
            content = delta_obj.get("content")
            if content is None:
                continue
            output.append(content)
        message = "".join(output)
        console.print(message)
        return message

    def _live_output(self, console: term.Console, response: openai.ChatCompletion) -> str:
        output = []
        with Live(console=console) as live:
            for chunk in response:
                delta_obj = chunk['choices'][0]['delta']
                content = delta_obj.get("content")
                if content is None:
                    continue
                output.append(content)
                md = Markdown("".join(output))
                live.update(md, refresh=True)
        return "".join(output)

    def ask(self, question: str, stream: bool, console: term.Console) -> str:
        self.current_session.add_message(ChatMessage(
            message=question,
            message_type=ChatMessageType.USER,
        ))
        response = self._new_chat_completion(stream=stream)
        answer = ""
        if not stream:
            answer = self._single_output(console, response)
        else:
            answer = self._live_output(console, response)
        self.current_session.add_message(ChatMessage(
            message=answer,
            message_type=ChatMessageType.ASSISTANT,
        ))
        return answer


_session_manager : ChatSessionManager


def get_session_manager() -> ChatSessionManager:
    global _session_manager
    return _session_manager


def init():
    global _session_manager
    openai.api_key = config.get_config().get('DEFAULT', 'OPENAI_API_KEY')
    _session_manager = ChatSessionManager()
    _session_manager.create('Chat01', auto_switch=True)


def is_valid_openai_api_key(key: str) -> bool:
    if not key.startswith('sk-'):
        return False
    return True
