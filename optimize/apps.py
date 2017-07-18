import optimize
import gamedata

from django.apps import AppConfig


class OptimizeConfig(AppConfig):
    name = ''

    def ready(self):
        gamedata.load()
        optimize.load()
