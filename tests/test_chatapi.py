import unittest
import json
from datetime import datetime

from chatgpt_cli.chatapi import ChatMessage, ChatMessageType, ChatSession, ActMode
from unittest.mock import Mock


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
    def test_generate_query_messages(self):
        chat_session = ChatSession("test_session", ActMode.ASSISTANT)
        chat_session.add_message(ChatMessage("test message", ChatMessageType.USER))
        chat_session.add_message(ChatMessage("system response", ChatMessageType.SYSTEM))
        chat_session.add_message(ChatMessage("test message 2", ChatMessageType.USER))

        expected_result = [
            ChatMessage("You are a friendly and helpful teaching assistant.", ChatMessageType.SYSTEM).to_message_json(),
            ChatMessage("test message", ChatMessageType.USER).to_message_json(),
            ChatMessage("system response", ChatMessageType.SYSTEM).to_message_json(),
            ChatMessage("test message 2", ChatMessageType.USER).to_message_json()
        ]
        self.assertEqual(chat_session.generate_query_messages(), expected_result)

    def test_add_message(self):
        chat_session = ChatSession("test_session", ActMode.ASSISTANT)
        chat_session.add_message(ChatMessage("test message", ChatMessageType.SYSTEM))
        chat_session.add_message(ChatMessage("test message 2", ChatMessageType.USER))

        self.assertEqual(len(chat_session.histories), 3)  # 3 messages including initial system message
        self.assertEqual(chat_session.histories[1].message, "test message")
        self.assertEqual(chat_session.histories[2].message, "test message 2")
        self.assertEqual(chat_session.conversation_count, 1)  # one user message added
