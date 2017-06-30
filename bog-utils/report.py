#!/usr/bin/env python3.6

import discord


TOKEN = 'MzI5NjQzMTkzOTQxNDkxNzEz.DDVe8w.9-wnZUGZGKbHfQ2Ee23heskf7Co'
CHANNEL_ID = '263901795422699521'


def announce(message):
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(CHANNEL_ID)
        await client.send_message(announcements, message)
        await client.logout()

    client.run(TOKEN)


def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(CHANNEL_ID)
        while True:
            message = input('Announce: ')
            if not message:
                break
            await client.send_message(announcements, message)
        await client.logout()

    client.run(TOKEN)


if __name__ == '__main__':
    main()
