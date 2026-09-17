"""Simulation model and state management for Club Budget: The Game."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import json
import os
import random


@dataclass
class MathChallenge:
    challenge_type: str
    prompt: str
    answer: float
    unit: str = "$"
    options: List[float] = field(default_factory=list)
    bonus_happiness: int = 5
    penalty_cost: float = 0.0


@dataclass
class Choice:
    id: str
    text: str
    cost: float
    revenue: float
    effects: Dict[str, int]
    reaction: str
    math_challenge: Optional[MathChallenge] = None


@dataclass
class Scenario:
    id: str
    title: str
    speaker: str
    description: str
    choices: List[Choice]


@dataclass
class GameEvent:
    id: str
    title: str
    description: str
    cost: float
    effects: Dict[str, int]


class ClubState:
    """Manages club finances, stakeholder morale, and simulation progress."""

    def __init__(
        self,
        club_name: str = "Mathletes Club",
        initial_budget: float = 300.0,
        students_count: int = 16,
        total_weeks: int = 12,
        starting_happiness: int = 72,
    ):
        self.club_name = club_name.strip() or "Mathletes Club"
        self.initial_budget = float(initial_budget)
        self.budget = float(initial_budget)
        self.students_count = max(1, int(students_count))
        self.total_weeks = max(1, int(total_weeks))
        self.current_week = 1

        # Stakeholder happiness levels (0 - 100)
        self.happiness: Dict[str, float] = {
            "students": float(starting_happiness),
            "coaches": float(starting_happiness),
            "parents": float(starting_happiness),
        }

        self.history: List[str] = []
        self.last_transaction_delta: float = 0.0
        self.last_effects_delta: Dict[str, int] = {"students": 0, "coaches": 0, "parents": 0}
        self.loss_reason: Optional[str] = None

    def evaluate_formula(self, formula_str: str) -> float:
        """Safely evaluates numeric formulas with club variables."""
        if not formula_str or str(formula_str).strip() == "0":
            return 0.0
        try:
            # Clean and provide safe context
            context = {
                "students": self.students_count,
                "students_x2": self.students_count * 2,
                "half_students": self.students_count // 2,
            }
            # Restrict built-ins for security
            val = eval(str(formula_str), {"__builtins__": None}, context)
            return round(float(val), 2)
        except Exception:
            return 0.0

    def format_text(self, text: str) -> str:
        """Replaces template variables in prompts and descriptions."""
        return text.format(
            club=self.club_name,
            students=self.students_count,
            students_x2=self.students_count * 2,
            half_students=self.students_count // 2,
            budget=f"{self.budget:.2f}",
            week=self.current_week,
            total_weeks=self.total_weeks,
        )

    def apply_choice(self, choice: Choice, math_correct: Optional[bool] = None) -> Tuple[float, Dict[str, int]]:
        """Applies financial and happiness outcomes of a player's decision."""
        net_cash = choice.revenue - choice.cost

        # Math bonus or penalty
        eff = dict(choice.effects)
        if choice.math_challenge and math_correct is not None:
            if math_correct:
                bonus = choice.math_challenge.bonus_happiness
                eff["students"] = eff.get("students", 0) + bonus // 2
                eff["coaches"] = eff.get("coaches", 0) + bonus
                eff["parents"] = eff.get("parents", 0) + bonus // 2
            else:
                net_cash -= choice.math_challenge.penalty_cost
                eff["students"] = eff.get("students", 0) - 2
                eff["coaches"] = eff.get("coaches", 0) - 3

        # Apply financial change
        self.budget = round(self.budget + net_cash, 2)
        self.last_transaction_delta = net_cash

        # Apply happiness changes (clamped 0 to 100)
        for key in ["students", "coaches", "parents"]:
            delta = eff.get(key, 0)
            self.happiness[key] = max(0.0, min(100.0, self.happiness[key] + delta))

        self.last_effects_delta = eff
        self.history.append(f"Wk {self.current_week}: Chose '{choice.text}' (Net ${net_cash:+.2f})")
        return net_cash, eff

    def apply_event(self, event: GameEvent) -> Tuple[float, Dict[str, int]]:
        """Applies an unexpected event's financial and happiness impact."""
        # Event cost reduces budget
        net_cash = -round(event.cost, 2)
        self.budget = round(self.budget + net_cash, 2)
        self.last_transaction_delta = net_cash

        eff = dict(event.effects)
        for key in ["students", "coaches", "parents"]:
            delta = eff.get(key, 0)
            self.happiness[key] = max(0.0, min(100.0, self.happiness[key] + delta))

        self.last_effects_delta = eff
        self.history.append(f"Wk {self.current_week} Event: {event.title} (${net_cash:+.2f})")
        return net_cash, eff

    def check_immediate_loss(self) -> Tuple[bool, Optional[str]]:
        """Checks if an immediate loss condition has been triggered.
        Triggers if any stakeholder happiness < 40 or budget < 0.
        """
        if self.budget < 0:
            self.loss_reason = f"Bankruptcy! The club ran out of money (Balance: ${self.budget:.2f})."
            return True, self.loss_reason

        for role, score in self.happiness.items():
            if score < 40.0:
                labels = {
                    "students": "Student Mutiny! Students stopped attending (Happiness < 40%).",
                    "coaches": "Coach Resigned! The coach was overwhelmed and burnt out (Happiness < 40%).",
                    "parents": "Parent Boycott! Parents pulled their children from the club (Happiness < 40%).",
                }
                self.loss_reason = labels.get(role, f"{role.capitalize()} satisfaction collapsed!")
                return True, self.loss_reason

        return False, None

    def is_season_finished(self) -> bool:
        return self.current_week > self.total_weeks

    def check_victory(self) -> Tuple[bool, str]:
        """Evaluates end-of-season status."""
        if not self.is_season_finished():
            return False, "Season in progress."

        lost, reason = self.check_immediate_loss()
        if lost:
            return False, reason or "Season failed."

        # All happiness scores must be >= 80
        all_above_80 = all(score >= 80.0 for score in self.happiness.values())
        if all_above_80:
            return True, "Gold Ribbon Season! Students, Coaches, and Parents are thrilled (all >= 80%)!"

        # Reached the end with positive balance but missed the >=80 standard
        low_stakeholders = [role.capitalize() for role, score in self.happiness.items() if score < 80.0]
        return False, f"Season Ended, but failed to reach 80% happiness for: {', '.join(low_stakeholders)}."

    def advance_week(self):
        """Advances simulation to next week."""
        self.current_week += 1


