class Player:

    def __init__(self, date, id, elo, ign, wins, losses, streak):
        self.date = date
        self.id = id
        self.elo = elo
        self.ign = ign
        self.wins = wins
        self.losses = losses
        self.streak = streak

    def eloChange(self, enemy_avg, team_avg, cond):
        if cond:
            self.elo += (abs(enemy_avg - team_avg))
        else:
            self.elo -= (abs(enemy_avg - team_avg))
