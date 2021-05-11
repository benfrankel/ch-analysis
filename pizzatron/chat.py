import datetime
import time
import traceback

import asyncio
import discord

import gamedata
from util import scrape
from . import const
from . import display
from . import parse
from . import parse_util


def chunkify(text):
    chunks = ['']
    lines = text.splitlines()
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


async def send_chunked(channel, text):
    chunks = chunkify(text)
    message = await channel.send(chunks[0])
    for chunk in chunks[1:]:
        await channel.send(chunk)

    return message


async def reply_chunked(message, text):
    chunks = chunkify(text)
    reply = await message.reply(chunks[0])
    for chunk in chunks[1:]:
        await message.channel.send(chunk)

    return reply


class Client(discord.Client):
    async def update_loot_fairy(self):
        # Loot fairy moves every 25 hours
        period = 25 * 60 * 60
        offset = 0

        # Calculate time until next move
        delta = offset - (int(time.time()) % period)
        if delta < 0:
            delta += period
        delta //= 60
        minutes = delta % 60
        delta //= 60
        hours = delta

        # Scrape loot fairy tracker to see if today's adventure was found
        adventures = scrape.loot_fairy_tracker()
        loot_fairy = ' '
        for adventure, found in adventures.items():
            if found:
                try:
                    adventure = gamedata.get_adventure(adventure)
                except KeyError:
                    loot_fairy = f' from **{adventure}** '
                else:
                    loot_fairy = f' from **{adventure.display_name} (lvl {adventure.level})** '

        # Update loot fairy message with results
        loot_fairy_channel = self.get_channel(const.CH_LOOT_FAIRY_CHANNEL_ID)
        loot_fairy_msg = await loot_fairy_channel.fetch_message(const.CH_LOOT_FAIRY_MESSAGE_ID)
        await loot_fairy_msg.edit(content=f'The Loot Fairy will move{loot_fairy}in **{hours}:{minutes:02d}** hours!')

    async def update_daily_deal(self):
        # Check current pins
        daily_deal_channel = self.get_channel(const.CH_DAILY_DEAL_CHANNEL_ID)
        pins = await daily_deal_channel.pins()
        most_recent = None
        for pin in pins:
            if pin.author == self.user:
                most_recent = pin
                break

        today = datetime.datetime.utcnow().date()
        if most_recent is not None:
            date = most_recent.content[len('Daily deal for **'):most_recent.content.find('\n')-len('**:')]
            try:
                date = datetime.date.fromisoformat(date)
            except ValueError:
                pass
            else:
                if date == today:
                    return

        # Scrape daily deal forum thread
        info = scrape.daily_deal()
        date = datetime.date.fromisoformat(info['date'][-4:] + '-' + info['date'][:-5])
        if date != today:
            return
        done = info['done']
        if not done:
            return

        items = []
        for item_name in info['items']:
            args = parse_util.tokenize(item_name)
            item, *_ = parse.parse_item(args, args)
            if item is not None:
                items.append(item)

        legendaries = items[:1]
        epics = items[1:4]
        rares = items[4:]
        message = f"""{display.items(legendaries, sort=True)}

{display.items(epics, sort=True)}

{display.items(rares, sort=True)}"""

        # Send a message with today's daily deal items and pin it
        message = await send_chunked(daily_deal_channel, f'Daily deal for **{date}**:\n\n{message}')
        await message.pin()

        if most_recent is not None:
            await most_recent.unpin()

    async def on_ready(self):
        print('Logged on as {0}.'.format(self.user))

        while True:
            try:
                await self.update_loot_fairy()
            except:
                traceback.print_exc()
            try:
                await self.update_daily_deal()
            except:
                traceback.print_exc()
            await asyncio.sleep(60)

    async def on_message(self, message):
        if message.author == self.user:
            return

        text = parse.get_text(message)
        if text is None:
            return

        print('[{0.author}] {0.content}'.format(message))
        command, args, raw_args = parse.parse(text)
        print('>', command.__name__, args, raw_args)

        error = None
        async with message.channel.typing():
            try:
                response = await command(args, raw_args) or 'I have no words...'
            except Exception as e:
                error = e
                response = 'Error... You found a bug!'
        await reply_chunked(message, response)

        if error is not None:
            raise error
