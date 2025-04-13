from django.urls import path
from .views_api import CombinedView, StageDetailView, PersonDetailView, LoggedUserView, ConventDetailView, CityView, GameRegistrationView, CSRFTokenView, GameDetailView
from .views_api import ParseGoogleSheet

urlpatterns = [
    path('logged_user/', LoggedUserView.as_view(), name='logged-user'),
    path('city/', CityView.as_view(), name='city'),
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf-token'),
    path('schedule/', CombinedView.as_view(), name='schedule'),
    path('game_detail/', GameDetailView.as_view(), name='game-detail'),
    path('game_detail/<int:id>/', GameDetailView.as_view(), name='game-detail-with-id'),
    path('stage_detail/<int:id>/', StageDetailView.as_view(), name='stage-detail'),
    path('game_registration/<int:id>/', GameRegistrationView.as_view(), name='game-registration-detail'),
    path('convent_detail/<int:id>/', ConventDetailView.as_view(), name='convent-detail'),
    path('person_detail/<int:id>/', PersonDetailView.as_view(), name='person-detail'),
    path('google_sheets/<str:id>/', ParseGoogleSheet.as_view(), name='parse-google-sheet'),
]