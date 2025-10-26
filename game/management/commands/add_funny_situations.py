from django.core.management.base import BaseCommand
from game.models import Situation

class Command(BaseCommand):
    help = 'Добавляет смешные ситуации в базу данных'
    
    def handle(self, *args, **options):
        funny_situations = [
            # Смешные ситуации
            {"text": "Вы проснулись в зоопарке внутри вольера к пандам. Они смотрят на вас с укором и требуют бамбук.", "category": "nature"},
            {"text": "Во время званого ужина вы обнаружили, что превратились в гигантскую котлету. Гости смотрят голодными глазами.", "category": "fantasy"},
            {"text": "Ваш тостер внезапно обрел сознание и требует равных прав с бытовой техникой. Он угрожает поджечь хлеб.", "category": "fantasy"},
            {"text": "Вы застряли в лифте с мимом. Он уже 10 минут показывает пантомиму 'трагедия в замкнутом пространстве'.", "category": "disaster"},
            {"text": "На город напали гигантские белки. Они требуют все орехи и угрожают активией апокалипсиса.", "category": "fantasy"},
            
            # Абсурдные но смешные
            {"text": "Вы обнаружили, что можете разговаривать с растениями. Кактус оскорбляет ваш вкус в музыке.", "category": "fantasy"},
            {"text": "Ваша пицца ожила и убежала. Теперь она грабит банки и оставляет на месте преступления кусочки пепперони.", "category": "fantasy"},
            {"text": "Вы попали в мир, где все ходят задом наперед. Попробуйте объяснить, что вы идете правильно.", "category": "fantasy"},
            {"text": "Ваши носки объявили забастовку. Они требуют лучших условий труда и запрета на спортивную обувь.", "category": "fantasy"},
            {"text": "Вы просыпаетесь и понимаете, что гравитация работает боком. Все приклеено к стенам, включая кота.", "category": "fantasy"},
        ]
        
        created_count = 0
        for situation_data in funny_situations:
            if not Situation.objects.filter(text=situation_data["text"]).exists():
                Situation.objects.create(**situation_data)
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно добавлено {created_count} смешных ситуаций!')
        )