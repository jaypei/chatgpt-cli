# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import datetime
import enum
from typing import List, Dict

import attrs
import openai

from chatgpt_cli import config


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
        self.sessions : Dict[ChatSession] = {}
        self.current_session : ChatSession = None

    def get_session(self, session_name: str) -> ChatSession:
        if session_name not in self.sessions:
            self.sessions[session_name] = ChatSession(session_name, act_mode=ActMode.ASSISTANT)
        return self.sessions[session_name]

    def switch(self, session_name: str) -> ChatSession:
        self.current_session = self.get_session(session_name)

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


_session_manager : ChatSessionManager = None


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
