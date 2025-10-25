from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_game, name='start_game'),
    path('game/<int:session_id>/', views.game_page, name='game_page'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('create_situation/', views.create_situation, name='create_situation'),
]