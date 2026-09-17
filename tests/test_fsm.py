"""Headless tests for GameFSM transitions and update loops."""

import unittest
import os
import pyxel
from src.fsm import GameFSM, StateEnum
from src.model import ClubState


class TestGameFSM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize headless pyxel instance for tests
        try:
            pyxel.init(256, 192, headless=True)
        except Exception:
            pass

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scenarios_path = os.path.join(base_dir, "data", "scenarios.json")
        events_path = os.path.join(base_dir, "data", "events.json")
        self.fsm = GameFSM(scenarios_path, events_path)

    def test_initial_state_is_title(self):
        self.assertEqual(self.fsm.current_state, StateEnum.TITLE)

    def test_start_new_game(self):
        self.fsm.setup_name = "Pi Pioneers"
        self.fsm.setup_budget = 400.0
        self.fsm.setup_students = 20
        self.fsm.setup_weeks = 10

        self.fsm.start_new_game()
        self.assertEqual(self.fsm.current_state, StateEnum.WEEK_START)
        self.assertIsNotNone(self.fsm.state)
        self.assertEqual(self.fsm.state.club_name, "Pi Pioneers")
        self.assertEqual(self.fsm.state.budget, 400.0)
        self.assertEqual(self.fsm.state.students_count, 20)
        self.assertEqual(self.fsm.state.total_weeks, 10)

    def test_week_start_to_scenario(self):
        self.fsm.start_new_game()
        # Trigger update
        self.fsm._update_week_start()
        self.assertEqual(self.fsm.current_state, StateEnum.SCENARIO)
        self.assertIsNotNone(self.fsm.current_scenario)
        self.assertGreater(len(self.fsm.current_scenario.choices), 0)

    def test_math_challenge_transition(self):
        self.fsm.start_new_game()
        self.fsm._load_current_scenario()

        # Find a choice that has a math challenge
        math_choice_idx = None
        for idx, c in enumerate(self.fsm.current_scenario.choices):
            if c.math_challenge:
                math_choice_idx = idx
                break

        if math_choice_idx is not None:
            self.fsm.scenario_cursor = math_choice_idx
            choice = self.fsm.current_scenario.choices[math_choice_idx]
            self.fsm.active_choice = choice
            self.fsm.transition_to(StateEnum.MATH_CHALLENGE)
            self.assertEqual(self.fsm.current_state, StateEnum.MATH_CHALLENGE)
            self.assertFalse(self.fsm.math_answered)

    def test_draw_cycles_headless(self):
        # Ensure draw methods don't crash in various states
        self.fsm.draw()

        self.fsm.start_new_game()
        self.fsm.draw()

        self.fsm.transition_to(StateEnum.GAME_OVER)
        self.fsm.draw()

        self.fsm.transition_to(StateEnum.VICTORY)
        self.fsm.draw()


if __name__ == "__main__":
    unittest.main()
