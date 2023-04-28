import collections
import random
import time

from . import parse
from . import parse_util
from gamedata import CardType, ItemType
from party import Party


HELP = """\
What can I do for you?
```
help        Display this help.
info        Display information about a card or item.
items       List items containing a given card.
optimize    Calculate an optimal deck from card weights.
wishlist    Display your Daily Deal wishlist.
party       Display a party from a `partydiscordcode`.
```
Try some of these commands:
```
pt raging battler
pt bless
pt help optimize
pt optimize dwarf priest greater heal
pt wishlist add asmod's telekinetic chain
```\
"""


##################
# ADMIN COMMANDS #
##################

async def cmd_reload(ctx, msg, parser):
    user_id = str(msg.author.id)

    if user_id not in ctx.state.admins:
        await ctx.reply(msg, 'Must be a Pizzatron admin to use that command.')
        return

    ctx.reload()

    await ctx.reply(msg, 'Successfully reloaded.')


##################
# USAGE COMMANDS #
##################

async def cmd_empty(ctx, msg, parser):
    if not parser.args:
        await ctx.reply(msg, 'No command provided. Try `pt help` for a list of commands.')
        return

    query = ' '.join(parser.args)
    results = ctx.parse.any_matcher.search(query, score_gap=100)
    if not results:
        await ctx.reply(msg, 'Command not recognized, and no results found. Try `pt help` for a list of commands, or double-check your spelling.')
        return

    suggestions = ''
    if len(results) > 1:
        suggestions = '\n\n*(Other results: ' + ', '.join(ctx.display.any_short(r) for r in results[1:]) + ')*'

    await ctx.reply(msg, ctx.display.any_long(results[0]) + suggestions)
    

async def cmd_help(ctx, msg, parser):
    if parser.args and parser.args[0] == 'optimize':
        card_packs = '- ' + '\n- '.join(sorted(ctx.party.card_packs.keys()))
        await ctx.reply(msg, f'**Card Packs:**\n{card_packs}')
        return

    await ctx.reply(msg, HELP)


######################
# GAME DATA COMMANDS #
######################

def build_cmd_reply(text):
    async def cmd_reply(ctx, msg, parser):
        await ctx.reply(msg, text)

    return cmd_reply


async def cmd_any_info(ctx, msg, parser):
    results = parser.any_search()

    suggestions = ''
    if len(results) > 1:
        suggestions = '\n\n*(Other results: ' + ', '.join(ctx.display.any_short(r) for r in results[1:]) + ')*'

    await ctx.reply(msg, ctx.display.any_long(results[0]) + suggestions)


async def cmd_item_info(ctx, msg, parser):
    results = parser.item_search()

    suggestions = ''
    if len(results) > 1:
        suggestions = '\n\n*(Other results: ' + ', '.join(ctx.display.item_short(r) for r in results[1:]) + ')*'

    await ctx.reply(msg, ctx.display.item_long(results[0]) + suggestions)


async def cmd_card_info(ctx, msg, parser):
    results = parser.card_search()

    suggestions = ''
    if len(results) > 1:
        suggestions = '\n\n*(Other results: ' + ', '.join(ctx.display.card_short(r) for r in results[1:]) + ')*'

    await ctx.reply(msg, ctx.display.card_long(results[0]) + suggestions)


def build_cmd_list_items(include=lambda item: True):
    async def cmd_list_items(ctx, msg, parser):
        card = parser.card()

        items = []
        for item in ctx.game.items:
            if include(item) and card in item.cards:
                items.append(item)

        if not items:
            await ctx.reply(msg, f'No items found with the card "{card.name}".')
            return

        await ctx.reply(msg, ctx.display.items_long(items, sort=True, highlight_card=lambda x: x == card))
    
    return cmd_list_items


