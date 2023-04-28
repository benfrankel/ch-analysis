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


async def _upload_emoji(client):
    # Get list of servers
    channels = [c for c in client.get_all_channels()]
    guilds = list(set(c.guild for c in channels))
    guilds.sort(key=lambda g: str(g))

    # Get list of item image names
    import gamedata
    gamedata.load()
    items = gamedata.get_items()
    image_names = list(set(i.image_name for i in items if not i.is_default_item))
    image_names.sort()

    # Create emoji for each item image, starting at ith image
    i = 0
    choice = -1
    while i < len(image_names) and choice < len(guilds) - 1:
        # Try next server
        choice += 1
        guild = guilds[choice]

        # Check for permission to create emojis in this server
        permissions = guild.me.guild_permissions
        if not permissions.manage_emojis:
            continue

        # Count existing emoji in the server to avoid hitting the limit (50)
        emojis = await guild.fetch_emojis()
        num_emoji = len(emojis)

        # Upload emoji to the server
        while i < len(image_names) and num_emoji < 50:
            # Download item image from CH live server
            image_name = image_names[i]
            try:
                image_path = gamedata.download_item_image(image_name)
            except Exception:
                print(f'        # Skipped: {image_name}')
                i += 1
                continue

            # Upload item image to server as emoji
            with open(image_path, 'rb') as f:
                # Get image as bytes
                image = f.read()

                # Create legal emoji name from image name
                name = ''.join(c if c.isalpha() or c.isnumeric() else '_' for c in image_name)

                # Upload emoji
                try:
                    emoji = await guild.create_custom_emoji(name=name, image=image)
                except Exception:
                    break

                # Print line for image name -> emoji ID map
                print("        '", image_name.replace("'", "\\'"), f"': '<:{emoji.name}:{emoji.id}>',", sep='')
                num_emoji += 1
                i += 1

    # If not all item images could be uploaded, mark which one to start with next time
    print('Next i:', i)
    await client.close()


def main():
    client = discord.Client()

    @client.event
    async def on_ready():
        while True:
            channels = [c for c in client.get_all_channels() if isinstance(c, discord.TextChannel)]
            channels.sort(key=lambda c: (str(c.guild), str(c.category), str(c)))
            print('\n'.join(f'{i + 1}. {c.guild} > {c.category} > {c}' for i, c in enumerate(channels)))
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
