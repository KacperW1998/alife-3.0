import os
import shutil
from colorama import init, Fore, Back, Style
import textwrap

init()  # Initialize colorama


class UIManager:
    def __init__(self):
        self.terminal_size = shutil.get_terminal_size()
        # Reduce main width to ensure no overlap
        self.main_width = int(self.terminal_size.columns * 0.58) - 2
        self.sidebar_width = int(self.terminal_size.columns * 0.42) - 1

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_screen(self, game_text, current_npc, game_state, current_location):
        self.clear_screen()

        # Properly wrap text to main width
        wrapped_text = []
        for line in game_text.split('\n'):
            if line.strip():
                wrapped_text.extend(textwrap.wrap(line, width=self.main_width))
            else:
                wrapped_text.append("")  # Keep empty lines

        game_lines = [line.ljust(self.main_width) for line in wrapped_text]

        # Create sidebar content
        sidebar_lines = self._generate_sidebar(current_npc, game_state, current_location)

        # Add header
        print(
            f"{Fore.YELLOW}{'S.T.A.L.K.E.R: SHADOWS OF TRUTH'.center(self.main_width + self.sidebar_width + 2)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-' * (self.main_width + self.sidebar_width + 2)}{Style.RESET_ALL}")

        # Combine and display
        for i in range(max(len(game_lines), len(sidebar_lines))):
            game_part = game_lines[i] if i < len(game_lines) else " " * self.main_width
            sidebar_part = sidebar_lines[i] if i < len(sidebar_lines) else ""
            # Add a separator between main and sidebar
            print(f"{game_part}  {Fore.CYAN}{sidebar_part}{Style.RESET_ALL}")

    def _generate_sidebar(self, current_npc, game_state, current_location):
        sidebar_lines = []

        # Add section title
        sidebar_lines.append("=" * self.sidebar_width)
        sidebar_lines.append("STALKER STATUS".center(self.sidebar_width))
        sidebar_lines.append("=" * self.sidebar_width)

        # Show player status
        sidebar_lines.append(f"Name: {game_state.player.name}")
        sidebar_lines.append(f"Location: {current_location['name']}")
        sidebar_lines.append(f"Health: {game_state.player.health}%")
        sidebar_lines.append(f"Day: {game_state.current_time['day']}, {game_state.current_time['period']}")
        sidebar_lines.append("-" * self.sidebar_width)

        # Show discovered clues
        sidebar_lines.append("DISCOVERED CLUES:")
        for clue, discovered in game_state.main_plot['discovered_clues'].items():
            prefix = f"{Fore.GREEN}✓{Fore.CYAN} " if discovered else "□ "
            sidebar_lines.append(f"{prefix}{clue}")

        # Show NPC memory if in conversation
        if current_npc:
            sidebar_lines.append("=" * self.sidebar_width)
            sidebar_lines.append(f"NPC: {current_npc.static_traits['name']}".center(self.sidebar_width))
            sidebar_lines.append("=" * self.sidebar_width)
            sidebar_lines.append("RELATIONSHIP STATS:")

            # Color-code trust levels
            trust_color = Fore.RED
            if current_npc.player_relationship['trust_level'] >= 7:
                trust_color = Fore.GREEN
            elif current_npc.player_relationship['trust_level'] >= 4:
                trust_color = Fore.YELLOW

            sidebar_lines.append(f"Trust: {trust_color}{current_npc.player_relationship['trust_level']}/10{Fore.CYAN}")
            sidebar_lines.append(f"Friendship: {current_npc.player_relationship['friendship_level']}/10")

            # Show faction
            sidebar_lines.append(f"Faction: {current_npc.static_traits['faction']}")

            sidebar_lines.append("-" * self.sidebar_width)
            sidebar_lines.append("NPC MEMORY:")

            # Show the memories (most recent first)
            if not current_npc.memory:
                sidebar_lines.append("No previous interactions.")
            else:
                for memory in reversed(current_npc.memory):
                    # Wrap long memory lines to fit sidebar
                    wrapped_memory = textwrap.wrap(memory, width=self.sidebar_width - 2)
                    for i, line in enumerate(wrapped_memory):
                        if i == 0:  # First line gets the bullet point
                            sidebar_lines.append(f"• {line}")
                        else:  # Continuation lines get indented
                            sidebar_lines.append(f"  {line}")
                    sidebar_lines.append("")  # Add a blank line between memories

        return sidebar_lines
