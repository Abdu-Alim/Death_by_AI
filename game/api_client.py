import requests
import json
import random
from django.conf import settings
from .models import Situation

class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.timeout = settings.TIMEOUT
        
    def generate_situation(self, category):
        """Генерация ситуации через DeepSeek API"""
        if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
            return self._get_fallback_situation(category)
        
        prompt = f"""
        Создай уникальную и сложную смертельно опасную ситуацию в категории "{category}".
        Ситуация должна быть реалистичной (если это не фантастика) и требовать от игрока продуманного плана выживания.
        Опиши ситуацию кратко, но детально - 2-3 предложения.
        Категория: {category}
        
        Примеры хороших ситуаций:
        - "Вы проснулись в джунглях ночью. Вокруг слышны рычание хищников и странные шелесты. У вас только нож и фонарик."
        - "Землетрясение разрушило здание, и вы оказались в ловушке в подвале. Вода постепенно поднимается."
        - "Во время эксперимента с порталом вы перенеслись в параллельное измерение, где законы физики работают иначе."
        
        Верни ТОЛЬКО текст ситуации, без дополнительных комментариев.
        """
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'Ты создатель сложных и интересных сценариев для игры на выживание.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 150,
                    'temperature': 0.8
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                situation_text = data['choices'][0]['message']['content'].strip()
                return situation_text
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self._get_fallback_situation(category)
                
        except Exception as e:
            print(f"API Connection Error: {e}")
            return self._get_fallback_situation(category)
    
    def evaluate_survival_plan(self, situation_text, player_plan):
        """Строгая оценка плана выживания с генерацией продолжения истории"""
        if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
            return self._get_strict_fallback_evaluation(situation_text, player_plan)
        
        prompt = f"""
        Ты - СТРОГИЙ и РЕАЛИСТИЧНЫЙ эксперт по выживанию. Оцени план игрока и создай продолжение истории.
        
        СИТУАЦИЯ: {situation_text}
        ПЛАН ИГРОКА: {player_plan}
        
        Твоя задача:
        1. Оценить, выживет ли игрок (survived: true/false) - будь СТРОГИМ!
        2. Написать короткое продолжение истории (2-3 предложения), что произошло дальше
        3. Дать краткий анализ плана
        
        Критерии оценки (БУДЬ СТРОГИМ!):
        - План должен быть логичным и реалистичным
        - Действия должны соответствовать ситуации
        - Учитывай физические ограничения и время
        - Бессмысленные или абсурдные планы = смерть
        - Слишком короткие или общие планы = смерть
        - Отсутствие конкретных действий = смерть
        
        Верни ответ в формате JSON:
        {{
            "survived": true/false,
            "story_continuation": "Что произошло дальше...",
            "analysis": "Краткий анализ плана"
        }}
        """
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'Ты строгий эксперт по выживанию. Оценивай планы реалистично и без снисхождения.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 350,
                    'temperature': 0.8
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                evaluation_text = data['choices'][0]['message']['content'].strip()
                
                # Парсим JSON ответ
                try:
                    evaluation = json.loads(evaluation_text)
                    survived = evaluation.get('survived', False)  # По умолчанию не выжил - СТРОГО!
                    story_continuation = evaluation.get('story_continuation', 'История не была продолжена.')
                    analysis = evaluation.get('analysis', 'Анализ не предоставлен.')
                    
                    # Формируем финальный фидбэк
                    if survived:
                        feedback = f"🎉 ВЫ ВЫЖИЛИ!\n\n📖 Что произошло: {story_continuation}\n\n📊 Анализ: {analysis}"
                    else:
                        feedback = f"💀 ВЫ ПОГИБЛИ...\n\n📖 Что произошло: {story_continuation}\n\n📊 Анализ: {analysis}"
                    
                    return survived, feedback
                    
                except json.JSONDecodeError:
                    print(f"JSON Parse Error: {evaluation_text}")
                    return self._get_strict_fallback_evaluation(situation_text, player_plan)
            else:
                print(f"API Error: {response.status_code}")
                return self._get_strict_fallback_evaluation(situation_text, player_plan)
                
        except Exception as e:
            print(f"API Connection Error: {e}")
            return self._get_strict_fallback_evaluation(situation_text, player_plan)

    def _get_strict_fallback_evaluation(self, situation_text, player_plan):
        """Строгая резервная оценка с генерацией истории"""
        plan_lower = player_plan.lower().strip()
        
        # СТРОГАЯ логика оценки
        survival_chance = 0.3  # Только 30% шанс выжить по умолчанию
        
        # Положительные факторы
        positive_keywords = [
            'укрытие', 'сигнал', 'сохранение', 'анализ', 'осторожно', 'план', 'поиск',
            'эвакуация', 'первая помощь', 'ориентир', 'ресурсы', 'стратегия', 'приоритет'
        ]
        
        # Отрицательные факторы
        negative_keywords = [
            'сдаться', 'умру', 'погибну', 'конец', 'прощай', 'паника', 'кричать',
            'бежать', 'надежда', 'магия', 'волшебство', 'суперсила', 'авось'
        ]
        
        # Оцениваем план
        positive_score = sum(2 for word in positive_keywords if word in plan_lower)
        negative_score = sum(3 for word in negative_keywords if word in plan_lower)
        
        # Длина плана важна
        length_bonus = min(len(player_plan) / 100, 0.4)  # Максимум +40% за длинный план
        
        survival_chance += (positive_score * 0.1) - (negative_score * 0.15) + length_bonus
        survival_chance = max(0.05, min(0.8, survival_chance))  # Ограничиваем шансы
        
        survived = random.random() < survival_chance
        
        # Генерируем продолжение истории
        if survived:
            story_templates = [
                f"Ваш план сработал! {random.choice(['Вы нашли укрытие', 'Вам удалось подать сигнал', 'Вы сохранили спокойствие'])} и {random.choice(['дождались помощи', 'нашли способ спастись', 'пережили опасность'])}.",
                f"Благодаря продуманным действиям {random.choice(['вы избежали главной угрозы', 'вам удалось стабилизировать ситуацию', 'вы нашли неожиданное решение'])} и {random.choice(['выжили вопреки всему', 'спасли себя', 'дожили до утра'])}.",
                f"Ваша стратегия оказалась эффективной. {random.choice(['Вы смогли', 'Вам удалось', 'Вы сумели'])} {random.choice(['обезопасить себя', 'найти помощь', 'переждать опасность'])} и теперь в безопасности."
            ]
            story = random.choice(story_templates)
            analysis = "План демонстрирует логичное мышление и учёт реальных обстоятельств."
        else:
            story_templates = [
                f"К сожалению, {random.choice(['ваш план не учел', 'вы недооценили', 'вы не предусмотрели'])} {random.choice(['главную опасность', 'временные ограничения', 'физические возможности'])}.",
                f"Ваши действия привели к {random.choice(['непредвиденным последствиям', 'ухудшению ситуации', 'катастрофическим результатам'])}. {random.choice(['Шансов не осталось', 'Спасение невозможно', 'Это конец'])}.",
                f"План оказался {random.choice(['неэффективным', 'опасным', 'нереалистичным'])}. {random.choice(['Ситуация вышла из-под контроля', 'Время было упущено', 'Ошибка оказалась фатальной'])}."
            ]
            story = random.choice(story_templates)
            analysis = "План недостаточно продуман для экстремальных условий выживания."
        
        # Формируем фидбэк
        if survived:
            feedback = f"🎉 ВЫ ВЫЖИЛИ!\n\n📖 Что произошло: {story}\n\n📊 Анализ: {analysis}"
        else:
            feedback = f"💀 ВЫ ПОГИБЛИ...\n\n📖 Что произошло: {story}\n\n📊 Анализ: {analysis}"
        
        return survived, feedback
        
    def _get_fallback_situation(self, category):
        """Резервная ситуация если API недоступно"""
        fallback_situations = {
            'nature': [
                "Вы заблудились в глубокой пещере. Фонарик садится, а пути назад вы не помните. Вокруг абсолютная темнота и тишина.",
                "Во время шторма вашу лодку выбросило на необитаемый остров. Рации нет, еды на 2 дня, пресная вода заканчивается.",
                "Вы встретили медведя гризли в лесу. Медведь заметил вас, встал на задние лапы и начинает приближаться. Убежать невозможно."
            ],
            'disaster': [
                "В небоскребе начался пожар. Вы на 25 этаже, лифты не работают, лестница заполнена едким дымом. Огонь распространяется быстро.",
                "На атомной электростанции произошла авария. Объявлена эвакуация, но дороги загружены. Уровень радиации растет с каждой минутой.",
                "Наводнение затопило город. Вы на крыше дома, вода поднимается, помощи не видно. Температура воды близка к нулю."
            ],
            'fantasy': [
                "Вы обнаружили, что можете читать мысли. Но теперь чужие мысли мешают вам сосредоточиться, а некоторые люди чувствуют ваше вторжение.",
                "Вам подарили кольцо, которое исполняет желания, но каждое исполнение имеет случайные побочные эффекты. Последнее желание вызвало катастрофу.",
                "Вы попали в мир, где технологии не работают, а магия реальна, но вы единственный без магических способностей. Местные жители считают вас угрозой."
            ]
        }
        return random.choice(fallback_situations.get(category, fallback_situations['nature']))