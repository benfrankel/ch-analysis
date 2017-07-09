import discord


# Fill in your Discord Bot's token here:
TOKEN = ''

# Fill in your announcements channel's ID here:
CHANNEL_ANNOUNCE = ''


def announce(message):
    client = discord.Client()

    @client.event
    async def on_ready():
        announcements = client.get_channel(CHANNEL_ANNOUNCE)
        await client.send_message(announcements, message)
        await client.logout()

    client.run(TOKEN)
