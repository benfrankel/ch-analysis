import copy
from dataclasses import dataclass, field
import datetime
import os.path

import cache
from . import const


GUILD_EVENTS_FILEPATH = os.path.join(const.BASE_DIRPATH, 'guild_events')
GUILD_CHECKPOINTS_FILEPATH = os.path.join(const.BASE_DIRPATH, 'guild_checkpoints')

# TODO: List battles that have already been processed?
# TODO: Disable / enable guild system toggle, initially disabled.
# TODO: Guild event = [message, delta state?]
# TODO: Store guild state "checkpoints" + "deltas".
# TODO: Whenever a new battle comes in, find the closest checkpoint, then
#       follow the deltas to reconstruct state at the time the battle
#       started.
# TODO: Shortly after a month ends, "freeze" the season and stop processing
#       new battles for that season. Then announce & distribute rewards.
# TODO: Include a summary for each season.
# TODO: If scoring system changes (hard change in code, not soft change),
#       it'll only affect processing of incoming battles after pizzatron
#       restarts. Old battles are stored as guild log events that include
#       points gained / lost as calculated in the older version.
# TODO: Save guild log BEFORE saving battle history


def load():
    manager = Manager()
    manager.load()
    return manager


###############
# GUILD STATE #
###############

@dataclass
class Ally:
    name: str


@dataclass
class Member:
    name: str
    is_tracking: bool = True
    is_leader: bool = False
    rating: float = 1000.0
    contribution: float = 0.0


@dataclass
class MemberShadow:
    name: str
    rating: float = 1000.0
    contribution: float = 0.0


@dataclass
class Guild:
    name: str
    auto_award: bool = True
    auto_award_next_season: bool = True
    allies: list[Ally] = field(default_factory=list, init=False)
    members: list[Member] = field(default_factory=list, init=False)
    shadows: list[Optional[MemberShadow]] = field(default_factory=list, init=False)

    def get_ally_idx(self, name):
        for i, ally in enumerate(self.allies):
            if ally.name == name:
                return i

        raise ValueError(f'Guild "{self.name}" has no ally named "{name}"')

    def get_member_idx(self, name):
        for i, member in enumerate(self.members):
            if member.name == name:
                return i

        raise ValueError(f'Guild "{self.name}" has no member named "{name}"')

    def get_member(self, name):
        for member in self.members:
            if member.name == name:
                return member

        raise ValueError(f'Guild "{self.name}" has no member named "{name}"')

    def get_shadow(self, name):
        for shadow in self.shadows:
            if shadow.name == name:
                return shadow

        raise ValueError(f'Guild "{self.name}" has no member named "{name}"')


@dataclass
class GuildState:
    is_active: bool
    minimum_rating: float
    blitz_multiplier: float
    guilds: list[Guild] = field(default_factory=list, init=False)

    def get_guild_idx(self, name):
        for i, guild in enumerate(self.guilds):
            if guild.name == name:
                return i

        raise ValueError(f'No guild named "{name}"')

    def get_guild(self, name):
        for guild in self.guilds:
            if guild.name == name:
                return guild

        raise ValueError(f'No guild named "{name}"')


@dataclass
class GuildCheckpoint:
    state: GuildState
    timestamp: float
    next_event_idx: int


###############
# GUILD EVENT #
###############

@dataclass
class EventSystemSetActive:
    user: str
    is_active: bool

    def __str__(self):
        return f'{self.user} {["disabled", "enabled"][self.is_active]} the guild system'


@dataclass
class EventSystemSetScoring:
    user: str
    minimum_rating: int
    blitz_multiplier: float

    def __str__(self):
        return f'{self.user} updated the guild system parameters: Minimum rating = {self.minimum_rating}, Blitz multiplier = {self.blitz_multiplier}'


@dataclass
class EventGuildCreate:
    user: str
    guild: str

    def __str__(self):
        return f'{self.user} formed {self.guild}'


@dataclass
class EventGuildDissolve:
    user: str
    guild: str

    def __str__(self):
        return f'{self.user} dissolved {self.guild}'


@dataclass
class EventGuildAddAlly:
    user: str
    guild: str
    target_user: str
    target_guild: str

    def __str__(self):
        return f'{self.user} and {self.target_user} formed an alliance between {self.guild} and {self.target_guild}'


@dataclass
class EventGuildRemoveAlly:
    user: str
    guild: str
    target_guild: str

    def __str__(self):
        return f'{self.user} ended the alliance between {self.guild} and {self.target_guild}'


@dataclass
class EventGuildSetAutoAward:
    user: str
    guild: str
    auto_award_next_season: bool

    def __str__(self):
        return f'{self.user} turned {["off", "on"][self.auto_award_next_season]} automatic award distribution for {self.guild} for the upcoming season'


@dataclass
class EventGuildMemberJoin:
    user: str
    guild: str

    def __str__(self):
        return f'{self.user} joined {self.guild}'


@dataclass
class EventGuildMemberLeave:
    user: str
    guild: str

    def __str__(self):
        return f'{self.user} left {self.guild}'


@dataclass
class EventGuildMemberKick:
    user: str
    guild: str
    target_user: str

    def __str__(self):
        return f'{self.user} kicked {self.target_user} from {self.guild}'


