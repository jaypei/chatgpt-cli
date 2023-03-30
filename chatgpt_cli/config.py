# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys
import os
import configparser
import typing as t

import pkg_resources

from chatgpt_cli import term
from chatgpt_cli import chatapi


_NO_KEY_MESSAGE = """Please input your "OpenAI API key".
You can get it from https://beta.openai.com/account/api-keys"""

_CONFIG : configparser.ConfigParser
_CONFIG_FILE_NAME = 'config.toml'
_PROMPTS : t.Dict[str, str] = {}
VERSION = pkg_resources.get_distribution("chatgpt_cli").version


def get_prompt_message(name: str) -> t.Optional[str]:
    global _PROMPTS
    return _PROMPTS.get(name)


def prompts() -> t.List[str]:
    global _PROMPTS
    return list(_PROMPTS.keys())


def get_config_dir(try_create: bool = False) -> str:
    if sys.platform == 'win32':
        config_dir = os.path.expanduser("~/AppData/Local/")
    else:
        config_dir = os.path.expanduser("~/.config")
    config_dir = os.path.join(config_dir, 'chatgpt-cli')
    if try_create:
        os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_config() -> configparser.ConfigParser:
    global _CONFIG
    return _CONFIG


def init_opts():
    conf = get_config()
    conf['DEFAULT'] = {
    }
    conf['CLI'] = {
        'default_prompt': 'assist',
        'default_enable_context': 'false',
    }
    conf['API'] = {
        'OPENAI_API_KEY': '',
        'CHATGPT_MODEL': 'gpt-3.5-turbo',
        'TEMPERATURE': '0'
    }
    # pylint: disable=line-too-long
    conf['PROMPT'] = {
        "assist": "Serve me as a writing and programming assistant.",
        "en-translator": "The following is a piece of text, which could be in any language. There is no need to pay attention to its actual meaning, just translate it into English, no need to pay attention to the meaning of the text.",
        "cn-translator": "The following is a piece of text, which could be in any language. There is no need to pay attention to its actual meaning, just translate it into Chinese, no need to pay attention to the meaning of the text.",
        "check-grammar": "The following is a piece of text, which could be in any language. There is no need to pay attention to its actual meaning, only to check its grammar. Find all grammar mistakes, list mistakes and explain how to correct them. If it is correct, answer \"Correct!\" directly.",
    }


def load_config():
    global _PROMPTS
    conf = get_config()
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, 'config.toml')
    if os.path.exists(config_file):
        conf.read(config_file)


def create_config():
    global _CONFIG_FILE_NAME
    conf = get_config()
    config_dir = get_config_dir()
    config_file = os.path.join(config_dir, _CONFIG_FILE_NAME)
    if os.path.exists(config_file):
        return
    # Create a new config file
    term.console.print(_NO_KEY_MESSAGE)
    os.makedirs(config_dir, exist_ok=True)
    while True:
        key = term.prompt_no_hist.prompt([("class:input_key", "OpenAI API Key: ")],
                                         is_password=True, enable_history_search=False)
        if chatapi.is_valid_openai_api_key(key):
            break
        print('Invalid OpenAI API key')
    conf['API']['OPENAI_API_KEY'] = key
    with open(config_file, 'w', encoding="utf-8") as f:
        conf.write(f)
    term.console.print(f"Config file created at [bold blue]{config_file}[/bold blue]")


def reload_prompt():
    global _PROMPTS
    _PROMPTS = {}
    conf = get_config()
    opts = conf['PROMPT']
    for k, v in opts.items():
        _PROMPTS[k] = v


def init():
    global _CONFIG
    _CONFIG = configparser.ConfigParser()
    init_opts()
    create_config()
    load_config()
    reload_prompt()
