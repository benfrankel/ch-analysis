import discord

from . import parse


def chunkify(response):
    chunks = ['']
    lines = response.splitlines()
    for line in lines:
        if len(line) > 2000:
            chunks.append(line[:1999] + '…')
        elif len(chunks[-1]) + len(line) + 1 > 2000:
            chunks.append(line)
        elif not chunks[-1]:
            chunks[-1] = line
        else:
            chunks[-1] += '\n' + line

    return chunks


class Client(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}.'.format(self.user))

    async def on_message(self, message):
        if message.author == self.user:
            return

        text = parse.get_text(message)
        if text is None:
            return

        print('[{0.author}] {0.content}'.format(message))
        command, args, raw_args = parse.parse(text)
        print('>', command.__name__, args, raw_args)

        async with message.channel.typing():
            response = command(args) or 'I have no words...'
            chunks = chunkify(response)
        for chunk in chunks:
            await message.channel.send(chunk)
