#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: shimarin
# Created: 2023-12-16

import sys,argparse
from slack_sdk import WebClient

def load_token_file(filename):
    with open(filename) as f:
        return f.read().strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to slack channel')
    parser.add_argument('--bot-token-file', type=str, default="/etc/slack/bot-token", help='Slack bot token')
    parser.add_argument('--plaintext', action='store_true', help='Disable markdown')
    parser.add_argument('channel', help='Channel name')
    parser.add_argument('message', nargs='?', type=str, default=None, help='Mesage to send')
    args = parser.parse_args()

    token = load_token_file(args.bot_token_file)

    if not args.message: args.message = sys.stdin.read().strip()

    client = WebClient(token=token)
    #print("channel=%s" % (args.channel))
    response = client.chat_postMessage(channel=args.channel, text=args.message,mrkdwn=not args.plaintext)