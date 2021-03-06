# -*- coding: utf-8 -*-
import logging
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
    instance = models.ForeignKey(Instance, related_name='domains', on_delete=models.CASCADE)
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
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT)
    rating_name = models.CharField(max_length=256, blank=True, default='')
    rating_type_id = models.CharField(max_length=32, choices=((r.id, r.name) for r in rating.ALL_RATINGS.values()))
    series_len = models.PositiveIntegerField(blank=True, null=True, help_text='Работает только если рейтинг является серией')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    days_number = models.PositiveIntegerField(blank=True, null=True, help_text='Брать игры за последние N дней')
    weight = models.IntegerField(help_text='Порядок сортировки', default=999)
    state = models.CharField(choices=STATE_CHOICES, max_length=16, default=STATE_INQUEUE)
    archived = models.BooleanField(default=False)
    last_recount = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('archived', 'weight', )

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
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    value = models.TextField()
    place = models.IntegerField(null=True, blank=True)
    game = models.ForeignKey('Game', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}, {}, {}: {}'.format(self.instance.name, self.rating, self.player, self.game, self.value)


class Player(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT)
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

    def merge(self, duplicate_player):
        logger = logging.getLogger('player_merge')
        logger.info(
            'Player merge. Main player: {}, Duplicate player: {}'.format(self.name, duplicate_player.name))
        counter = 0
        for game_result in GameResult.objects.filter(player=duplicate_player).all():
            logger.info('Game id: {} changing player {} to {}'.format(game_result.game_id, duplicate_player.name, self.name))
            game_result.player = self
            game_result.save()
            counter += 1
        return counter


class Game(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.PROTECT)
    date = models.DateField()
    addition_time = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.PROTECT)

    def recount_places(self):
        for place, game_result in enumerate(self.gameresult_set.order_by('-score', 'starting_position').all()):
            game_result.place = place + 1
            game_result.save()

    class Meta:
        ordering = ('-date', '-addition_time',)

    def __str__(self):
        return 'Game date: {}'.format(self.date)


class GameResult(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    score = models.IntegerField()
    place = models.SmallIntegerField()
    starting_position = models.SmallIntegerField()

    class Meta:
        ordering = ('starting_position', )
