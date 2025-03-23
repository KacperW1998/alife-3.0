import asyncio
import os
from dotenv import load_dotenv
from alife.engine.game_state import GameState
from alife.engine.ui_manager import UIManager
from alife.engine.player import Player

load_dotenv()  # Load environment variables from .env file


async def main():
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        return

    # Initialize game
    game_state = GameState()
    await game_state.load_game_data()
    ui = UIManager()

    # Intro and character creation
    print("Welcome to S.T.A.L.K.E.R: Shadows of Truth")
    print("=========================================")
    print("In this demo, you'll play as a stalker investigating the mysterious disappearance of Professor Kalancha.")
    print("This is a text-based adventure showcasing dynamic NPC memory and relationships.")
    print()
    player_name = input("Enter your stalker name: ")
    game_state.player = Player(player_name)
    game_state.player.location_id = "rookie_village"

    # Game introduction
    game_text = f"""Welcome to the Zone, {player_name}.

You find yourself in Rookie Village, a relatively safe haven on the edge of the Zone.
The air smells of campfire smoke and the faint metallic tang of radiation.
A few stalkers mill about, some eyeing you with curiosity.

Type 'help' to see available commands.
"""

    # Main game loop
    running = True
    current_npc = None
    conversation_active = False
    conversation_history = []

    while running:
        # Render the split screen
        current_location = game_state.get_location(game_state.player.location_id)
        ui.render_screen(game_text, current_npc, game_state, current_location)

        # Get player input
        command = input("> ").strip().lower()

        if conversation_active:
            # In conversation mode
            if command == "exit" or command == "bye":
                # End conversation and update NPC memory
                game_text = "Updating NPC memory..."
                ui.render_screen(game_text, current_npc, game_state, current_location)

                await current_npc.update_memory(conversation_history, game_state)
                conversation_active = False
                current_npc = None
                game_text = "You end the conversation."
                conversation_history = []
            else:
                # Show thinking message
                game_text = f"You: {command}\n\n{current_npc.static_traits['name']} is thinking..."
                ui.render_screen(game_text, current_npc, game_state, current_location)

                # Continue conversation with NPC
                response = await current_npc.generate_response(command, conversation_history, game_state)
                game_text = f"You: {command}\n\n{current_npc.static_traits['name']}: {response}"
                conversation_history.append({"role": "user", "content": command})
                conversation_history.append({"role": "assistant", "content": response})
        else:
            # Normal game mode - parse commands
            if command == "help":
                game_text = """Available commands:
- look: Examine your surroundings
- talk [npc_name]: Start a conversation with an NPC
- go [location]: Travel to a connected location
- inventory: Check your belongings
- examine [item]: Look at an item more closely
- exit/quit: End the game
"""
            elif command == "look":
                npcs_here = [npc for npc in game_state.npcs.values()
                             if npc.dynamic_state["location"] == game_state.player.location_id]
                npc_list = ", ".join([npc.static_traits["name"] for npc in npcs_here])

                game_text = f"{current_location['description']}\n\n"
                game_text += f"NPCs present: {npc_list if npc_list else 'None'}\n\n"
                game_text += f"Connected locations: {', '.join(current_location['connected_to'])}"

            elif command.startswith("talk "):
                npc_name = command[5:].strip().lower()
                # Find the NPC by name
                found_npc = None
                for npc in game_state.npcs.values():
                    if npc.static_traits["name"].lower() == npc_name and npc.dynamic_state[
                        "location"] == game_state.player.location_id:
                        found_npc = npc
                        break

                if found_npc:
                    current_npc = found_npc
                    conversation_active = True
                    conversation_history = []

                    # Show thinking message
                    game_text = f"Approaching {current_npc.static_traits['name']}..."
                    ui.render_screen(game_text, current_npc, game_state, current_location)

                    greeting = await current_npc.get_greeting(game_state)
                    game_text = f"{current_npc.static_traits['name']}: {greeting}"
                    conversation_history.append({"role": "assistant", "content": greeting})
                else:
                    game_text = f"There's no one named '{npc_name}' here."

            elif command.startswith("go "):
                location_name = command[3:].strip().lower()
                if location_name in current_location["connected_to"]:
                    game_state.player.location_id = location_name
                    new_location = game_state.get_location(location_name)
                    game_text = f"You travel to {new_location['name']}.\n\n{new_location['description']}"
                else:
                    game_text = f"You can't go to '{location_name}' from here."

            elif command == "inventory":
                if game_state.player.inventory:
                    game_text = "Your inventory contains:\n- " + "\n- ".join(game_state.player.inventory)
                else:
                    game_text = "Your inventory is empty."

            elif command == "exit" or command == "quit":
                running = False
                game_text = "Thank you for playing!"

            else:
                game_text = "Unknown command. Type 'help' for a list of commands."

    print(game_text)
    print("Demo complete. Thanks for playing!")


if __name__ == "__main__":
    asyncio.run(main())
