import discord


# Fill in your Discord Bot's token here:
TOKEN = ''

# Fill in your announcements channel's ID here:
CHANNEL_ID = 444597426708414475


class Pizzatron3000(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}.'.format(self.user))

    async def on_message(self, message):
        print('[{0.author}] {0.content}'.format(message))
