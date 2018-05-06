import os.path

from website.settings import BASE_DIR


LOCALDATA_DIR = os.path.join(BASE_DIR, 'localdata')
GAMEDATA_DIR = os.path.join(LOCALDATA_DIR, 'gamedata')
GUILD_PIZZA_DIR = os.path.join(LOCALDATA_DIR, 'guild_pizza')
META_DIR = os.path.join(LOCALDATA_DIR, 'meta')
BATTLES_DIR = os.path.join(META_DIR, 'battles')
