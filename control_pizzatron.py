#!/usr/bin/env python3

import discord.errors

import pizzatron


def input_option_int(message):
    while True:
        choice = input(message)

        if not choice:
            return None

        try:
            return int(choice)
        except ValueError:
            pass


def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        while True:
            channels = list(filter(lambda c: isinstance(c, discord.TextChannel), client.get_all_channels()))
            print('\n'.join('{}. {}'.format(i + 1, channel) for i, channel in enumerate(channels)))
            print()

            choice = input_option_int('Pick a channel: ')
            if choice is None or not (1 <= choice <= len(channels)):
                break
            channel = channels[choice - 1]

            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.send_messages:
                print('\nSending messages on that channel is not permitted!\n')
                continue

            message = input('Send: ')
            if not message:
                print('\nNo message sent.\n')
                continue
            await channel.send(message)
            print()

        await client.close()

    client.run(pizzatron.TOKEN)


if __name__ == '__main__':
    main()
