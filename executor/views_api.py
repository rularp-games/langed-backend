from datetime import date
from rest_framework import generics
from .models import Staging, ConventStaging, Person, City, Convent, Game, MasterGroup
from .serializers import StagingSerializer, PersonSerializer, ConventStagingSerializer, GameSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.middleware.csrf import get_token
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CSRFTokenView(APIView):
    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrf_token': csrf_token})


class StagingList(generics.ListCreateAPIView):
    queryset = Staging.objects.all()
    serializer_class = StagingSerializer


class CityView(APIView):
    def get(self, request):
        cities = City.objects.values('id', 'name')
        response_data = {'cities': [{'id': item['id'], 'name': item['name']} for item in cities]}
        return Response(response_data)


class ConventDetailView(APIView):
    def get(self, request, id):
        try:
            stage = ConventStaging.objects.get(id=id)
            serializer = ConventStagingSerializer(stage)
            return Response(serializer.data)
        except ConventStaging.DoesNotExist:
            return Response({"error": "Staging not found"}, status=status.HTTP_404_NOT_FOUND)


class GameRegistrationView(APIView):
    def get(self, request, id):
        if request.user.is_anonymous:
            return Response({"registration": "none"})
        try:
            game = Staging.objects.get(id=id)
            person = Person.objects.get(user_id=request.user.id)
            if game.masters.filter(id=person.id).exists():
                return Response({"registration": "none"})
            if game.technicians.filter(id=person.id).exists():
                return Response({"registration": "none"})
            if game.organizers.filter(id=person.id).exists():
                return Response({"registration": "none"})
            if game.pending_players.filter(id=person.id).exists():
                return Response({"registration": "unregister"})
            if game.players.filter(id=person.id).exists():
                return Response({"registration": "unregister"})
            return Response({"registration": "register"})
        except ObjectDoesNotExist:
            return Response({"registration": "none"})


    def post(self, request, id, format=None):
        if request.user.is_anonymous:
            return Response({"registration": "none"})
        try:
            game = Staging.objects.get(id=id)
            person = Person.objects.get(user_id=request.user.id)
            if request.data['registration'] == 'register':
                if game.masters.filter(id=person.id).exists():
                    return Response({"registration": "none"})
                if game.technicians.filter(id=person.id).exists():
                    return Response({"registration": "none"})
                if game.organizers.filter(id=person.id).exists():
                    return Response({"registration": "none"})
                if game.players.filter(id=person.id).exists():
                    return Response({"registration": "none"})
                game.pending_players.add(person)

            if request.data['registration'] == 'unregister':
                if game.pending_players.filter(id=person.id).exists():
                    game.pending_players.remove(person)
                    return Response({"registration": "unregister"})
                if game.players.filter(id=person.id).exists():
                    game.players.remove(person)
                    return Response({"registration": "unregister"})

            return Response({"registration": "none"})
        except ObjectDoesNotExist:
            return Response({"registration": "none"})


class StageDetailView(APIView):
    def get(self, request, id):
        try:
            stage = Staging.objects.get(id=id)
            serializer = StagingSerializer(stage)
            return Response(serializer.data)
        except Staging.DoesNotExist:
            return Response({"error": "Staging not found"}, status=status.HTTP_404_NOT_FOUND)


class PersonDetailView(APIView):
    def get(self, request, id):
        try:
            person = Person.objects.get(id=id)
            serializer = PersonSerializer(person)
            return Response(serializer.data)
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)


class LoggedUserView(APIView):
    def get(self, request):
        user = request.user
        if request.user.is_anonymous:
            response_json = {'username': 'Anonymous',
                             'first_name': '',
                             'last_name': ''}
        else:
            response_json = {'username': user.username,
                             'first_name': user.first_name,
                             'last_name': user.last_name}
        return Response(response_json)


