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
        """Оценка плана выживания через DeepSeek API"""
        if not self.api_key or self.api_key == 'your_deepseek_api_key_here':
            return self._get_fallback_evaluation(player_plan)
        
        prompt = f"""
        Ты - эксперт по выживанию в экстремальных ситуациях. Оцени план игрока и реши, выживет ли он.
        
        СИТУАЦИЯ: {situation_text}
        ПЛАН ИГРОКА: {player_plan}
        
        Проанализируй план по следующим критериям:
        1. Логичность и реализуемость
        2. Учет доступных ресурсов и условий
        3. Опасности, которые игрок не учел
        4. Альтернативные варианты действий
        
        Верни ответ в формате JSON:
        {{
            "survived": true/false,
            "score": число от 1 до 10,
            "feedback": "развернутый фидбэк с объяснением решения, 2-3 предложения",
            "reasoning": "краткое объяснение почему выжил/не выжил"
        }}
        
        Будь строгим, но справедливым. Реальные шансы на выживание в таких ситуациях обычно низкие.
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
                        {'role': 'system', 'content': 'Ты строгий эксперт по выживанию. Оценивай реалистично.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 300,
                    'temperature': 0.3
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                evaluation_text = data['choices'][0]['message']['content'].strip()
                
                # Парсим JSON ответ
                try:
                    evaluation = json.loads(evaluation_text)
                    survived = evaluation.get('survived', False)
                    feedback = evaluation.get('feedback', 'Не удалось оценить план.')
                    return survived, feedback
                except json.JSONDecodeError:
                    # Если API вернуло не JSON, используем fallback
                    return self._get_fallback_evaluation(player_plan)
            else:
                print(f"API Error: {response.status_code}")
                return self._get_fallback_evaluation(player_plan)
                
        except Exception as e:
            print(f"API Connection Error: {e}")
            return self._get_fallback_evaluation(player_plan)
    
    def _get_fallback_situation(self, category):
        """Резервная ситуация если API недоступно"""
        fallback_situations = {
            'nature': [
                "Вы заблудились в глубокой пещере. Фонарик садится, а пути назад вы не помните.",
                "Во время шторма вашу лодку выбросило на необитаемый остров. Рации нет, еды на 2 дня.",
                "Вы встретили медведя гризли в лесу. Медведь заметил вас и начинает приближаться."
            ],
            'disaster': [
                "В небоскребе начался пожар. Вы на 25 этаже, лифты не работают, лестница заполнена дымом.",
                "На атомной электростанции произошла авария. Объявлена эвакуация, но дороги загружены.",
                "Наводнение затопило город. Вы на крыше дома, вода поднимается, помощи не видно."
            ],
            'fantasy': [
                "Вы обнаружили, что можете читать мысли. Но теперь чужие мысли мешают вам сосредоточиться.",
                "Вам подарили кольцо, которое исполняет желания, но каждое исполнение имеет случайные побочные эффекты.",
                "Вы попали в мир, где технологии не работают, а магия реальна, но вы единственный без магических способностей."
            ]
        }
        return random.choice(fallback_situations.get(category, fallback_situations['nature']))
    
    def _get_fallback_evaluation(self, player_plan):
        """Резервная оценка если API недоступно"""
        plan_lower = player_plan.lower()
        
        # Улучшенная логика оценки
        positive_indicators = ['план', 'укрытие', 'помощь', 'сигнал', 'сохранение', 'анализ', 'осторожно']
        negative_indicators = ['паника', 'сдаться', 'бежать', 'кричать', 'не знаю', 'надежда']
        
        positive_score = sum(1 for word in positive_indicators if word in plan_lower)
        negative_score = sum(1 for word in negative_indicators if word in plan_lower)
        
        survived = positive_score > negative_score and len(player_plan) > 50
        
        if survived:
            feedback = "✅ Ваш план демонстрирует логичное мышление в условиях стресса. Вы учли основные аспекты выживания."
        else:
            feedback = "❌ План недостаточно продуман для данной ситуации. В реальных условиях шансы на выживание были бы низкими."
        
        return survived, feedback