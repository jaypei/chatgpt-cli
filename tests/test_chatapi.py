# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import unittest

from chatgpt_cli.chatapi import ChatMessage, ChatMessageType, ChatSession
from chatgpt_cli.config import init as init_config
from chatgpt_cli.config import get_config, reload_prompt


class TestChatMessage(unittest.TestCase):

    def test_to_message_json(self):

        test_message = ChatMessage(
            message="You are a helpful, pattern-following assistant that translates corporate jargon into plain English.",
            message_type=ChatMessageType.SYSTEM,
        )

        expected_output = {
            "role": "system",
            "content": "You are a helpful, pattern-following assistant that translates corporate jargon into plain English."
        }

        self.assertEqual(test_message.to_message_json(), expected_output)



class TestChatSession(unittest.TestCase):

    def setUp(self):
        init_config()
        conf = get_config()
        conf.set('CLI', 'default_prompt', 'assist')
        conf.set('CLI', 'default_enable_context', 'True')
        conf.set('PROMPT', 'assist', 'TEST ASSIST')
        reload_prompt()

    def test_generate_query_messages(self):
        chat_session = ChatSession("test_session", "assist")
        chat_session.add_message(ChatMessage("test message", ChatMessageType.USER))
        chat_session.add_message(ChatMessage("system response", ChatMessageType.SYSTEM))
        chat_session.add_message(ChatMessage("test message 2", ChatMessageType.USER))

        expected_result = [
            ChatMessage("TEST ASSIST\n\ntest message", ChatMessageType.USER).to_message_json(),
            ChatMessage("system response", ChatMessageType.SYSTEM).to_message_json(),
            ChatMessage("TEST ASSIST\n\ntest message 2", ChatMessageType.USER).to_message_json()
        ]
        self.assertEqual(chat_session.generate_query_messages(), expected_result)

    def test_add_message(self):
        chat_session = ChatSession("test_session", "assist")
        chat_session.add_message(ChatMessage("test message", ChatMessageType.SYSTEM))
        chat_session.add_message(ChatMessage("test message 2", ChatMessageType.USER))

        self.assertEqual(len(chat_session.histories), 2)
        self.assertEqual(chat_session.histories[0].message, "test message")
        self.assertEqual(chat_session.histories[1].message, "TEST ASSIST\n\ntest message 2")
        self.assertEqual(chat_session.conversation_count, 1)
