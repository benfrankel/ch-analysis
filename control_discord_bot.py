#!/usr/bin/env python3.6

from util.guild.chat import TOKEN, CHANNEL_ID
import discord


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
