from datetime import datetime

class Player:

    def __init__(self, date: datetime, id: int, elo: int, ign: str, wins: int, losses: int, streak: int):
        self.date = date
        self.id = id
        self.elo = elo
        self.ign = ign
        self.wins = wins
        self.losses = losses
        self.streak = streak