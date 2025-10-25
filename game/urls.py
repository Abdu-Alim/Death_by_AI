from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_game, name='start_game'),
    path('game/<int:session_id>/', views.game_page, name='game_page'),
    path('game/<int:session_id>/submit/', views.submit_action, name='submit_action'),
    path('game/<int:session_id>/result/', views.result_page, name='result_page'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('create_situation/', views.create_situation, name='create_situation'),
    path('about/', views.about, name='about'),
    path('generate-ai-situation/', views.generate_ai_situation, name='generate_ai_situation'),
]