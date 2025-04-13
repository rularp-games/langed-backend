from django.contrib import admin

from executor.models import Game, City, Staging, Convent, ConventStaging, Person, MasterGroup

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'announcement',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nickname')

@admin.register(MasterGroup)
class MasterGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Convent)
class ConventAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ConventStaging)
class ConventStagingAdmin(admin.ModelAdmin):
    list_display = ('city', 'convent', 'start_date', 'end_date',)

@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    def get_game_name(self, obj):
        return obj.game.name
    list_display = ('get_game_name', 'convent_staging', 'date',)

