import os
from openai import OpenAI


async def summarize_conversation(conversation_text, npc, game_state):
    # Load memory prompt template
    with open(os.path.join("prompts", "memory_prompt.txt"), "r") as f:
        memory_prompt = f.read()

    # Format the prompt
    prompt = memory_prompt.format(
        npc_name=npc.static_traits["name"],
        player_name=game_state.player.name,
        conversation=conversation_text
    )

    # Initialize OpenAI client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    # Generate summary
    response = client.chat.completions.create(
        model="anthropic/claude-3-haiku",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
