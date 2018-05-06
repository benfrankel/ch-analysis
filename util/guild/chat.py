import discord


# Fill in your Discord Bot's token here:
TOKEN = 'MzI5NjQzMTkzOTQxNDkxNzEz.DDVe8w.9-wnZUGZGKbHfQ2Ee23heskf7Co'

# Fill in your announcements channel's ID here:
CHANNEL_ID = '334114051967680513'


def announce(message):
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(CHANNEL_ID)
        await client.send_message(announcements, message)
        await client.logout()

    client.run(TOKEN)
