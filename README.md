# chatgpt-cli

A ChatGPT CLI tool based on the OpenAI API, for hardcore terminal users.

[![check](https://github.com/jaypei/chatgpt-cli/actions/workflows/check.yml/badge.svg?branch=main)](https://github.com/jaypei/chatgpt-cli/actions/workflows/check.yml)

## Demo

[![demo](https://asciinema.org/a/568562.svg)](https://asciinema.org/a/568562?autoplay=1)

## Usage

You need to first open [HERE](https://beta.openai.com/account/api-keys) to get a valid API Key.

```sh
# Install
pip install git+https://github.com/jaypei/chatgpt-cli

# Ask directly without keeping any context.
chatgpt-cli ask <question>

# Start a chat session, so that we can have a conversation with context.
chatgpt-cli chat

# Have fun!
```
