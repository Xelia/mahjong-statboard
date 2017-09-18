# -*- coding: utf-8 -*-
from collections import defaultdict
from django.db import models
from django.contrib.auth import get_user_model

from mahjong_statboard import rating
from mahjong_statboard.rating.backends import LocalBackend


class Instance(models.Model):
    STORAGE_LOCAL = 'local'
    STORAGE_PANTHEON = 'pantheon'
    STORAGE_CHOICES = (
        (STORAGE_LOCAL, STORAGE_LOCAL),
        (STORAGE_PANTHEON, STORAGE_PANTHEON),
    )
    name = models.TextField()
    description = models.TextField(blank=True)
    title = models.TextField(blank=True)
    game_storage = models.CharField(max_length=16, choices=STORAGE_CHOICES, default=STORAGE_LOCAL)
    pantheon_id = models.IntegerField(blank=True, null=True)
    admins = models.ManyToManyField(get_user_model(), blank=True)

    def get_backend(self):
        return LocalBackend(self)

    def __str__(self):
        return self.name


class InstanceDomain(models.Model):
    instance = models.ForeignKey(Instance, related_name='domains')
    name = models.CharField(max_length=256, unique=True)


class Rating(models.Model):
    STATE_INQUEUE = 'inqueue'
    STATE_COUNTING = 'counting'
    STATE_ACTUAL = 'actual'
    STATE_CHOICES = (
        (STATE_INQUEUE, 'In queue for counting'),
        (STATE_COUNTING, 'Counting'),
        (STATE_ACTUAL, 'Actual')
    )
    instance = models.ForeignKey(Instance)
    rating_name = models.CharField(max_length=256, blank=True, default='')
    rating_type_id = models.CharField(max_length=32, choices=((r.id, r.name) for r in rating.ALL_RATINGS.values()))
    series_len = models.PositiveIntegerField(blank=True, null=True, help_text='Работает только если рейтинг является серией')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    weight = models.IntegerField(help_text='Порядок сортировки', default=999)
    state = models.CharField(choices=STATE_CHOICES, max_length=16, default=STATE_INQUEUE)

    class Meta:
        ordering = ('weight', )

    def get_rating_type(self):
        return rating.ALL_RATINGS[self.rating_type_id]

    @property
    def stats(self):
        return {stat.player_id: stat for stat in self.stats_set.all()}

    @property
    def name(self):
        if self.rating_name:
            return self.rating_name
        res = self.get_rating_type().name
        if self.start_date:
            res += ' start: {}'.format(self.start_date)
        if self.end_date:
            res += ' end: {}'.format(self.end_date)
        if self.series_len:
            res += ' length: {}'.format(self.series_len)
        return res

    def __str__(self):
        return '{}: {}'.format(self.instance.name, self.name)


class Stats(models.Model):
    instance = models.ForeignKey(Instance)
    rating = models.ForeignKey(Rating)
    player = models.ForeignKey('Player')
    value = models.TextField()
    place = models.IntegerField(null=True, blank=True)
    game = models.ForeignKey('Game', null=True)

    def __str__(self):
        return '{}, {}, {}, {}: {}'.format(self.instance.name, self.rating, self.player, self.game, self.value)


class Player(models.Model):
    instance = models.ForeignKey(Instance)
    name = models.CharField(max_length=256)
    full_name = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)

    @property
    def opponents(self):
        result = defaultdict(lambda: {'wins': 0, 'losses': 0, 'player': None})
        for game in Game.objects.filter(gameresult__player_id=self.id).prefetch_related('gameresult_set', 'gameresult_set__player'):
            game_results = game.gameresult_set.all()
            for gr in game_results:
                if gr.player_id == self.id:
                    player_place = gr.place
                    break
            for gr in game_results:
                if gr.player_id != self.id:
                    result[gr.player.id]['wins' if gr.place > player_place else 'losses'] += 1
                    result[gr.player.id]['player'] = gr.player

        return sorted(result.values(), key=lambda a: a['wins'] + a['losses'], reverse=True)

    class Meta:
        unique_together = ('instance', 'name')

    def __str__(self):
        return 'Player: {}'.format(self.name)


class Game(models.Model):
    instance = models.ForeignKey(Instance)
    date = models.DateField()
    addition_time = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(get_user_model(), null=True)

    class Meta:
        ordering = ('-date', '-addition_time',)

    def __str__(self):
        return 'Game date: {}'.format(self.date)


class GameResult(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    score = models.IntegerField()
    place = models.SmallIntegerField()
    starting_position = models.SmallIntegerField()

    class Meta:
        ordering = ('starting_position', )
