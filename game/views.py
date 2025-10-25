from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Player, Situation, GameSession, PlayerAction
import random

def home(request):
    """Главная страница"""
    return render(request, 'game/home.html')

def start_game(request):
    """Начало новой игры"""
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        
        # Создаем или находим игрока
        player, created = Player.objects.get_or_create(name=player_name)
        
        # Выбираем случайную ситуацию
        situations = Situation.objects.all()
        if situations:
            situation = random.choice(situations)
        else:
            # Если нет ситуаций, создаем базовую
            situation = Situation.objects.create(
                text="Вы оказались один в джунглях ночью. Вокруг слышны странные звуки.",
                category="nature"
            )
        
        # Создаем игровую сессию
        game_session = GameSession.objects.create(
            player=player,
            situation=situation,
            lives=3,
            score=0
        )
        
        return redirect('game_page', session_id=game_session.id)
    
    return render(request, 'game/start.html')

def game_page(request, session_id):
    """Страница игры"""
    game_session = get_object_or_404(GameSession, id=session_id)
    return render(request, 'game/game.html', {
        'game_session': game_session
    })

def leaderboard(request):
    """Таблица лидеров"""
    leaders = GameSession.objects.filter(is_active=False).order_by('-score')[:10]
    return render(request, 'game/leaderboard.html', {
        'leaders': leaders
    })

def create_situation(request):
    """Создание пользовательской ситуации"""
    if request.method == 'POST':
        text = request.POST.get('situation_text')
        category = request.POST.get('category')
        
        Situation.objects.create(
            text=text,
            category=category,
            is_user_created=True
        )
        
        return redirect('home')
    
    return render(request, 'game/create_situation.html')