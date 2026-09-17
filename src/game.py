"""Main Pyxel game application wrapper."""

import os
import pyxel
from src.fsm import GameFSM


class ClubBudgetGame:
    SCREEN_WIDTH = 256
    SCREEN_HEIGHT = 192

    def __init__(self):
        # Resolve data paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scenarios_path = os.path.join(base_dir, "data", "scenarios.json")
        events_path = os.path.join(base_dir, "data", "events.json")

        pyxel.init(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            title="Club Budget: The Game (8-Bit Math Sim)",
            fps=30,
            display_scale=3,
        )

        self.fsm = GameFSM(scenarios_path, events_path)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.fsm.update()

    def draw(self):
        self.fsm.draw()
