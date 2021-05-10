from .const import TOKEN
from .chat import Client


def load():
    import gamedata
    gamedata.load()

    import optimize
    optimize.load()

    from . import parse
    parse.load()


def announce(message):
    import discord
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(const.BOG_ANNOUNCEMENTS_CHANNEL_ID)
        await announcements.send(message)
        await client.close()

    client.run(TOKEN)


__all__ = ['TOKEN', 'Client']