async def cmd_pool(ctx, msg, parser):
    param_pools = (
        (
            'Radioactive Handicap',
            lambda c: c.is_radioactive_card,
            (
                'radioactive handicap',
                'radioactive bomb',
                'radioactive bolt',
                'radiation handicap',
                'radiation bomb',
                'radiation bolt',
                'rad handicap',
                'rad bomb',
                'rad bolt',
                'handicap',
                'bomb',
                'bolt',
                'destructive purge',
                'des purge',
            ),
        ),
        (
            'Genetic Boost',
            lambda c: c.is_genetic_card,
            (
                'genetic boost',
                'genetic engineering',
                'genetic therapy',
                'gene boost',
                'gene engineering',
                'gene therapy',
                'boost',
                'engineering',
                'therapy',
            ),
        ),
        (
            'Fungal Twist',
            lambda c: c.is_fungal_twist_card,
            (
                'fungal twist',
                'twist minds',
            ),
        ),
        (
            'Laser Malfunction',
            lambda c: c.is_laser_malfunction_card,
            (
                'laser malfunction',
                'malfunction',
                'laser fail',
                'fail',
            ),
        ),
        (
            'Lycanthropic Form',
            lambda c: c.is_werewolf_card,
            (
                'lycanthropic form',
                'werewolf form',
                'wolf form',
                'howl',
            ),
        ),
        (
            'Ethereal Form',
            lambda c: c.is_spirit_card,
            (
                'ethereal form',
                'spirit form',
                'ghost form',
                'mediums garb',
                'garb',
            ),
        ),
        (
            'Vampiric Form',
            lambda c: c.is_vampire_card,
            (
                'vampiric form',
                'vampire form',
                'vamp form',
                'vampire kiss',
                'kiss',
            ),
        ),
        (
            'Zombie Form',
            lambda c: c.is_zombie_card,
            (
                'zombie form',
                'spark of undeath',
            ),
        ),
        (
            'Sculptorly Form',
            lambda c: c.is_sculptor_card,
            (
                'sculptorly form',
                'sculptor form',
                'sculpture form',
                'sculpt form',
                'sculp form',
             )
        ),
        (
            'Piratic Form',
            lambda c: c.is_pirate_card,
            (
                'piratic form',
                'pirate form',
                'piracy form',
                'pir form',
                'sailor form',
            ),
        ),
        (
            'Pixish Form',
            lambda c: c.is_pixie_card,
            (
                'pixish form',
                'pixie form',
                'pix form',
            )
        ),
        (
            'Form',
            lambda c: c.is_form_card,
            (
                'forms',
                'shifting block forms',
            )
        ),
        (
            'Walpurgis Form',
            lambda c: c.is_walpurgis_form_card,
            (
                'walpurgis night forms',
                'walpurgis forms',
                'castle mitternacht forms',
                'cm forms',
            )
        ),
        (
            'Hook',
            lambda c: c.is_hook_card,
            (
                'hook',
                'hemorrhage',
            )
        ),
        (
            'Meal',
            lambda c: c.is_meal_card,
            (
                'meal',
                'morsel',
                'edible',
            ),
        ),
        (
            'Push the Button',
            lambda c: c.is_melee and c.is_attack and c.damage_type == 'Laser' and c.is_implemented,
            (
                'push the button',
                'push button',
                'button',
            ),
        ),
        (
            'Pull the Trigger',
            lambda c: c.is_magic and c.is_attack and c.damage_type == 'Laser' and c.is_implemented,
            (
                'pull the trigger',
                'pull trigger',
                'trigger',
            ),
        ),
    )

    pool_alias_map = {}
    for name, in_pool, aliases in param_pools:
        cards = sorted(filter(in_pool, ctx.game.cards), key=ctx.display.by_type_quality_name)
        for alias in aliases:
            pool_alias_map[alias] = (name, cards)

    pool_matcher = parse_util.Matcher(
        pool_alias_map,

        allow_typo=True,
        typo_cutoff=0.85,
        typo_require_unique=True,

        allow_prefix=True,
        prefix_min_length=1,
        prefix_min_ratio=0.2,
        prefix_allow_typo=True,
        prefix_typo_cutoff=0.95,
    )

    pool_key, *_ = pool_matcher.split(parser.args, parser.raw_args)
    if pool_key is None:
        await ctx.reply(msg, f'Sorry, I don\'t recognize the card pool "{" ".join(parser.raw_args)}".')
        return

    pool_name, cards = pool_alias_map[pool_key]
    await ctx.reply(msg, f'**{pool_name} Pool:**\n{ctx.display.cards_long(cards)}')


##########################
# DECK BUILDING COMMANDS #
##########################

