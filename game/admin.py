from django.contrib import admin
from .models import Player, Situation, GameSession, PlayerAction

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

@admin.register(Situation)
class SituationAdmin(admin.ModelAdmin):
    list_display = ['category', 'text', 'created_by', 'created_at']
    list_filter = ['category', 'is_user_created']

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['player', 'score', 'lives', 'is_active', 'created_at']
    list_filter = ['is_active']

@admin.register(PlayerAction)
class PlayerActionAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'survived', 'created_at']
    list_filter = ['survived']