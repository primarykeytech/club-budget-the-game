"""Unit tests for the Club Budget simulation engine."""

import unittest
import os
from src.model import ClubState, ScenarioManager, Choice, MathChallenge, GameEvent


class TestClubModel(unittest.TestCase):
    def setUp(self):
        self.state = ClubState(
            club_name="Alpha Math Club",
            initial_budget=250.0,
            students_count=16,
            total_weeks=8,
            starting_happiness=75,
        )

    def test_initial_state(self):
        self.assertEqual(self.state.club_name, "Alpha Math Club")
        self.assertEqual(self.state.budget, 250.0)
        self.assertEqual(self.state.students_count, 16)
        self.assertEqual(self.state.total_weeks, 8)
        self.assertEqual(self.state.current_week, 1)
        self.assertEqual(self.state.happiness["students"], 75.0)
        self.assertEqual(self.state.happiness["coaches"], 75.0)
        self.assertEqual(self.state.happiness["parents"], 75.0)

    def test_formula_evaluation(self):
        # 16 students * $0.25 = $4.00
        val = self.state.evaluate_formula("0.25 * students")
        self.assertEqual(val, 4.00)

        # 16 students * $1.75 = $28.00
        val2 = self.state.evaluate_formula("1.75 * students")
        self.assertEqual(val2, 28.00)

        # Bake sale: (3.50 * 32) - 15 = 112 - 15 = 97.00
        val3 = self.state.evaluate_formula("(3.50 * students * 2) - 15.00")
        self.assertEqual(val3, 97.00)

    def test_apply_choice_deduction(self):
        choice = Choice(
            id="test_pencils",
            text="Buy Pencils",
            cost=20.0,
            revenue=0.0,
            effects={"students": 5, "coaches": 2, "parents": -1},
            reaction="Pencils bought!",
        )
        net_cash, eff = self.state.apply_choice(choice)
        self.assertEqual(net_cash, -20.0)
        self.assertEqual(self.state.budget, 230.0)
        self.assertEqual(self.state.happiness["students"], 80.0)
        self.assertEqual(self.state.happiness["coaches"], 77.0)
        self.assertEqual(self.state.happiness["parents"], 74.0)

    def test_math_challenge_bonus(self):
        challenge = MathChallenge(
            challenge_type="decimal_mult",
            prompt="16 * 0.25",
            answer=4.0,
            bonus_happiness=6,
            penalty_cost=2.0,
        )
        choice = Choice(
            id="test_math",
            text="Math Option",
            cost=4.0,
            revenue=0.0,
            effects={"students": 0, "coaches": 0, "parents": 0},
            reaction="Good job",
            math_challenge=challenge,
        )
        # Correct answer
        self.state.apply_choice(choice, math_correct=True)
        self.assertGreater(self.state.happiness["coaches"], 75.0)

    def test_math_challenge_penalty(self):
        challenge = MathChallenge(
            challenge_type="decimal_mult",
            prompt="16 * 0.25",
            answer=4.0,
            bonus_happiness=6,
            penalty_cost=5.0,
        )
        choice = Choice(
            id="test_math",
            text="Math Option",
            cost=4.0,
            revenue=0.0,
            effects={"students": 0, "coaches": 0, "parents": 0},
            reaction="Oops",
            math_challenge=challenge,
        )
        # Incorrect answer incurs penalty_cost of $5.00 extra
        initial_budget = self.state.budget
        self.state.apply_choice(choice, math_correct=False)
        self.assertEqual(self.state.budget, initial_budget - 4.0 - 5.0)

    def test_immediate_loss_low_happiness(self):
        # Drop student happiness below 40
        self.state.happiness["students"] = 38.0
        lost, reason = self.state.check_immediate_loss()
        self.assertTrue(lost)
        self.assertIn("Student Mutiny", reason)

        # Coach drop
        self.state.happiness["students"] = 70.0
        self.state.happiness["coaches"] = 35.0
        lost, reason = self.state.check_immediate_loss()
        self.assertTrue(lost)
        self.assertIn("Coach Resigned", reason)

        # Parent drop
        self.state.happiness["coaches"] = 70.0
        self.state.happiness["parents"] = 39.5
        lost, reason = self.state.check_immediate_loss()
        self.assertTrue(lost)
        self.assertIn("Parent Boycott", reason)

    def test_immediate_loss_bankruptcy(self):
        self.state.budget = -5.0
        lost, reason = self.state.check_immediate_loss()
        self.assertTrue(lost)
        self.assertIn("Bankruptcy", reason)

    def test_victory_condition(self):
        self.state.current_week = 9  # Season passed total_weeks (8)
        self.state.happiness["students"] = 82.0
        self.state.happiness["coaches"] = 85.0
        self.state.happiness["parents"] = 80.0
        won, msg = self.state.check_victory()
        self.assertTrue(won)
        self.assertIn("Gold Ribbon Season", msg)

    def test_end_season_missed_target(self):
        self.state.current_week = 9
        # One score is below 80, but above 40
        self.state.happiness["students"] = 85.0
        self.state.happiness["coaches"] = 78.0
        self.state.happiness["parents"] = 85.0
        won, msg = self.state.check_victory()
        self.assertFalse(won)
        self.assertIn("Coaches", msg)

    def test_scenario_manager_loading(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        scen_path = os.path.join(data_dir, "scenarios.json")
        evt_path = os.path.join(data_dir, "events.json")

        sm = ScenarioManager(scen_path, evt_path)
        self.assertGreater(len(sm.scenarios_raw), 0)
        self.assertGreater(len(sm.events_raw), 0)

        # Get scenario for week 1
        scen = sm.get_scenario_for_week(1, self.state)
        self.assertIsNotNone(scen.title)
        self.assertGreater(len(scen.choices), 1)

        # Verify math options generation
        for c in scen.choices:
            if c.math_challenge:
                self.assertEqual(len(c.math_challenge.options), 4)
                self.assertIn(c.math_challenge.answer, c.math_challenge.options)


if __name__ == "__main__":
    unittest.main()