async def cmd_party(ctx, msg, parser):
    try:
        party = parser.party()
    except parse.ParseError:
        name = ' '.join(parser.raw_args)
        
        user_id = str(msg.author.id)
        parties = ctx.state.parties.setdefault(user_id, {})
    
        if name not in parties:
            raise
            #await ctx.reply(msg, f'There is no party named "{name}" in your party storage.')
    
        party = Party.from_json(ctx.game, parties[name])
    
    await ctx.reply(msg, ctx.display.party_long(party))


async def cmd_party_list(ctx, msg, parser):
    user_id = str(msg.author.id)
    parties = ctx.state.parties.setdefault(user_id, {})

    if not parties:
        await ctx.reply(msg, f'Your party storage is empty! Use `pt party add` to add a party.')
        return
    parties = {name: Party.from_json(ctx.game, party) for name, party in parties.items()}

    await ctx.reply(msg, '\n'.join(f'**{name}:** {ctx.display.party_short(parties[name])}' for name in sorted(parties)))


async def cmd_party_add(ctx, msg, parser):
    party = parser.party()
    if not parser.args:
        raise parse.ParseError('Please provide a party name.')
    name = ' '.join(parser.raw_args)
    
    user_id = str(msg.author.id)
    parties = ctx.state.parties.setdefault(user_id, {})

    if name in parties:
        await ctx.reply(msg, f'There is already a party named "{name}" in your party storage.')
        return
    parties[name] = party.to_json()
    ctx.state.save()

    await ctx.reply(msg, f'Successfully added "{name}" to your party storage.')


async def cmd_party_remove(ctx, msg, parser):
    if not parser.args:
        raise parse.ParseError('Please specify a party name.')
    name = ' '.join(parser.raw_args)
    
    user_id = str(msg.author.id)
    parties = ctx.state.parties.setdefault(user_id, {})

    if name not in parties:
        await ctx.reply(msg, f'There is no party named "{name}" in your party storage.')
        return
    party = Party.from_json(ctx.game, parties[name])
    del parties[name]
    ctx.state.save()

    await ctx.reply(msg, f'Successfully removed "{name}" from your party storage.\n\n{ctx.display.party_code(party)}')


async def cmd_simulate(ctx, msg, parser):
    card = parser.card()
    level, archetype, items = parser.character()
    cards = [c for i in items for c in i.cards]
    racial_move = archetype.default_move

    draw_deck = cards
    random.shuffle(draw_deck)
    discard_deck = []
    attachments = []
    hand = []
    for round_ in range(1, 4):
        # Draw cards at start of round
        # TODO: Unholy energy / etc.?
        draws = [racial_move]
        draw_count = 3 if round_ == 1 else 2
        for _ in range(draw_count):
            if not draw_deck:
                draw_deck = discard_deck
                random.shuffle(draw_deck)
                discard_deck = []

            draws.append(draw_deck[0])
            del draw_deck[0]
        hand.extend(draws)
        print(round_, hand)

        # Play cards during round
        # TODO: Attachments, duration; mandatory cards
        # TODO: Inspiration / etc.?
        # TODO: Trait: card.is_trait()
        # TODO: Mandatory: card.is_mandatory()
        
        # Discard cards at end of round
        # TODO: Discard low quality cards?
        # TODO: Forward Thinking: card.retain_count_modifier() == 1
        # TODO: Vow of Poverty: card.retain_card_name_filter() == 'Empty'
        # TODO: Free card: card.end_round_count() == 0
        hand_size = sum(not card.is_free_card for card in hand)
        discard_deck.extend(hand[:-2])
        del hand[:-2]
    
    
    await ctx.reply(msg, f'Card: {card}, deck: {cards}')


