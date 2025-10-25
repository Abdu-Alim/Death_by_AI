from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Player, Situation, GameSession, PlayerAction
from .api_client import DeepSeekClient
import random

def home(request):
    """Главная страница"""
    return render(request, 'game/home.html')

def start_game(request):
    """Начало новой игры"""
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        
        if not player_name:
            return render(request, 'game/start.html', {'error': 'Введите имя игрока'})
        
        # Создаем или находим игрока
        player, created = Player.objects.get_or_create(name=player_name)
        
        # Выбираем случайную ситуацию
        situations = Situation.objects.all()
        if situations:
            situation = random.choice(situations)
        else:
            # Если нет ситуаций, создаем через API
            api_client = DeepSeekClient()
            situation_text = api_client.generate_situation('nature')
            situation = Situation.objects.create(
                text=situation_text,
                category='nature'
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
    
    # Проверяем, активна ли еще сессия
    if not game_session.is_active or game_session.lives <= 0:
        return redirect('result_page', session_id=session_id)
    
    return render(request, 'game/game.html', {
        'game_session': game_session
    })

def submit_action(request, session_id):
    """Обработка действия игрока"""
    if request.method == 'POST':
        game_session = get_object_or_404(GameSession, id=session_id)
        action_text = request.POST.get('action_text', '')
        
        if not action_text:
            return redirect('game_page', session_id=session_id)
        
        # Используем API для оценки
        api_client = DeepSeekClient()
        survived, feedback = api_client.evaluate_survival_plan(
            game_session.situation.text, 
            action_text
        )
        
        # Создаем запись о действии
        player_action = PlayerAction.objects.create(
            game_session=game_session,
            action_text=action_text,
            survived=survived,
            feedback=feedback
        )
        
        # Обновляем игровую сессию
        if survived:
            game_session.score += 1
        else:
            game_session.lives -= 1
            
        if game_session.lives <= 0:
            game_session.is_active = False
            
        game_session.save()
        
        return redirect('result_page', session_id=session_id)
    
    return redirect('game_page', session_id=session_id)

def result_page(request, session_id):
    """Страница с результатом раунда"""
    game_session = get_object_or_404(GameSession, id=session_id)
    latest_action = PlayerAction.objects.filter(game_session=game_session).last()
    
    return render(request, 'game/result.html', {
        'game_session': game_session,
        'player_action': latest_action,
        'survived': latest_action.survived if latest_action else False
    })

def leaderboard(request):
    """Таблица лидеров"""
    # Получаем лучшие результаты (игроки с максимальным счетом)
    best_sessions = GameSession.objects.filter(is_active=False).order_by('-score', '-id')[:10]
    return render(request, 'game/leaderboard.html', {
        'leaders': best_sessions
    })

def create_situation(request):
    """Создание пользовательской ситуации"""
    if request.method == 'POST':
        text = request.POST.get('situation_text')
        category = request.POST.get('category')
        
        if not text or not category:
            return render(request, 'game/create_situation.html', {
                'error': 'Заполните все поля'
            })
        
        Situation.objects.create(
            text=text,
            category=category,
            is_user_created=True
        )
        
        return redirect('home')
    
    return render(request, 'game/create_situation.html')

def about(request):
    """Страница о проекте"""
    return render(request, 'game/about.html')

def generate_ai_situation(request):
    """Генерация ситуации через AI (AJAX)"""
    if request.method == 'POST':
        category = request.POST.get('category', 'nature')
        
        api_client = DeepSeekClient()
        situation_text = api_client.generate_situation(category)
        
        # Сохраняем в базу
        situation = Situation.objects.create(
            text=situation_text,
            category=category,
            is_user_created=False
        )
        
        return JsonResponse({
            'success': True,
            'situation': situation_text,
            'situation_id': situation.id
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})