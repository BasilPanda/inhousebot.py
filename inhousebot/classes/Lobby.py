class Lobby:
    """
    Lobby class holds information on how a lobby is setup
    """
    LOBBY_TYPES = {
        0: "None",
        1: "League of Legends",     # 5v5
        2: "4v4",
        3: "Rocket League",         # 3v3
    }

    def __init__(self, _lobbyType):
        self.players = []
        self.rightSide = []
        self.leftSide = []
        self.captains = []
        self.lobbyType = _lobbyType

