# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


class CommandError(Exception):

    def __init__(self, message, exit_code=1):
        self.message = message
        self.exit_code = exit_code


class CommandExit(Exception):
    pass
