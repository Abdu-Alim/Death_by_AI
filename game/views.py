from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Player, Situation, GameSession, PlayerAction
import random
import json
import random
from django.views.decorators.csrf import csrf_exempt

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

def evaluate_survival(action_text, situation_text):
    """
    Функция для оценки выживания (пока заглушка)
    В День 4 заменим на реальный вызов DeepSeek API
    """
    # Простая логика оценки по ключевым словам
    positive_keywords = ['огонь', 'укрытие', 'помощь', 'спасение', 'сигнал', 'вода', 'еда', 'тепло']
    negative_keywords = ['сдаться', 'плакать', 'бежать', 'паника', 'отчаяние']
    
    action_lower = action_text.lower()
    
    # Подсчитываем баллы
    score = 0
    for keyword in positive_keywords:
        if keyword in action_lower:
            score += 2
    
    for keyword in negative_keywords:
        if keyword in action_lower:
            score -= 1
    
    # Определяем результат
    survived = score > 2
    feedback = ""
    
    if survived:
        feedback = "✅ ИИ оценил ваш план как эффективный! Вы выжили благодаря продуманным действиям."
    else:
        feedback = "❌ ИИ счел ваш план недостаточно эффективным. В реальной ситуации шансы на выживание были бы низкими."
    
    return survived, feedback
def submit_action(request, session_id):
    """Обработка действия игрока"""
    if request.method == 'POST':
        game_session = get_object_or_404(GameSession, id=session_id)
        action_text = request.POST.get('action_text', '')
        
        # Оцениваем выживание (пока заглушка)
        survived, feedback = evaluate_survival(action_text, game_session.situation.text)
        
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
        
        return render(request, 'game/result.html', {
            'game_session': game_session,
            'player_action': player_action,
            'survived': survived
        })
    
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
