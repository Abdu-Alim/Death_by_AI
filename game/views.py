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

# ЗАМЕНИТЕ функцию evaluate_survival на эту улучшенную версию:
def evaluate_survival(action_text, situation_text):
    """
    Улучшенная функция оценки выживания с учетом категории ситуации
    """
    action_lower = action_text.lower()
    
    # Более сложная система ключевых слов по категориям
    category_keywords = {
        'nature': {
            'positive': ['укрытие', 'огонь', 'сигнал', 'вода', 'ориентация', 'сохранение тепла', 'ягоды', 'рыба', 'охота'],
            'negative': ['паника', 'бежать', 'сдаться', 'кричать', 'отчаяние', 'бездействие']
        },
        'disaster': {
            'positive': ['эвакуация', 'помощь', 'медицина', 'укрытие', 'запас', 'план', 'спокойствие', 'организация'],
            'negative': ['паника', 'толпа', 'замкнутость', 'импульсивность', 'одиночество']
        },
        'fantasy': {
            'positive': ['анализ', 'технологии', 'изобретательность', 'логика', 'адаптация', 'исследование', 'хитрость'],
            'negative': ['неверие', 'отказ', 'страх', 'бегство', 'агрессия']
        }
    }
    
    # Определяем категорию ситуации (упрощенно)
    category = 'nature'  # по умолчанию
    if 'космическ' in situation_text.lower() or 'робот' in situation_text.lower():
        category = 'fantasy'
    elif 'землетрясение' in situation_text.lower() or 'цунами' in situation_text.lower() or 'авария' in situation_text.lower():
        category = 'disaster'
    
    # Получаем ключевые слова для категории
    keywords = category_keywords.get(category, category_keywords['nature'])
    
    # Подсчитываем баллы
    score = 0
    feedback_parts = []
    
    for positive_word in keywords['positive']:
        if positive_word in action_lower:
            score += 2
            feedback_parts.append(f"✓ Упоминание '{positive_word}' увеличивает шансы на выживание")
    
    for negative_word in keywords['negative']:
        if negative_word in action_lower:
            score -= 3
            feedback_parts.append(f"✗ '{negative_word}' может снизить ваши шансы")
    
    # Дополнительные факторы
    if len(action_text) > 100:
        score += 1  # Детальный план
        feedback_parts.append("✓ Детальный план увеличивает шансы")
    
    if 'план' in action_lower or 'стратегия' in action_lower:
        score += 1
        feedback_parts.append("✓ Наличие плана - хороший признак")
    
    # Определяем результат
    survived = score >= 3
    
    # Формируем фидбэк
    if survived:
        main_feedback = "✅ ИИ оценил ваш план как эффективный! Вы демонстрируете хорошие навыки выживания."
    else:
        main_feedback = "❌ ИИ счел ваш план недостаточно продуманным. В реальной ситуации шансы были бы низкими."
    
    # Объединяем все части фидбэка
    if feedback_parts:
        detailed_feedback = "\n".join(feedback_parts)
        full_feedback = f"{main_feedback}\n\nАнализ:\n{detailed_feedback}"
    else:
        full_feedback = main_feedback + "\n\nПлан слишком общий, попробуйте быть конкретнее."
    
    return survived, full_feedback
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
def about(request):
    """Страница о проекте"""
    return render(request, 'game/about.html')