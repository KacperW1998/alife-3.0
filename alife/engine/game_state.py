import json
import os
from alife.engine.npc_agent import NPCAgent


class GameState:
    def __init__(self):
        self.locations = {}
        self.npcs = {}
        self.items = {}
        self.player = None
        self.current_time = {"day": 1, "period": "morning"}
        self.main_plot = {
            "discovered_clues": {
                "professor_last_seen": False,
                "research_purpose": False,
                "lab_location": False
            }
        }

    async def load_game_data(self):
        # Load locations
        with open(os.path.join("data", "locations.json"), "r") as f:
            locations_data = json.load(f)
            for loc in locations_data:
                self.locations[loc["id"]] = loc

        # Load NPCs
        with open(os.path.join("data", "npcs.json"), "r") as f:
            npcs_data = json.load(f)
            for npc_data in npcs_data:
                self.npcs[npc_data["id"]] = NPCAgent(npc_data)

        # Load items
        with open(os.path.join("data", "items.json"), "r") as f:
            self.items = json.load(f)

    def get_location(self, location_id):
        return self.locations.get(location_id, {"name": "Unknown", "description": "You are lost.", "connected_to": []})
