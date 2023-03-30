# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import unittest
from unittest.mock import Mock
from chatgpt_cli.cmds.base import BaseCmd, load_cmd


class TestCmdLoader(unittest.TestCase):
    
    def test_valid_cmd_name(self):
        cmd_name = "ChatCommand"
        cmd = load_cmd(cmd_name)
        self.assertIsInstance(cmd, BaseCmd)
    
    def test_invalid_cmd_name(self):
        cmd_name = "InvalidCommand"
        with self.assertRaises(ValueError):
            load_cmd(cmd_name)
    
    def test_no_such_module(self):
        cmd_name = "InvalidModuleCommand"
        with self.assertRaises(ValueError):
            load_cmd(cmd_name)
    
    def test_no_such_command(self):
        cmd_name = "InvalidCmd"
        with self.assertRaises(ValueError):
            load_cmd(cmd_name)
    
    def test_cmd_class_called(self):
        cmd_name = "ChatCommand"
        module = Mock()
        cmd_cls = Mock(return_value=BaseCmd())
        setattr(module, cmd_name, cmd_cls)
        with unittest.mock.patch("chatgpt_cli.cmds.base.importlib.import_module", return_value=module):
            cmd = load_cmd(cmd_name)
            cmd_cls.assert_called_once()
