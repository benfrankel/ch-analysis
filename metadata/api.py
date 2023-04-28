"""
Interface with Card Hunter API.
"""

import datetime
import time
import urllib.parse

from . import model


# CH API endpoints
CH_API_DOMAIN = 'http://api.cardhunter.com'

PLAYERS_PATH = '/players'
BATTLES_PATH = '/battles'
# TODO: Not functional right now.
CHARACTERS_PATH = '/characters'
# TODO: Not functional right now.
ITEMS_PATH = '/items'

MAX_COUNT = 100

_limit = 1
_limit_remaining = 1
_limit_reset = None


class RequestLimitReached(Exception):
    pass


async def _call(session, path, **query):
    global _limit
    global _limit_remaining
    global _limit_reset

    now = time.time() * 1000
    if _limit_reset is not None and now > _limit_reset:
        _limit_remaining = _limit
        _limit_reset = None
    if _limit_remaining == 0:
        raise RequestLimitReached()

    url = urllib.parse.urljoin(CH_API_DOMAIN, path)
    if query:
        for key in [key for key, value in query.items() if value is None]:
            del query[key]

    async with session.get(url, params=query) as response:
        _limit = int(response.headers.get('X-RateLimit-Limit', _limit))
        _limit_remaining = int(response.headers.get('X-RateLimit-Remaining', _limit_remaining - 1))
        _limit_reset = response.headers.get('X-RateLimit-Reset', _limit_reset)
        _limit_reset = None if _limit_reset is None else int(_limit_reset)
        if response.status == 429:
            raise RequestLimitReached()
        return await response.json()


class Pager:
    def __init__(self, session, first, last, prev, next_, entries, key, parser):
        self._session = session
        
        # Links to other pages
        self._first = first
        self._last = last
        self._prev = prev
        self._next = next_
        
        # Current page
        self.page = 0
        self.entries = entries

        # Parsing helpers
        self._key = key
        self._parser = parser

    async def _to_page(self, path):
        if path is None:
            return False
        
        page = _parse_page(self._session, await _call(self._session, path), self._key, self._parser)
        self.entries = page.entries
        self._prev = page._prev
        self._next = page._next

        return True

    async def to_first(self):
        if await self._to_page(self._first):
            self.page = 0
        return self

    async def to_last(self):
        if await self._to_page(self._last):
            self.page = -1
        return self

    async def to_prev(self):
        if await self._to_page(self._prev):
            self.page -= 1
        return self

    async def to_next(self):
        if await self._to_page(self._next):
            self.page += 1
        return self

    def __repr__(self):
        return f'{self.__class__.__name__}({self.page}, "{self._key}")'


def _parse_page(session, response, key, parser):
    def escape(path):
        if path is None:
            return None
        
        parse = urllib.parse.urlparse(path)
        if not parse.query:
            return path
        
        path = parse.path
        query = urllib.parse.urlencode(urllib.parse.parse_qsl(parse.query))
        return f'{path}?{query}'

    meta = response['meta']
    entries = [parser(entry) for entry in response[key]]
    
    return Pager(
        session,
        escape(meta['first']),
        escape(meta['last']),
        escape(meta['prev']),
        escape(meta['next']),
        entries,
        key,
        parser,
    )


def _parse_player(entry):
    return model.Player(
        name=entry['name'],
        rating=entry['rating'],
        steam_id=entry['steam_id'],
        kongregate_id=entry['kongregate_id'],
        ranked_mp_games=entry.get('ranked_mp_games'),
        ranked_mp_wins=entry.get('ranked_mp_wins'),
        ranked_ai_games=entry.get('ranked_ai_games'),
        ranked_ai_wins=entry.get('ranked_ai_wins'),
    )


async def search_players(
    session,
    count=10,
    initial=None,
    search=None,
    min_rating=None,
    max_rating=None,
):
    if min_rating is not None:
        min_rating -= 1
    if max_rating is not None:
        max_rating += 1
    
    return _parse_page(
        session,
        response=await _call(
            session,
            PLAYERS_PATH,
            count=count,
            initial=initial,
            substring=search,
            above_rating=min_rating,
            below_rating=max_rating,
        ),
        key='players',
        parser=_parse_player,
    )


async def get_player(session, name):
    response = await _call(session, f'{PLAYERS_PATH}/{urllib.parse.quote(name)}')
    return _parse_player(response['player'])


def _parse_battle(entry):
    start_time = entry['start'].replace('Z', '+00:00')
    start_time = datetime.datetime.fromisoformat(start_time)
    
    return model.BattleResult(
        id=entry['id'],
        start_time=start_time,
        duration_seconds=entry['duration'],
        num_rounds=entry['rounds'],
        scenario_name=entry['scenario'],
        scenario_hash=entry.get('scenarioHash'),
        quest=entry['quest'],
        game_type=entry['gameType'],
        player_names=(entry['player1'], entry['player2']),
        player_scores=(entry['player1Score'], entry['player2Score']),
        player_avg_hps=(entry['player1AvgHealth'], entry['player2AvgHealth']),
        winner=entry['winner'],
    )


async def search_battles(
    session,
    count=10,
    # RANKED, CASUAL, or LEAGUE
    game_type=None,
    min_id=None,
    max_id=None,
    min_start=None,
    max_start=None,
    scenario=None,
):
    if min_id is not None:
        min_id -= 1
    if max_id is not None:
        max_id += 1
    if min_start is not None:
        min_start -= datetime.timedelta(microseconds=1)
        min_start = str(min_start).replace('+00:00', 'Z')
    if max_start is not None:
        max_start += datetime.timedelta(microseconds=1)
        max_start = str(max_start).replace('+00:00', 'Z')

    return _parse_page(
        session,
        response=await _call(
            session,
            BATTLES_PATH,
            count=count,
            after=min_id,
            before=max_id,
            after_time=min_start,
            before_time=max_start,
            scenario=scenario,
        ),
        key='battles',
        parser=_parse_battle,
    )


async def get_battle(name):
    response = await _call(session, f'{BATTLES_PATH}/{urllib.parse.quote(name)}')
    return _parse_battle(response['battle'])
