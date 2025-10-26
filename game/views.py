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
        player_name = request.POST.get('player_name').strip()
        
        if not player_name:
            return render(request, 'game/start.html', {'error': 'Введите имя игрока'})
        
        # Нормализуем имя (убираем лишние пробелы, приводим к одному регистру)
        normalized_name = ' '.join(player_name.split()).title()
        
        # Ищем существующего игрока или создаем нового
        player, created = Player.objects.get_or_create(
            name=normalized_name,
            defaults={'name': normalized_name}
        )
        
        # Если у игрока есть активные сессии, завершаем их
        active_sessions = GameSession.objects.filter(player=player, is_active=True)
        for session in active_sessions:
            session.is_active = False
            session.save()
        
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
        
        # Создаем новую игровую сессию
        game_session = GameSession.objects.create(
            player=player,
            situation=situation,
            lives=3,
            score=0
        )
        
        return redirect('game_page', session_id=game_session.id)
    
    return render(request, 'game/start.html')

def game_page(request, session_id):
    """Страница игры - ПРОСТАЯ ВЕРСИЯ"""
    game_session = get_object_or_404(GameSession, id=session_id)
    
    # Базовая проверка - если игра завершена, показываем результат
    if not game_session.is_active or game_session.lives <= 0:
        return redirect('result_page', session_id=session_id)
    
    return render(request, 'game/game.html', {
        'game_session': game_session
    })

def submit_action(request, session_id):
    """Обработка действия игрока - ПРОСТАЯ ВЕРСИЯ"""
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
        PlayerAction.objects.create(
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

def next_situation(request, session_id):
    """Переход к следующей ситуации - УЛУЧШЕННАЯ ВЕРСИЯ"""
    game_session = get_object_or_404(GameSession, id=session_id)
    
    # Проверяем, активна ли еще сессия
    if not game_session.is_active or game_session.lives <= 0:
        return redirect('result_page', session_id=session_id)
    
    # Выбираем случайную ситуацию (ВСЕГДА новую)
    situations = Situation.objects.all()
    
    if situations.count() > 1:
        # Если есть больше одной ситуации, исключаем текущую
        current_situation = game_session.situation
        available_situations = situations.exclude(id=current_situation.id)
        if available_situations.exists():
            new_situation = random.choice(available_situations)
        else:
            new_situation = random.choice(situations)
    else:
        new_situation = situations.first()
    
    # Обновляем сессию с новой ситуацией
    game_session.situation = new_situation
    game_session.save()
    
    print(f"DEBUG: Changed situation from {game_session.situation.id} to {new_situation.id}")  # Для отладки
    
    return redirect('game_page', session_id=session_id)

def result_page(request, session_id):
    """Страница с результатом раунда"""
    game_session = get_object_or_404(GameSession, id=session_id)
    latest_action = PlayerAction.objects.filter(game_session=game_session).order_by('-created_at').first()
    
    return render(request, 'game/result.html', {
        'game_session': game_session,
        'player_action': latest_action,
        'survived': latest_action.survived if latest_action else False
    })

def leaderboard(request):
    """Таблица лидеров - показывает лучший результат каждого игрока"""
    # Получаем максимальный счет для каждого игрока
    from django.db.models import Max
    
    best_scores = GameSession.objects.values('player__name').annotate(
        best_score=Max('score')
    ).order_by('-best_score')[:10]
    
    # Собираем информацию для отображения
    leaders = []
    for score_data in best_scores:
        player_name = score_data['player__name']
        best_score = score_data['best_score']
        
        # Находим сессию с этим счетом
        best_session = GameSession.objects.filter(
            player__name=player_name, 
            score=best_score
        ).order_by('-id').first()
        
        if best_session:
            leaders.append(best_session)
    
    return render(request, 'game/leaderboard.html', {
        'leaders': leaders
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