async def cmd_optimize(ctx, msg, parser):
    if not parser.args:
        # TODO: Give example
        raise parse.ParseError('Please specify a character archetype and card weights to optimize for.')

    archetype = parser.archetype()

    card_pack_matcher = parse_util.Matcher(
        ctx.party.card_packs,

        allow_typo=True,
        typo_cutoff=0.85,
        typo_require_unique=True,

        allow_prefix=True,
        prefix_min_length=1,
        prefix_min_ratio=0.2,
        prefix_allow_typo=True,
        prefix_typo_cutoff=0.95,
    )
    card_pack_combo = {}
    while parser.args:
        index, key = card_pack_matcher.longest_match(parser.args)
        if index is not None:
            card_pack = ctx.party.card_packs[key]
            del parser.args[:index]
            del parser.raw_args[:index]
        else:
            card = parser.card()
            card_pack = {card.name: 1}

        weight = 1
        if parser.raw_args:
            try:
                weight = float(parser.raw_args[0])
                del parser.args[0]
                del parser.raw_args[0]
            except ValueError:
                pass
        for card, value in card_pack.items():
            card_pack_combo.setdefault(card, 0)
            card_pack_combo[card] += value * weight

    if not card_pack_combo:
        raise parse.ParseError('Please specify card weights to optimize for.')

    optimal = await ctx.party.optimize(archetype, card_pack_combo)
    score, num_traits, items = optimal[0]

    stats = f'**Total value:** {score}\n**Number of traits:** {num_traits}\n**Average value:** {score / (36 - num_traits)}'
    items = ctx.display.items_long(items)

    # TODO: Could create Character from items and display a party code
    await ctx.reply(msg, f'{stats}\n\n{items}')


#######################
# DAILY DEAL COMMANDS #
#######################

async def cmd_daily_deal_list(ctx, msg, parser):
    user_id = str(msg.author.id)
    wishlist = ctx.state.wishlists.setdefault(user_id, {'items': [], 'cards': []})
    
    if not wishlist['items'] and not wishlist['cards']:
        await ctx.reply(msg, 'Your Daily Deal wishlist is empty! Use `pt wishlist add` to add an item or card.')
        return

    items = [ItemType.from_json(ctx.game, i) for i in wishlist['items']]
    cards = [CardType.from_json(ctx.game, c) for c in wishlist['cards']]

    items_str = ctx.display.items_long(items, sort=True) if items else ''
    cards_str = f'\n\n**Cards:** {ctx.display.cards_long(cards, sort=True)}' if cards else ''
    
    await ctx.reply(msg, f'{items_str}{cards_str}')


async def cmd_daily_deal_add(ctx, msg, parser):
    thing = parser.any()
    thing_json = thing.to_json()

    user_id = str(msg.author.id)
    wishlist = ctx.state.wishlists.setdefault(user_id, {'items': [], 'cards': []})

    if isinstance(thing, ItemType):
        if thing_json in wishlist['items']:
            await ctx.reply(msg, f'The item "{thing.name}" is already present in your Daily Deal wishlist.')
            return
        wishlist['items'].append(thing_json)
    elif isinstance(thing, CardType):
        if thing_json in wishlist['cards']:
            await ctx.reply(msg, f'The card "{thing.name}" is already present in your Daily Deal wishlist.')
            return
        wishlist['cards'].append(thing_json)
    ctx.state.save()
    
    await ctx.reply(msg, f'Successfully added "{thing.name}" to your Daily Deal wishlist.')


async def cmd_daily_deal_remove(ctx, msg, parser):
    thing = parser.any()
    thing_json = thing.to_json()

    user_id = str(msg.author.id)
    wishlist = ctx.state.wishlists.setdefault(user_id, {'items': [], 'cards': []})

    if isinstance(thing, ItemType):
        try:
            wishlist['items'].remove(thing_json)
        except ValueError:
            await ctx.reply(msg, f'The item "{thing.name}" is already absent from your Daily Deal wishlist.')
            return
    elif isinstance(thing, CardType):
        try:
            wishlist['cards'].remove(thing_json)
        except ValueError:
            await ctx.reply(msg, f'The card "{thing.name}" is already absent from your Daily Deal wishlist.')
    ctx.state.save()
    
    await ctx.reply(msg, f'Successfully removed "{thing.name}" from your Daily Deal wishlist.')


#################
# META COMMANDS #
#################

