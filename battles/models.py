from django.db import models


class Guild(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Player(models.Model):
    name = models.CharField(max_length=200, unique=True)
    guild = models.ForeignKey(Guild, null=True, blank=True)
    principal = models.BooleanField()


class Battle(models.Model):
    winner = models.ForeignKey(Player)
    loser = models.ForeignKey(Player)

    date = models.DateTimeField()
    blitz = models.BooleanField()
    contribution = models.PositiveIntegerField()
