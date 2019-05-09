class Player:

    def __init__(self, date, id, elo, ign, wins, losses, streak, tier, rank):
        self.date = date
        self.id = id
        self.elo = elo
        self.ign = ign
        self.wins = wins
        self.losses = losses
        self.streak = streak
        self.tier = tier
        self.rank = rank

    def to_list(self):
        tolist = [self.date, self.id, self.elo, self.ign, self.wins, self.losses, self.streak, self.tier, self.rank]
        return tolist
