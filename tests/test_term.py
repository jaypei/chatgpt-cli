# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import unittest

from chatgpt_cli.term import split_command_line


class TestSplitCommandLine(unittest.TestCase):
    
    def test_empty_string(self):
        result = split_command_line("")
        self.assertEqual(result, [])

    def test_simple_command(self):
        result = split_command_line("ls -la")
        self.assertEqual(result, ["ls", "-la"])

    def test_command_with_quotes(self):
        result = split_command_line('grep "error message" /var/log/messages')
        self.assertEqual(result, ["grep", "error message", "/var/log/messages"])

    def test_command_with_backslash(self):
        result = split_command_line(r"echo I\'m fine")
        self.assertEqual(result, ["echo", "I'm", "fine"])