async def cmd_player_info(ctx, msg, parser):
    user_id = str(msg.author.id)

    player = ' '.join(parser.raw_args)
    if not player:
        accounts = ctx.state.accounts.setdefault(user_id, [])
        if not accounts:
            # TODO: Explain how to add CH account
            await ctx.reply(msg, f'Please specify a player, or add your own CH account first.')
            return
        player = accounts[0]

    player_idx = ctx.meta.player_name_to_idx.get(player)
    if player_idx is None:
        await ctx.reply(msg, f'"{player}" has no recorded games played.')
        return

    battles = list(ctx.meta.iter_player_battle_results(player_idx))
    ranked_battles = [x for x in battles if ctx.meta.is_ranked(x)]

    # TODO: Figure out why this doesn't match Farbs' site. Then remove AI battles.
    total_games = len(ranked_battles)
    wins = sum(ctx.meta.is_winner(x, player_idx) for x in ranked_battles)
    losses = total_games - wins
    winrate = wins / (total_games or 1)

    # TODO: Presentation
    # TODO: (Age since?) date of first pvp game played
    await ctx.reply(msg, f'**Total games:** {total_games}\n**W / L:** {wins} / {losses}\n**Winrate:** {winrate:.2%}')


async def cmd_player_head_to_head(ctx, msg, parser):
    user_id = str(msg.author.id)

    vs_idx = -1
    player = None
    try:
        vs_idx = parser.args.index('vs')
    except ValueError:
        accounts = ctx.state.accounts.setdefault(user_id, [])
        if not accounts:
            # TODO: Explain how to add CH account
            await ctx.reply(msg, f'Please specify two players separated by "vs", or add your own CH account and specify an opponent.')
            return
        player = accounts[0]
    else:
        player = ' '.join(parser.raw_args[:vs_idx])
        if not player:
            await ctx.reply(msg, f'Please specify a player before "vs".')
            return
        
    player_idx = ctx.meta.player_name_to_idx.get(player)
    if player_idx is None:
        await ctx.reply(msg, f'"{player}" has no recorded games played.')
        return

    opponent = ' '.join(parser.raw_args[vs_idx + 1:])
    if not opponent:
        await ctx.reply(msg, f'Please specify an opponent.')
        return

    opponent_idx = ctx.meta.player_name_to_idx.get(opponent)
    if opponent_idx is None:
        await ctx.reply(msg, f'"{opponent}" has no recorded games played.')
        return

    battles = list(ctx.meta.iter_h2h_battle_results(player_idx, opponent_idx))
    ranked_battles = [x for x in battles if ctx.meta.is_ranked(x)]

    # TODO: Figure out why this doesn't match Farbs' site. Then remove AI battles.
    total_games = len(ranked_battles)
    wins = sum(ctx.meta.is_winner(x, player_idx) for x in ranked_battles)
    losses = total_games - wins
    winrate = wins / (total_games or 1)

    # TODO: Presentation
    # TODO: (Age since?) date of first pvp game played
    await ctx.reply(msg, f'**Total games:** {total_games}\n**W / L:** {wins} / {losses}\n**Winrate:** {winrate:.2%}')


async def cmd_account_list(ctx, msg, parser):
    user_id = str(msg.author.id)
    accounts = ctx.state.accounts.setdefault(user_id, [])
    add_attempts = ctx.state.account_add_attempts.setdefault(user_id, [])
    add_attempts_start = ctx.state.account_add_attempts_start.setdefault(user_id, [])
    add_attempts_reset = ctx.state.account_add_attempts_reset.setdefault(user_id, [])

    # TODO: Formatting and timing info
    await ctx.reply(msg, f'Accounts: {accounts}\nAdd attempts: {add_attempts}')


async def cmd_account_add(ctx, msg, parser):
    user_id = str(msg.author.id)
    accounts = ctx.state.accounts.setdefault(user_id, [])
    add_attempts = ctx.state.account_add_attempts.setdefault(user_id, [])
    add_attempts_start = ctx.state.account_add_attempts_start.setdefault(user_id, [])
    add_attempts_reset = ctx.state.account_add_attempts_reset.setdefault(user_id, [])
    
    account_name = ' '.join(parser.raw_args)
    
    if account_name in add_attempts:
        # TODO: Show scenario instructions
        # TODO: Include timing info
        await ctx.reply(msg, f'Already attempting to add "{account_name}" to your account list.')
        return
    for user, accs in ctx.state.account_add_attempts.items():
        if account_name in accs:
            # TODO: Include timing info
            await ctx.reply(msg, f'Another user is already attempting to add "{account_name}" to their account list.')
            return

    if account_name in accounts:
        await ctx.reply(msg, f'"{account_name}" is already present in your account list.')
        return
    for user, accs in ctx.state.accounts.items():
        if account_name in accs:
            await ctx.reply(msg, f'"{account_name}" is already present in another user\'s account list.')
            return

    now = time.time()
    add_attempts.append(account_name)
    add_attempts_start.append(now)
    add_attempts_reset.append(now + 30 * 60)
    ctx.state.save()

    # TODO: Send info on where to find .scn, how to run it
    # TODO: Include timing info
    await ctx.reply(msg, f'Attempting to add "{account_name}" to your account list.')


