# Object model for Card Hunter meta data (players, battles)

import datetime

from gamedata import CharacterArchetype, ItemType


# Character (a character with items equipped)
class Character:
    def __init__(self,
        name,
        level,
        archetype,
        items,
    ):
        self.name = name
        self.level = level
        self.archetype = archetype
        self.items = items

    def to_json(self):
        return {
            'name': self.name or '',
            'level': self.level,
            'archetype': self.archetype.to_json(),
            'items': [item.to_json() for item in self.items],
        }

    @classmethod
    def from_json(cls, game, data):
        return cls(
            data['name'] or None,
            data['level'],
            CharacterArchetype.from_json(game, data['archetype']),
            [ItemType.from_json(game, item) for item in data['items']],
        )

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.name}")'

    def __str__(self):
        return self.name


# Party (up to 3 characters)
class Party:
    def __init__(self,
        characters,
    ):
        self.characters = characters

    def to_json(self):
        return [char.to_json() for char in self.characters]

    @classmethod
    def from_json(cls, game, data):
        return cls([Character.from_json(game, char) for char in data])

    def __iter__(self):
        return iter(self.characters)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.characters})'

    def __str__(self):
        return ', '.join(str(char) for char in self.characters)
