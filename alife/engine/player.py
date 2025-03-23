class Player:
    def __init__(self, name):
        self.name = name
        self.location_id = None
        self.inventory = ["medkit", "vodka", "bread"]
        self.health = 100
        self.radiation = 0
        self.faction_reputation = {
            "loners": 0,
            "duty": 0,
            "freedom": 0,
            "ecologists": 0,
            "military": 0
        }
