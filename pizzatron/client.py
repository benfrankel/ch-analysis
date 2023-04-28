import datetime
import time
import traceback

import asyncio
import discord

import gamedata
import metadata
import party
from util import scrape
from . import commands
from . import const
from . import display
from . import parse
from . import parse_util
from . import state


_MESSAGE_CHARACTER_LIMIT = 2000


def _chunkify(text):
    chunks = []
    lines = text.splitlines()
    for line in lines:
        # Append line to the previous chunk if it will fit in the same message
        remaining = _MESSAGE_CHARACTER_LIMIT - len(chunks[-1]) - 1 - len(line) if chunks else -1
        if remaining >= 0 and not (remaining == 0 and line and line[-1].isspace()):
            chunks[-1] += '\n' + line
            continue

        # Append a zero-width space to preserve formatting (Discord strips whitespace at the end of each message)
        if chunks and chunks[-1][-1].isspace():
            chunks[-1] += '\u200b'
        
        # Prepend a zero-width space to preserve formatting (Discord strips whitespace at the beginning of each message)
        if not line or line[0].isspace():
            line = '\u200b' + line

        # Truncate line if it won't fit in one message
        remaining = _MESSAGE_CHARACTER_LIMIT - len(line)
        if remaining < 0 or (remaining == 0 and line[-1].isspace()):
            line = line[:_MESSAGE_CHARACTER_LIMIT - 1] + '…'

        chunks.append(line)

    return chunks


