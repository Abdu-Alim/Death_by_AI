from django.db import models

class Player(models.Model):
    CATEGORY_CHOICES = [
        ('nature', 'Природа'),
        ('disaster', 'Катастрофа'),
        ('fantasy', 'Фантастика'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Situation(models.Model):
    CATEGORY_CHOICES = [
        ('nature', 'Природа'),
        ('disaster', 'Катастрофа'),
        ('fantasy', 'Фантастика'),
    ]
    
    text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_by = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)
    is_user_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category}: {self.text[:50]}..."

class GameSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    situation = models.ForeignKey(Situation, on_delete=models.CASCADE)
    lives = models.IntegerField(default=3)
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.name} - Score: {self.score}"

class PlayerAction(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    action_text = models.TextField()
    survived = models.BooleanField(default=False)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.game_session.player.name} - Survived: {self.survived}"