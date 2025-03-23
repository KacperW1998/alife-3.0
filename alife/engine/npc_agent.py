import os
import json
from openai import OpenAI
from alife.engine.memory_updater import summarize_conversation


class NPCAgent:
    def __init__(self, npc_data):
        self.id = npc_data["id"]
        self.static_traits = npc_data["static_traits"]
        self.dynamic_state = npc_data["dynamic_state"]
        self.player_relationship = npc_data["player_relationship"]
        self.knowledge = npc_data["knowledge"]
        self.memory = []

        # Initialize OpenAI client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # Load NPC prompt template
        with open(os.path.join("prompts", "npc_prompt.txt"), "r") as f:
            self.prompt_template = f.read()

    async def generate_response(self, player_input, conversation_history, game_state):
        # Create a system prompt with NPC information
        npc_prompt = self.prompt_template.format(
            npc_name=self.static_traits["name"],
            npc_faction=self.static_traits["faction"],
            npc_personality=self.static_traits["personality"],
            npc_appearance=self.static_traits["appearance"],
            player_name=game_state.player.name,
            player_relationship=json.dumps(self.player_relationship, indent=2),
            npc_knowledge=json.dumps(self.knowledge, indent=2),
            memory_summary="\n".join(self.memory) if self.memory else "No prior interactions."
        )

        # Prepare the messages
        messages = [{"role": "system", "content": npc_prompt}]

        # Add conversation history
        messages.extend(conversation_history)

        # Add the latest user input if not already in history
        if not conversation_history or conversation_history[-1]["role"] != "user":
            messages.append({"role": "user", "content": player_input})

        # Generate response
        response = self.client.chat.completions.create(
            model="anthropic/claude-3-haiku",  # Using a smaller model for faster responses
            messages=messages,
        )

        return response.choices[0].message.content

    async def get_greeting(self, game_state):
        prompt = f"""
You are {self.static_traits['name']}, a {self.static_traits['faction']} stalker in the Zone.
Your personality: {self.static_traits['personality']}

The player ({game_state.player.name}) has just approached you to talk.
Generate a brief, in-character greeting that reflects your personality and relationship with the player.

Relationship status: {json.dumps(self.player_relationship, indent=2)}
Previous interactions: {self.memory if self.memory else "This is your first meeting."}

Your greeting:
"""

        response = self.client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    async def update_memory(self, conversation_history, game_state):
        if not conversation_history:
            return

        full_conversation = ""
        for msg in conversation_history:
            role = "Player" if msg["role"] == "user" else self.static_traits["name"]
            full_conversation += f"{role}: {msg['content']}\n\n"

        # Get memory summary
        new_memory = await summarize_conversation(full_conversation, self, game_state)

        # Update relationship values based on conversation sentiment
        # This is a simplified approach - in a real implementation, you'd want more nuanced analysis
        if "positive" in new_memory.lower():
            self.player_relationship["trust_level"] = min(10, self.player_relationship["trust_level"] + 1)
            self.player_relationship["friendship_level"] = min(10, self.player_relationship["friendship_level"] + 1)
        elif "negative" in new_memory.lower():
            self.player_relationship["trust_level"] = max(1, self.player_relationship["trust_level"] - 1)
            self.player_relationship["friendship_level"] = max(1, self.player_relationship["friendship_level"] - 1)

        # Update last interaction time
        self.player_relationship["last_interaction_time"] = game_state.current_time

        # Add to memory list
        self.memory.append(new_memory)

        # Keep only the last 5 memories
        if len(self.memory) > 5:
            self.memory = self.memory[-5:]

        # Add to key interactions if significant
        if "important information" in new_memory.lower() or "significant" in new_memory.lower():
            self.player_relationship["key_interactions"].append({
                "day": game_state.current_time["day"],
                "summary": new_memory
            })
