from .const import TOKEN
from .client import Client


def announce(message):
    import discord
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(const.BOG_ANNOUNCEMENTS_CHANNEL_ID)
        await announcements.send(message)
        await client.close()

    client.run(TOKEN)


__all__ = []
