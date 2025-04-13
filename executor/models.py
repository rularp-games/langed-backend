from django.contrib.auth.models import User
from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=1024)
    announcement = models.TextField(blank=True,
                                    null=True)
    short_announcement = models.TextField(blank=True,
                                          null=True)
    red_flags = models.TextField(blank=True,
                                 null=True)
    
    author = models.ForeignKey('Person',
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    master_group = models.ForeignKey('MasterGroup',
                                     on_delete=models.SET_NULL,
                                     blank=True,
                                     null=True)
    creator = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)


    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Игра'

class Person(models.Model):
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    nickname = models.CharField(max_length=1024)
    vk_url = models.URLField(blank=True,
                             null=True)
    tg_url = models.URLField(blank=True,
                             null=True)
    user = models.ForeignKey('auth.User',
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)

    def __str__(self):
        return f'{self.first_name} "{self.nickname}" {self.last_name}'

    class Meta:
        verbose_name_plural = 'Человек'

class MasterGroup(models.Model):
    name = models.CharField(max_length=1024)
    vk_url = models.URLField(blank=True,
                             null=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Мастерская группа'

class City(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Город'
        ordering = ['name']

class Convent(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True,
                                   null=True)
    url = models.URLField(blank=True,
                          null=True)
    
    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Конвент серия'

class ConventStaging(models.Model):
    city = models.ForeignKey('City',
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)
    convent = models.ForeignKey('Convent',
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=1024,
                            blank=True,
                            null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    members = models.ManyToManyField('Person',
                                     blank=True)
    organizers = models.ManyToManyField('Person',
                                        blank=True,
                                        related_name='ConventStagingOrganizers')

    def __str__(self):
        return f'{self.convent.name}'

    class Meta:
        verbose_name_plural = 'Конвент'

class Staging(models.Model):
    city = models.ForeignKey('City',
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)
    game = models.ForeignKey('Game',
                             on_delete=models.CASCADE)
    convent_staging = models.ForeignKey('ConventStaging', 
                                        on_delete=models.SET_NULL,
                                        blank=True,
                                        null=True,
                                        related_name='StagingConvent')
    date = models.DateField(default='2025-01-01',
                            blank=True,)
    announcement_url = models.URLField(blank=True,
                                       null=True)
    masters = models.ManyToManyField('Person',
                                     blank=True,
                                     related_name='StagingMasters')
    players = models.ManyToManyField('Person',
                                     blank=True,
                                     related_name='StagingPlayers')
    pending_players = models.ManyToManyField('Person',
                                             blank=True,
                                             related_name='StagingPendingPlayers')
    technicians = models.ManyToManyField('Person',
                                         blank=True,
                                         related_name='StagingTechnicians')
    organizers = models.ManyToManyField('Person',
                                        blank=True,
                                        related_name='StagingOrganizers')

    def __str__(self):
        if self.city:
            city_or_convent = f'{self.city.name} [{self.date}]'
        else:
            city_or_convent = f'{self.convent_staging.convent.name}'
        return f'{self.game.name} - {city_or_convent}'

    def save(self, *args, **kwargs):
        if not self.date and self.convent_staging and self.convent_staging.start_date:
            self.date = self.convent_staging.start_date
        
        super(Staging, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Прогон'