class ScenarioManager:
    """Loads and compiles dynamic scenarios and events from data files."""

    def __init__(self, scenarios_path: str, events_path: str):
        self.scenarios_path = scenarios_path
        self.events_path = events_path
        self.scenarios_raw: List[Dict[str, Any]] = []
        self.events_raw: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.scenarios_path):
            with open(self.scenarios_path, "r", encoding="utf-8") as f:
                self.scenarios_raw = json.load(f)
        if os.path.exists(self.events_path):
            with open(self.events_path, "r", encoding="utf-8") as f:
                self.events_raw = json.load(f)

    def get_scenario_for_week(self, week_num: int, state: ClubState) -> Scenario:
        """Returns a compiled scenario tailored to current club state."""
        # Pick scenario cyclically or shuffled
        idx = (week_num - 1) % len(self.scenarios_raw) if self.scenarios_raw else 0
        raw = self.scenarios_raw[idx] if self.scenarios_raw else {
            "id": "generic",
            "title": "Weekly Planning",
            "speaker": "Coach",
            "description": "How should we organize this week's activities?",
            "choices": []
        }

        choices: List[Choice] = []
        for raw_c in raw.get("choices", []):
            cost = state.evaluate_formula(raw_c.get("cost_formula", "0"))
            rev = state.evaluate_formula(raw_c.get("revenue_formula", "0"))

            math_challenge = None
            if raw_c.get("math_challenge"):
                mc_raw = raw_c["math_challenge"]
                ans = state.evaluate_formula(mc_raw.get("answer_formula", "0"))
                prompt = state.format_text(mc_raw.get("prompt", ""))

                # Generate 4 distinct multiple choice options
                options = self._generate_math_options(ans)
                math_challenge = MathChallenge(
                    challenge_type=mc_raw.get("type", "calc"),
                    prompt=prompt,
                    answer=ans,
                    unit=mc_raw.get("unit", "$"),
                    options=options,
                    bonus_happiness=mc_raw.get("bonus_happiness", 5),
                    penalty_cost=mc_raw.get("penalty_cost", 0.0),
                )

            choices.append(
                Choice(
                    id=raw_c.get("id", "opt"),
                    text=state.format_text(raw_c.get("text", "")),
                    cost=cost,
                    revenue=rev,
                    effects=raw_c.get("effects", {}),
                    reaction=state.format_text(raw_c.get("reaction", "")),
                    math_challenge=math_challenge,
                )
            )

        return Scenario(
            id=raw.get("id", "scen"),
            title=state.format_text(raw.get("title", "")),
            speaker=raw.get("speaker", "Coach"),
            description=state.format_text(raw.get("description", "")),
            choices=choices,
        )

    def get_event_if_triggered(self, week_num: int, state: ClubState) -> Optional[GameEvent]:
        """Triggers unexpected event every 3-4 weeks (or if condition met)."""
        # Periodic unexpected event on weeks 3, 6, 9, 12, etc.
        if week_num > 1 and week_num % 3 == 0 and self.events_raw:
            raw = random.choice(self.events_raw)
            cost = state.evaluate_formula(raw.get("cost_formula", str(raw.get("cost", 0))))
            return GameEvent(
                id=raw.get("id", "event"),
                title=state.format_text(raw.get("title", "")),
                description=state.format_text(raw.get("description", "")),
                cost=cost,
                effects=raw.get("effects", {}),
            )
        return None

    def _generate_math_options(self, correct_ans: float) -> List[float]:
        """Generates 4 plausible multiple-choice options including the correct answer."""
        opts = {correct_ans}
        # Common 5th grade distractors: off by small addition/subtraction, scale factor, or rounded
        deltas = [
            round(correct_ans + random.choice([2.0, 5.0, 10.0, 0.50, 1.50]), 2),
            round(max(0.0, correct_ans - random.choice([2.0, 4.0, 5.0, 0.50])), 2),
            round(correct_ans * random.choice([0.8, 1.2, 1.5]), 2),
            round(correct_ans + 10.0, 2),
        ]
        for d in deltas:
            if d != correct_ans and d >= 0:
                opts.add(d)
            if len(opts) >= 4:
                break

        while len(opts) < 4:
            fake = round(max(0.0, correct_ans + len(opts) * 3.5), 2)
            opts.add(fake)

        res = list(opts)
        random.shuffle(res)
        return res