async def cmd_account_remove(ctx, msg, parser):
    user_id = str(msg.author.id)
    accounts = ctx.state.accounts.setdefault(user_id, [])
    add_attempts = ctx.state.account_add_attempts.setdefault(user_id, [])
    add_attempts_start = ctx.state.account_add_attempts_start.setdefault(user_id, [])
    add_attempts_reset = ctx.state.account_add_attempts_reset.setdefault(user_id, [])

    account_name = ' '.join(parser.raw_args)
    
    if account_name in accounts:
        accounts.remove(account_name)
        ctx.state.save()
        
        await ctx.reply(msg, f'Removed "{account_name}" from your CH account list.')
        return
    
    if account_name in add_attempts:
        idx = add_attempts.index(account_name)
        del add_attempts[idx]
        del add_attempts_start[idx]
        del add_attempts_reset[idx]
        ctx.state.save()
        
        await ctx.reply(msg, f'No longer attempting to add "{account_name}" to your account list.')
        return
    
    await ctx.reply(msg, f'"{account_name}" is already absent from your account list.')


async def cmd_account_select(ctx, msg, parser):
    # TODO: Select linked account
    pass


async def cmd_guild_season(ctx, msg, parser):
    pass


async def cmd_guild_status(ctx, msg, parser):
    pass


async def cmd_guild_create(ctx, msg, parser):
    # TODO: User becomes leader
    # TODO: Make sure user isn't already in a guild
    # TODO: Make sure requested guild name isn't already in use?
    # TODO: [users], [leaders], [allies], creation date
    # TODO: What happens to guild points and stuff when users are added and removed during season? what happens to past seasons?
    pass