@dataclass
class EventGuildMemberSetTracking:
    user: str
    guild: str
    is_tracking: bool

    def __str__(self):
        return f'{self.user} turned {["off", "on"][self.is_tracking]} tracking for {self.guild}'


@dataclass
class EventGuildMemberSetLeader:
    user: str
    guild: str
    target_user: str
    is_leader: bool

    def __str__(self):
        if self.is_leader:
            return f'{self.user} promoted {self.target_user} from member to leader of {self.guild}'
        else:
            return f'{self.user} demoted {self.target_user} from leader to member of {self.guild}'
    

###########
# MANAGER #
###########

class Manager:
    def __init__(self):
        # Local cache
        self.guild_events_cache = cache.Cache(
            GUILD_EVENTS_FILEPATH,
            format=cache.Format.PICKLE,
        )
        self.guild_checkpoints_cache = cache.Cache(
            GUILD_CHECKPOINTS_FILEPATH,
            format=cache.Format.PICKLE,
        )

        # In-memory storage
        self.guild_events = []
        self.guild_checkpoints = []

        # Flags
        self.is_loaded = False

        def _reload_guild_events(self):
            self.guild_events_cache.reload()
            self.guild_events = self.guild_events_cache.data

        def _reload_guild_checkpoints(self):
            self.guild_checkpoints_cache.reload()
            self.guild_checkpoints = self.guild_checkpoints_cache.data

        def load(self):
            if self.is_loaded:
                return

            self._reload_guild_events()
            self._reload_guild_checkpoints()

            self.is_loaded = True

        def reload(self):
            self.is_loaded = False
            self.load()

        def save(self):
            if not self.is_loaded:
                return

            self.guild_events_cache.save()
            self.guild_checkpoints_cache.save()

        def _get_state(self, timestamp):
            checkpoint = None
            for c in self.guild_checkpoints[::-1]:
                if c.timestamp <= timestamp:
                    checkpoint = c
                    break
            else:
                raise ValueError('Timestamp predates the guild system')

            state = copy.deepcopy(checkpoint.state)
            for event in self.guild_events[checkpoint.next_event_idx:]:
                if timestamp < event.timestamp:
                    break

                # TODO: Battle result event
                if isinstance(event, EventSystemSetActive):
                    state.is_active = event.is_active
                elif isinstance(event, EventSystemSetScoring):
                    state.minimum_rating = event.minimum_rating
                    state.blitz_multiplier = event.blitz_multiplier
                elif isinstance(event, EventGuildCreate):
                    guild = Guild(event.guild)
                    guild.members.append(Member(event.user, is_leader=True))
                    guild.shadows.append(None)
                    state.guilds.append(guild)
                elif isinstance(event, EventGuildDissolve):
                    guild_idx = state.get_guild_idx(event.guild)
                    del state.guilds[guild_idx]
                elif isinstance(event, EventGuildAddAlly):
                    guild = state.get_guild(event.guild)
                    guild.allies.append(Ally(event.target_guild))
                elif isinstance(event, EventGuildRemoveAlly):
                    guild = state.get_guild(event.guild)
                    ally_idx = guild.get_ally_idx(event.target_guild)
                    del guild.allies[ally_idx]
                elif isinstance(event, EventGuildSetAutoAward):
                    guild = state.get_guild(event.guild)
                    guild.auto_award_next_season = event.auto_award_next_season
                elif isinstance(event, EventGuildMemberJoin):
                    guild = state.get_guild(event.guild)
                    guild.members.append(Member(event.user))
                    # TODO: Tie to shadow or create new empty shadow?
                    guild.shadows.append(None)
                elif isinstance(event, EventGuildMemberLeave):
                    guild = state.get_guild(event.guild)
                    member_idx = guild.get_member_idx(event.user)
                    del guild.members[member_idx]
                    # TODO: Create shadow
                elif isinstance(event, EventGuildMemberKick):
                    guild = state.get_guild(event.guild)
                    member_idx = guild.get_member_idx(event.target_user)
                    del guild.members[member_idx]
                    # TODO: Create shadow
                elif isinstance(event, EventGuildMemberSetTracking):
                    guild = state.get_guild(event.guild)
                    member = guild.get_member(event.user)
                    member.is_tracking = event.is_tracking
                elif isinstance(event, EventGuildMemberSetLeader):
                    guild = state.get_guild(event.guild)
                    member = guild.get_member(event.user)
                    member.is_tracking = event.is_tracking

            return state

        def process_battle(self, battle):
            if battle.start_time <= self.guild_checkpoints[-1].timestamp:
                return

            state = self._get_state(battle.start_time)

            # TODO: Check if one of the players is in a guild, else return
            # TODO: Calculate rating changes based on guild state
            # TODO: Create and append guild event

        # TODO: Functions for other guild events via pizzatron commands

        # TODO: Start new season:
        #       - When a battle comes in from the next season?
        #       - Create checkpoint to freeze the old season (stop updating from older battle results -- just do this automatically with checkpoint system above)
        #       - Create summary
        #       - Announce and distribute pizza / prizes
