from django.db import models


class Guild(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=200, unique=True)
    guild = models.ForeignKey(Guild, null=True, blank=True)
    principal = models.BooleanField()

    def __str__(self):
        if self.guild is None:
            return self.name
        return f'{self.name}, {self.guild}'


class Battle(models.Model):
    winner = models.ForeignKey(Player, related_name='winner')
    loser = models.ForeignKey(Player, related_name='loser')

    date = models.DateTimeField()
    blitz = models.BooleanField()
    contribution = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.winner} {["defeated", "blitzed"][self.blitz]} {self.loser}'