async def cmd_guild_dissolve(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to leaders? All guildmembers?
    pass


async def cmd_guild_toggle_auto_award(ctx, msg, parser):
    # TODO: Only activate toggle at start of next season, then DM all guildmembers
    pass


async def cmd_guild_enable_auto_award(ctx, msg, parser):
    # TODO: Only activate toggle at start of next season, then DM all guildmembers
    pass


async def cmd_guild_disable_auto_award(ctx, msg, parser):
    # TODO: Only activate toggle at start of next season, then DM all guildmembers
    pass


async def cmd_guild_invite(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other user
    # TODO: Send DM to leaders?
    pass


async def cmd_guild_kick(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other user
    # TODO: Send DM to leaders?
    pass


async def cmd_guild_join(ctx, msg, parser):
    # TODO: Only works if invited
    # TODO: Send DM to leaders?
    pass


async def cmd_guild_leave(ctx, msg, parser):
    # TODO: Send DM to leaders?
    pass


async def cmd_guild_add_leader(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other user?
    pass


async def cmd_guild_remove_leader(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other user?
    pass


async def cmd_guild_request_ally(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other guild's leaders
    # TODO: Check if there's already an outgoing request to that guild (=> don't send another request)
    # TODO: Check if there's already an incoming request from that guild (=> accept it)
    pass


async def cmd_guild_remove_ally(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Only works if already allied
    # TODO: Send DM to (both?) other guild's leaders (and members?)
    pass


async def cmd_guild_accept_ally(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to (both?) other guild's leaders (and members?)
    pass


async def cmd_guild_deny_ally(ctx, msg, parser):
    # TODO: Only works if user is leader
    # TODO: Send DM to other guild's leaders
    pass


###############
# EASTER EGGS #
###############

async def cmd_random(ctx, msg, parser):
    key = random.randint(0, 1)
    if key == 0:
        await cmd_random_card(ctx, msg, parser)
    else:
        await build_cmd_random_item()(ctx, msg, parser)


async def cmd_random_card(ctx, msg, parser):
    card = random.choice(ctx.game.cards)
    await ctx.reply(msg, ctx.display.card_long(card))


def build_cmd_random_item(include=lambda item: True):
    async def cmd_random_item(ctx, msg, parser):
        items = list(filter(include, ctx.game.items))
        item = random.choice(items)
        await ctx.reply(msg, ctx.display.item_long(item))
    
    return cmd_random_item


async def cmd_quiz(ctx, msg, parser):
    image_uses = collections.Counter(i.image_name for i in ctx.game.items)
    items = [i for i in ctx.game.items if not i.is_default_item and image_uses[i.image_name] == 1]
    item = random.choice(items)
    
    rarity = ctx.display.rarity_icon(item.rarity)
    if rarity:
        rarity += ' '

    slot = ctx.display.item_icon(item) or ctx.display.slot_icon(item.slot_type)
    if slot:
        slot += ' '
    
    card_icons = [ctx.display.card_icon(c) for c in item.cards]
    card_icons = ''.join(card_icons) + ' ' if all(card_icons) else ''

    item_name = item.name + ' ' * (40 - len(item.name))

    await ctx.reply(msg, f'{rarity}{slot}{card_icons}')
    await ctx.send(msg.channel, f'Answer: ||`{item_name}`||')


COMMAND_MAP = {
    # Admin commands
    'reload': cmd_reload,
    
    # Usage commands
    'help': cmd_help,

    # Game data commands
    'info': cmd_any_info,
    'item info': cmd_item_info,
    'item': cmd_item_info,
    'card info': cmd_card_info,
    'card': cmd_card_info,

    'list items': build_cmd_list_items(),
    'list weapons': build_cmd_list_items(lambda i: i.is_weapon),
    'list divine weapons': build_cmd_list_items(lambda i: i.is_divine_weapon),
    'list staves': build_cmd_list_items(lambda i: i.is_staff),
    'list helmets': build_cmd_list_items(lambda i: i.is_helmet),
    'list divine items': build_cmd_list_items(lambda i: i.is_divine_item),
    'list arcane items': build_cmd_list_items(lambda i: i.is_arcane_item),
    'list heavy armors': build_cmd_list_items(lambda i: i.is_heavy_armor),
    'list divine armors': build_cmd_list_items(lambda i: i.is_divine_armor),
    'list robes': build_cmd_list_items(lambda i: i.is_robes),
    'list shields': build_cmd_list_items(lambda i: i.is_shield),
    'list boots': build_cmd_list_items(lambda i: i.is_boots),
    'list martial skills': build_cmd_list_items(lambda i: i.is_martial_skill),
    'list divine skills': build_cmd_list_items(lambda i: i.is_divine_skill),
    'list arcane skills': build_cmd_list_items(lambda i: i.is_arcane_skill),
    'list elf skills': build_cmd_list_items(lambda i: i.is_elf_skill),
    'list human skills': build_cmd_list_items(lambda i: i.is_human_skill),
    'list dwarf skills': build_cmd_list_items(lambda i: i.is_dwarf_skill),
    'items': build_cmd_list_items(),
    'weapons': build_cmd_list_items(lambda i: i.is_weapon),
    'divine weapons': build_cmd_list_items(lambda i: i.is_divine_weapon),
    'staves': build_cmd_list_items(lambda i: i.is_staff),
    'helmets': build_cmd_list_items(lambda i: i.is_helmet),
    'divine items': build_cmd_list_items(lambda i: i.is_divine_item),
    'arcane items': build_cmd_list_items(lambda i: i.is_arcane_item),
    'heavy armors': build_cmd_list_items(lambda i: i.is_heavy_armor),
    'divine armors': build_cmd_list_items(lambda i: i.is_divine_armor),
    #'robes': build_cmd_list_items(lambda i: i.is_robes),
    'shields': build_cmd_list_items(lambda i: i.is_shield),
    #'boots': build_cmd_list_items(lambda i: i.is_boots),
    'martial skills': build_cmd_list_items(lambda i: i.is_martial_skill),
    'divine skills': build_cmd_list_items(lambda i: i.is_divine_skill),
    'arcane skills': build_cmd_list_items(lambda i: i.is_arcane_skill),
    'elf skills': build_cmd_list_items(lambda i: i.is_elf_skill),
    'human skills': build_cmd_list_items(lambda i: i.is_human_skill),
    'dwarf skills': build_cmd_list_items(lambda i: i.is_dwarf_skill),

    'card pool': cmd_pool,
    'pool': cmd_pool,
    'deck': cmd_pool,

    # Deck building commands
    'partydiscordcode': cmd_party,
    'partycode': cmd_party,
    'party show': cmd_party,
    'party display': cmd_party,
    'party view': cmd_party,
    'show party': cmd_party,
    'display party': cmd_party,
    'view party': cmd_party,
    'party': cmd_party,

    'party list': cmd_party_list,
    'parties': cmd_party_list,
    'list parties': cmd_party_list,

    'party add': cmd_party_add,
    'party save': cmd_party_add,
    'add party': cmd_party_add,
    'save party': cmd_party_add,

    'party remove': cmd_party_remove,
    'remove party': cmd_party_remove,

    'simulate': cmd_simulate,

    'optimize': cmd_optimize,
    'optimise': cmd_optimize,

    # Daily deal commands
    'daily deal wishlist': cmd_daily_deal_list,
    'daily deal list': cmd_daily_deal_list,
    'dd wishlist': cmd_daily_deal_list,
    'dd list': cmd_daily_deal_list,
    'wishlist': cmd_daily_deal_list,

    'daily deal add': cmd_daily_deal_add,
    'dd add': cmd_daily_deal_add,
    'wishlist add': cmd_daily_deal_add,

    'daily deal remove': cmd_daily_deal_remove,
    'dd remove': cmd_daily_deal_remove,
    'wishlist remove': cmd_daily_deal_remove,

    # Meta commands
    'player info': cmd_player_info,
    
    'player head to head': cmd_player_head_to_head,
    'player h2h': cmd_player_head_to_head,
    'head to head': cmd_player_head_to_head,
    'h2h': cmd_player_head_to_head,
    
    'account list': cmd_account_list,
    'account': cmd_account_list,
    
    'account add': cmd_account_add,

    'account remove': cmd_account_remove,

    # Easter eggs
    'sadge': build_cmd_reply('<:block:823700307862618173>'),

    'test': build_cmd_reply('Test passed!'),

    'walpanic': cmd_random,

    'walpanic card': cmd_random_card,
    
    'walpanic item': build_cmd_random_item(),
    'walpanic weapon': build_cmd_random_item(lambda i: i.is_weapon),
    'walpanic divine weapon': build_cmd_random_item(lambda i: i.is_divine_weapon),
    'walpanic staff': build_cmd_random_item(lambda i: i.is_staff),
    'walpanic helmet': build_cmd_random_item(lambda i: i.is_helmet),
    'walpanic divine item': build_cmd_random_item(lambda i: i.is_divine_item),
    'walpanic arcane item': build_cmd_random_item(lambda i: i.is_arcane_item),
    'walpanic heavy armor': build_cmd_random_item(lambda i: i.is_heavy_armor),
    'walpanic divine armor': build_cmd_random_item(lambda i: i.is_divine_armor),
    'walpanic robes': build_cmd_random_item(lambda i: i.is_robes),
    'walpanic shield': build_cmd_random_item(lambda i: i.is_shield),
    'walpanic boots': build_cmd_random_item(lambda i: i.is_boots),
    'walpanic martial skill': build_cmd_random_item(lambda i: i.is_martial_skill),
    'walpanic divine skill': build_cmd_random_item(lambda i: i.is_divine_skill),
    'walpanic arcane skill': build_cmd_random_item(lambda i: i.is_arcane_skill),
    'walpanic elf skill': build_cmd_random_item(lambda i: i.is_elf_skill),
    'walpanic human skill': build_cmd_random_item(lambda i: i.is_human_skill),
    'walpanic dwarf skill': build_cmd_random_item(lambda i: i.is_dwarf_skill),

    'quiz': cmd_quiz,
}

COMMAND_MATCHER = parse_util.Matcher(
    COMMAND_MAP,

    default=cmd_empty,

    allow_typo=True,
    typo_cutoff=0.95,
    typo_require_unique=True,
)
