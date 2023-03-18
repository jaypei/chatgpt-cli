# -*- coding: utf-8 -*-
#
# Copyright 2023, JayPei <jaypei97159@gmail.com>
#


import sys
import os
import configparser

import pkg_resources

from chatgpt_cli import term
from chatgpt_cli import chatapi


_CONFIG : configparser.ConfigParser
_CONFIG_FILE_NAME = 'config.toml'
VERSION = pkg_resources.get_distribution("chatgpt_cli").version


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
        'OPENAI_API_KEY': '',
        'CHATGPT_MODEL': 'gpt-3.5-turbo'
    }


def load_config():
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
    term.console.print("Please input your \"OpenAI API key\". "
                       "You can get it from https://beta.openai.com/account/api-keys")
    os.makedirs(config_dir, exist_ok=True)
    while True:
        key = term.prompt_no_hist.prompt([("class:input_key", "OpenAI API Key: ")],
                                         is_password=True, enable_history_search=False)
        if chatapi.is_valid_openai_api_key(key):
            break
        print('Invalid OpenAI API key')
    conf['DEFAULT']['OPENAI_API_KEY'] = key
    with open(config_file, 'w', encoding="utf-8") as f:
        conf.write(f)
    term.console.print(f"Config file created at [bold blue]{config_file}[/bold blue]")


def init():
    global _CONFIG
    _CONFIG = configparser.ConfigParser()
    init_opts()
    create_config()
    load_config()