class CombinedView(APIView):
    def get(self, request):
        schedule = []

        void_convent_staging = ConventStaging.objects.exclude(StagingConvent__isnull=False).values('id', 
                                                                                                   'convent__name', 
                                                                                                   'city__name', 
                                                                                                   'convent__url',
                                                                                                   'start_date', 
                                                                                                   'end_date').order_by('start_date')

        for item in Staging.objects.values('id',
                                           'date', 
                                           'game__name', 
                                           'city__name',
                                           'announcement_url',
                                           'convent_staging__city__name',
                                           'convent_staging__convent__url',
                                           'convent_staging__id',
                                           'convent_staging__start_date', 
                                           'convent_staging__end_date',
                                           'convent_staging__convent__name').order_by('date'):
            while void_convent_staging and void_convent_staging[0]['start_date'] < item['date']:
                schedule.append({
                    'convent_id': void_convent_staging[0]['id'],
                    'convent_name': void_convent_staging[0]['convent__name'],
                    'city': void_convent_staging[0]['city__name'],
                    'announcement_url': void_convent_staging[0]['convent__url'],
                    'start_date': void_convent_staging[0]['start_date'],
                    'end_date': void_convent_staging[0]['end_date'],
                    'finished': str(void_convent_staging[0]['end_date'] < date.today()),
                })
                void_convent_staging = void_convent_staging[1:]
            
            current_convent_staging = {
                'convent_id': item['convent_staging__id'],
                'convent_name': item['convent_staging__convent__name'],
                'city': item['convent_staging__city__name'],
                'announcement_url': item['convent_staging__convent__url'],
                'start_date': item['convent_staging__start_date'],
                'end_date': item['convent_staging__end_date'],
                'finished': str(item['convent_staging__end_date'] < date.today()),
            }

            if item['convent_staging__convent__name'] and not current_convent_staging in schedule:
                schedule.append(current_convent_staging)

            schedule.append({
                'id': item['id'],
                'city': item['city__name'] or item['convent_staging__city__name'],
                'convent_name': item['convent_staging__convent__name'],
                'announcement_url': item['announcement_url'],
                'date': item['date'],
                'game_name': item['game__name'],
                'finished': str(item['date'] < date.today()),
            })

        while void_convent_staging:
            schedule.append({
                'convent_id': void_convent_staging[0]['id'],
                'convent_name': void_convent_staging[0]['convent__name'],
                'city': void_convent_staging[0]['city__name'],
                'announcement_url': void_convent_staging[0]['convent__url'],
                'start_date': void_convent_staging[0]['start_date'],
                'end_date': void_convent_staging[0]['end_date'],
                'finished': str(void_convent_staging[0]['end_date'] < date.today()),
            })
            void_convent_staging = void_convent_staging[1:]

        response_data = {
            'schedule': schedule
        }

        return Response(response_data)


class ParseGoogleSheet(APIView):
    def get(self, request, id):
        if request.user.is_anonymous or not request.user.is_superuser:
            return Response({'results': []})
        credentials = service_account.Credentials.from_service_account_file('/rularpgames-cec15a3f2c66.json', 
                                                                            scopes=['https://www.googleapis.com/auth/spreadsheets'])

        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = id

        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=sheets[0]['properties']['title']).execute()

        values = result.get('values', [])

        results = []
        for item in values:
            if 'Название' in item[0] or 'название' in item[0]:
                continue
            while len(item) < 11:
                item.append('')
            convent, start_date, end_date, city, game_name, announcement, short_announcement, red_flags, author, master_group, announcement_url = item[0:11]

            current_city, created = City.objects.get_or_create(name=city)
            if convent:
                current_convent, created = Convent.objects.get_or_create(name=convent)
                if not current_convent.url and not game_name:
                    current_convent.url = announcement_url
                    current_convent.save()
                current_convent_staging, created = ConventStaging.objects.get_or_create(convent=current_convent, 
                                                                                        start_date=datetime.strptime(start_date, "%d.%m.%Y"), 
                                                                                        end_date=datetime.strptime(end_date, "%d.%m.%Y"), 
                                                                                        city=current_city)
            else:
                current_convent_staging = None

            if game_name:
                current_game, created = Game.objects.get_or_create(name=game_name)
                if not current_game.announcement:
                    current_game.announcement = announcement
                if not current_game.short_announcement:
                    current_game.short_announcement = short_announcement
                if not current_game.red_flags:
                    current_game.red_flags = red_flags
                if master_group:
                    current_master_group, created = MasterGroup.objects.get_or_create(name=master_group)                    
                    current_game.master_group = current_master_group
                current_game.save()

                current_game_staging, created = Staging.objects.get_or_create(game=current_game, 
                                                                                date=datetime.strptime(start_date, "%d.%m.%Y"), 
                                                                                city=current_city, 
                                                                                convent_staging=current_convent_staging)
                if announcement_url:
                    current_game_staging.announcement_url = announcement_url
                    current_game_staging.save()


            results.append({
                'convent': convent,
                'start_date': start_date,
                'end_date': end_date,
                'city': city,
                'game_name': game_name,
                'announcement': announcement,
                'short_announcement': short_announcement,
                'red_flags': red_flags,
                'author': author,
                'master_group': master_group,
            })

        return Response({'results': results})


class GameDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, id, format=None):
        game = Game.objects.get(id=id)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def post(self, request, format=None):
        id = request.data.get('id')
        user = request.user
        if id:
            try:
                game = Game.objects.get(id=id)
                serializer = GameSerializer(game, 
                                            data=request.data, 
                                            partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Game.DoesNotExist:
                return Response({"detail": "Game not found."}, status=status.HTTP_404_NOT_FOUND)

        else:
            serializer = GameSerializer(data=request.data)
            if serializer.is_valid():
                current_game = serializer.save()
                current_game.creator_id = user.id
                current_game.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
