from django.db import models
from datetime import datetime

class History(models.Model):
    csrf_token = models.CharField(max_length=96)
    timestamp = models.CharField(max_length=24, default = datetime.now().timestamp())
    date = models.CharField(max_length=16, default = datetime.now().strftime('%d %b %Y'))
    time = models.CharField(max_length=16, default = datetime.now().strftime('%H:%M:%S'))
    game_fen = models.CharField(max_length=96, default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") # current game fen
    moves = models.CharField(max_length=512, default="") # moves list
    status = models.CharField(max_length=48, default="White") # whose turn 
    winner = models.CharField(max_length=48, blank = True) # who won
    condition = models.CharField(max_length=32, default="In Progress") # in progress / condition for win
    computer_time_left = models.CharField(max_length=16, default="") 
    player_time_left = models.CharField(max_length=16, default="")