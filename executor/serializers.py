from rest_framework import serializers
from .models import Staging, Person, ConventStaging, City, Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name', 'announcement', 'short_announcement', 'red_flags', 'creator_id']


class StagingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='game.name', read_only=True)
    announcement = serializers.CharField(source='game.announcement', read_only=True)
    red_flags = serializers.CharField(source='game.red_flags', read_only=True)
    convent_staging_date = serializers.DateField(source='convent_staging.start_date', read_only=True, format='%d-%m-%Y')
    convent_staging_id = serializers.CharField(source='convent_staging.id', read_only=True)
    city = serializers.DateField(source='convent_staging.city.name', read_only=True)
    date = serializers.DateField(format='%d-%m-%Y')
    masters = serializers.SerializerMethodField()
    organizers = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    pending_players = serializers.SerializerMethodField()
    technicians = serializers.SerializerMethodField()

    def get_masters(self, obj):
        masters = obj.masters.values('id', 'first_name', 'last_name')
        return list([{'name': f"{item['first_name']} {item['last_name']}", 'id': item['id']} for item in masters])

    def get_organizers(self, obj):
        organizers = obj.organizers.values('id', 'first_name', 'last_name')
        return list([{'name': f"{item['first_name']} {item['last_name']}", 'id': item['id']} for item in organizers])

    def get_players(self, obj):
        players = obj.players.values('id', 'first_name', 'last_name')
        return list([{'name': f"{item['first_name']} {item['last_name']}", 'id': item['id']} for item in players])

    def get_pending_players(self, obj):
        pending_players = obj.pending_players.values('id', 'first_name', 'last_name')
        return list([{'name': f"{item['first_name']} {item['last_name']}", 'id': item['id']} for item in pending_players])

    def get_technicians(self, obj):
        technicians = obj.technicians.values('id', 'first_name', 'last_name')
        return list([{'name': f"{item['first_name']} {item['last_name']}", 'id': item['id']} for item in technicians])

    class Meta:
        model = Staging
        fields = '__all__'


class ConventStagingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='convent.name', read_only=True)
    announcement = serializers.CharField(source='convent.announcement', read_only=True)
    city = serializers.DateField(source='city.name', read_only=True)
    convent_url = serializers.CharField(source='convent.url', read_only=True)
    game = serializers.SerializerMethodField()
    
    def get_game(self, obj):
        return obj.StagingConvent.values('id', 'game__name')

    class Meta:
        model = ConventStaging
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()
    technician = serializers.SerializerMethodField()
    master = serializers.SerializerMethodField()

    def get_player(self, obj):
        return obj.StagingPlayers.values('id', 'game__name')

    def get_organizer(self, obj):
        return obj.StagingOrganizers.values('id', 'game__name')

    def get_technician(self, obj):
        return obj.StagingTechnicians.values('id', 'game__name')

    def get_master(self, obj):
        return obj.StagingMasters.values('id', 'game__name')

    class Meta:
        model = Person
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'