class Client(discord.Client):
    def __init__(self):
        super().__init__()

        self._tasks_started = False
        self._message_locks = {}
        
        self.game = gamedata.Manager()
        self.meta = metadata.Manager()
        self.state = state.Manager()
        self.display = display.Manager()
        self.party = party.Manager()
        self.parse = parse.Manager()

    def load(self):
        self.game.load()
        self.meta.load()
        self.state.load()
        self.display.load()
        self.party.load(self.game)
        self.parse.load(self.game)

    def reload(self):
        self.game.reload()
        self.meta.reload()
        self.state.reload()
        self.display.reload()
        self.party.reload(self.game)
        self.parse.reload(self.game)

    async def send(self, target, text):
        chunks = _chunkify(text)
        async with self._message_locks.setdefault(target.id, asyncio.Lock()):
            message = await target.send(chunks[0])
            for chunk in chunks[1:]:
                await target.send(chunk)
    
        return message
    
    async def reply(self, message, text):
        chunks = _chunkify(text)
        async with self._message_locks.setdefault(message.channel.id, asyncio.Lock()):
            reply = await message.reply(chunks[0])
            for chunk in chunks[1:]:
                await message.channel.send(chunk)
    
        return reply

    async def pin(self, message):
        async with self._message_locks.setdefault(message.channel.id, asyncio.Lock()):
            return await message.pin()
    
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
                    adventure = self.game.get_adventure(adventure)
                except KeyError:
                    loot_fairy = f' from **{adventure}** '
                else:
                    loot_fairy = f' from **{adventure.display_name} (lvl {adventure.level})** '

        # Update loot fairy message with results
        loot_fairy_channel = self.get_channel(const.CH_LOOT_FAIRY_CHANNEL_ID)
        loot_fairy_msg = await loot_fairy_channel.fetch_message(const.CH_LOOT_FAIRY_MESSAGE_ID)
        await loot_fairy_msg.edit(content=f'The Loot Fairy will move{loot_fairy}in **{hours}:{minutes:02d}** hours!\n({scrape.LOOT_FAIRY_TRACKER_URL})')


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
            args, raw_args = parse_util.tokenize(item_name)
            item, *_ = self.parse.item_matcher.parse(args, raw_args)
            if item is not None:
                items.append(item)

        legendaries = items[:1]
        epics = items[1:4]
        rares = items[4:]
        cards_on_rares = set(c for i in rares for c in i.cards)
        rare_cards = list(set(c for c in cards_on_rares if c.is_rare))
        
        message = f"""Daily deal for **{date}**:

{self.display.items_long(legendaries, sort=True)}

{self.display.items_long(epics, sort=True)}

{self.display.items_long(rares, sort=True)}

**Rare Cards:** {self.display.cards_long(rare_cards, sort=True)}"""

        # Send a message with today's daily deal items and pin it
        message = await self.send(daily_deal_channel, message)
        await self.pin(message)

        if most_recent is not None:
            await most_recent.unpin()

        for user_id, wishlist in self.state.wishlists.items():
            # TODO: Provide from_json in self.state for convenience?
            wish_items = set(gamedata.ItemType.from_json(self.game, i) for i in wishlist['items'])
            wish_cards = set(gamedata.CardType.from_json(self.game, c) for c in wishlist['cards'])
            overlap_items = wish_items & set(items)
            overlap_cards = wish_cards & cards_on_rares
            if not overlap_items and not overlap_cards:
                continue

            user = await self.fetch_user(int(user_id))
            if user is not None:
                items_str = self.display.items_long(list(overlap_items), sort=True) if overlap_items else ''
                cards_str = f'**Cards:** {self.display.cards_long(list(overlap_cards), sort=True)}' if overlap_cards else ''
                if overlap_items:
                    cards_str = '\n\n' + cards_str
                await self.send(user, f'Check out today\'s Daily Deal!\n{items_str}{cards_str}')


    async def update_battle_history(self):
        for x in await self.meta.download():
            # TODO: Magic constant
            account_add_scenario_hash = '496cb44a8fbcc45fedeafde42863f6da'
            if not self.meta.is_scenario(x, account_add_scenario_hash):
                continue

            winner = self.meta.winner_name(x)
            start_time = self.meta.start_timestamp(x)
            for user_id, add_attempts in self.state.account_add_attempts.items():
                if winner not in add_attempts:
                    continue
                idx = add_attempts.index(winner)

                add_attempts_start = self.state.account_add_attempts_start[user_id]
                add_attempts_reset = self.state.account_add_attempts_reset[user_id]
                if not add_attempts_start[idx] <= start_time < add_attempts_reset[idx]:
                    continue

                del add_attempts[idx]
                del add_attempts_start[idx]
                del add_attempts_reset[idx]
                self.state.accounts.setdefault(user_id, []).append(winner)
                self.state.save()

                user = await self.fetch_user(int(user_id))
                if user is not None:
                    await self.send(user, f'Successfully added "{winner}" to your CH account list!')


    async def update_account_lists(self):
        now = time.time()
        for user_id, add_attempts in self.state.account_add_attempts.items():
            add_attempts_start = self.state.account_add_attempts_start[user_id]
            add_attempts_reset = self.state.account_add_attempts_reset[user_id]
            idx = 0
            while idx < len(add_attempts):
                if now > add_attempts_reset[idx]:
                    account_name = add_attempts[idx]
                    del add_attempts[idx]
                    del add_attempts_start[idx]
                    del add_attempts_reset[idx]
                    self.state.save()

                    user = await self.fetch_user(int(user_id))
                    if user is not None:
                        await self.send(user, f'Your attempt to add "{account_name}" to your CH account list has timed out.')
                
                    continue
            
                idx += 1


    async def on_ready(self):
        print('Logged on as {0}.'.format(self.user))

        if self._tasks_started:
            return

        async def loop(task):
            while True:
                try:
                    await task()
                except:
                    traceback.print_exc()
                await asyncio.sleep(60)

        asyncio.create_task(loop(self.update_loot_fairy))
        asyncio.create_task(loop(self.update_daily_deal))
        asyncio.create_task(loop(self.update_account_lists))
        asyncio.create_task(loop(self.update_battle_history))

        self._tasks_started = True


    async def on_message(self, msg):
        if msg.author == self.user:
            return

        text = parse.get_text(msg)
        if text is None:
            return

        args, raw_args = parse_util.tokenize(text)
        command, args, raw_args = commands.COMMAND_MATCHER.parse_start_or_end(args, raw_args)
        parser = parse.Parser(self.game, self.parse, args, raw_args)

        print()
        print(msg.created_at)
        print(f'[{msg.author}] {msg.content}')
        print('>', command.__name__, args, raw_args)

        async with msg.channel.typing():
            try:
                await command(self, msg, parser)
            except parse.ParseError as e:
                await self.reply(msg, f'`{command.__name__}`: {e}')
            except:
                await self.reply(msg, 'Error... You found a bug!')
                raise
