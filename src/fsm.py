"""Finite State Machine controller and game screen implementations."""

import pyxel
from typing import Optional, List
from src.model import ClubState, ScenarioManager, Scenario, Choice, MathChallenge, GameEvent
from src.audio import SoundManager
from src.ui import (
    draw_hud,
    draw_box,
    draw_vignette_stage,
    draw_word_wrapped,
    COL_NAVY,
    COL_DARK_GRAY,
    COL_LIGHT_GRAY,
    COL_WHITE,
    COL_YELLOW,
    COL_GREEN,
    COL_DARK_GREEN,
    COL_CYAN,
    COL_RED,
    COL_ORANGE,
    COL_BROWN,
    COL_PURPLE,
    COL_BLACK,
    COL_PINK,
    COL_PEACH,
)


class StateEnum:
    TITLE = "TITLE"
    SETUP = "SETUP"
    WEEK_START = "WEEK_START"
    SCENARIO = "SCENARIO"
    MATH_CHALLENGE = "MATH_CHALLENGE"
    WEEK_SUMMARY = "WEEK_SUMMARY"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"


class GameFSM:
    def __init__(self, scenarios_path: str, events_path: str):
        self.scenarios_path = scenarios_path
        self.events_path = events_path
        self.scenario_mgr = ScenarioManager(scenarios_path, events_path)
        self.audio = SoundManager()

        # State Variables
        self.current_state = StateEnum.TITLE
        self.state_timer = 0
        self.flash_timer = 0

        # Setup Form Fields
        self.setup_fields = ["club_name", "budget", "students", "weeks"]
        self.setup_cursor = 0
        self.setup_name = "Mathletes Club"
        self.setup_budget = 300.0
        self.setup_students = 16
        self.setup_weeks = 12

        # Active Session State
        self.state: Optional[ClubState] = None
        self.current_scenario: Optional[Scenario] = None
        self.current_event: Optional[GameEvent] = None
        self.scenario_cursor = 0

        # Math Challenge State
        self.active_choice: Optional[Choice] = None
        self.math_cursor = 0
        self.math_answered = False
        self.math_correct = False
        self.math_feedback_timer = 0

        # Summary State
        self.summary_text = ""
        self.last_net_cash = 0.0

    def start_new_game(self):
        """Initializes a fresh club simulation with player parameters."""
        self.audio.stop_music()
        self.state = ClubState(
            club_name=self.setup_name,
            initial_budget=self.setup_budget,
            students_count=self.setup_students,
            total_weeks=self.setup_weeks,
            starting_happiness=72,
        )
        self.scenario_mgr.start_season(self.setup_weeks)
        self.current_state = StateEnum.WEEK_START
        self.state_timer = 0
        self.audio.play(SoundManager.SOUND_CONFIRM)

    def transition_to(self, new_state: str):
        self.current_state = new_state
        self.state_timer = 0

    # ------------------------------------------------------------------
    # UPDATE ROUTINES
    # ------------------------------------------------------------------

    def update(self):
        self.state_timer += 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Global Mute toggle
        if pyxel.btnp(pyxel.KEY_M):
            is_muted = self.audio.toggle_mute()
            if not is_muted and self.current_state in (StateEnum.TITLE, StateEnum.SETUP):
                self.audio.play_title_music()

        if self.current_state == StateEnum.TITLE:
            self._update_title()
        elif self.current_state == StateEnum.SETUP:
            self._update_setup()
        elif self.current_state == StateEnum.WEEK_START:
            self._update_week_start()
        elif self.current_state == StateEnum.SCENARIO:
            self._update_scenario()
        elif self.current_state == StateEnum.MATH_CHALLENGE:
            self._update_math_challenge()
        elif self.current_state == StateEnum.WEEK_SUMMARY:
            self._update_week_summary()
        elif self.current_state == StateEnum.GAME_OVER:
            self._update_game_over()
        elif self.current_state == StateEnum.VICTORY:
            self._update_victory()

    def _update_title(self):
        # Play title theme if not already running
        if not self.audio.music_playing and not self.audio.muted:
            self.audio.play_title_music()

        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self.audio.play(SoundManager.SOUND_CONFIRM)
            self.transition_to(StateEnum.SETUP)

    def _update_setup(self):
        # Navigation between fields
        if pyxel.btnp(pyxel.KEY_UP):
            self.setup_cursor = (self.setup_cursor - 1) % (len(self.setup_fields) + 1)
            self.audio.play(SoundManager.SOUND_SELECT)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.setup_cursor = (self.setup_cursor + 1) % (len(self.setup_fields) + 1)
            self.audio.play(SoundManager.SOUND_SELECT)

        # Field adjustments
        curr_field = self.setup_fields[self.setup_cursor] if self.setup_cursor < len(self.setup_fields) else "start"

        if curr_field == "club_name":
            # Cycle through cool club presets with LEFT/RIGHT
            presets = [
                "Mathletes Club",
                "Pi Pioneers",
                "Prime Time Math",
                "Algebra All-Stars",
                "Infinity Wizards",
                "Pythagoras Club",
            ]
            if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_RIGHT):
                cur_idx = presets.index(self.setup_name) if self.setup_name in presets else 0
                step = 1 if pyxel.btnp(pyxel.KEY_RIGHT) else -1
                self.setup_name = presets[(cur_idx + step) % len(presets)]
                self.audio.play(SoundManager.SOUND_SELECT)

        elif curr_field == "budget":
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.setup_budget = max(100.0, self.setup_budget - 25.0)
                self.audio.play(SoundManager.SOUND_SELECT)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.setup_budget = min(1000.0, self.setup_budget + 25.0)
                self.audio.play(SoundManager.SOUND_SELECT)

        elif curr_field == "students":
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.setup_students = max(4, self.setup_students - 2)
                self.audio.play(SoundManager.SOUND_SELECT)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.setup_students = min(36, self.setup_students + 2)
                self.audio.play(SoundManager.SOUND_SELECT)

        elif curr_field == "weeks":
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.setup_weeks = max(4, self.setup_weeks - 2)
                self.audio.play(SoundManager.SOUND_SELECT)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.setup_weeks = min(30, self.setup_weeks + 2)
                self.audio.play(SoundManager.SOUND_SELECT)

        elif curr_field == "start":
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                self.start_new_game()

    def _update_week_start(self):
        # Trigger unexpected event check once on week start
        if self.state_timer == 1:
            self.current_event = self.scenario_mgr.get_event_if_triggered(self.state.current_week, self.state)
            if self.current_event:
                self.audio.play(SoundManager.SOUND_ALARM)
                self.state.apply_event(self.current_event)
                self.flash_timer = 20

        # If event active, wait for player to press Enter/Space
        if self.current_event:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                # Check for immediate loss after event
                lost, reason = self.state.check_immediate_loss()
                if lost:
                    self.audio.play(SoundManager.SOUND_GAME_OVER)
                    self.transition_to(StateEnum.GAME_OVER)
                    return
                self.current_event = None
                self._load_current_scenario()
        else:
            self._load_current_scenario()

    def _load_current_scenario(self):
        self.current_scenario = self.scenario_mgr.get_scenario_for_week(self.state.current_week, self.state)
        self.scenario_cursor = 0
        self.transition_to(StateEnum.SCENARIO)

    def _update_scenario(self):
        if not self.current_scenario or not self.current_scenario.choices:
            return

        # Navigate choices
        if pyxel.btnp(pyxel.KEY_UP):
            self.scenario_cursor = (self.scenario_cursor - 1) % len(self.current_scenario.choices)
            self.audio.play(SoundManager.SOUND_SELECT)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.scenario_cursor = (self.scenario_cursor + 1) % len(self.current_scenario.choices)
            self.audio.play(SoundManager.SOUND_SELECT)

        # Confirm choice
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            choice = self.current_scenario.choices[self.scenario_cursor]
            self.active_choice = choice
            self.audio.play(SoundManager.SOUND_CONFIRM)

            if choice.math_challenge:
                self.math_cursor = 0
                self.math_answered = False
                self.math_correct = False
                self.math_feedback_timer = 0
                self.transition_to(StateEnum.MATH_CHALLENGE)
            else:
                # No math problem for this choice, apply immediately
                cash, eff = self.state.apply_choice(choice, math_correct=None)
                self.last_net_cash = cash
                self.summary_text = choice.reaction
                self.flash_timer = 20
                if cash > 0:
                    self.audio.play(SoundManager.SOUND_CASH)
                elif cash < 0:
                    self.audio.play(SoundManager.SOUND_ALARM)
                self.transition_to(StateEnum.WEEK_SUMMARY)

    def _update_math_challenge(self):
        if not self.active_choice or not self.active_choice.math_challenge:
            return

        challenge = self.active_choice.math_challenge

        if not self.math_answered:
            # Navigate multiple-choice answers
            if pyxel.btnp(pyxel.KEY_UP):
                self.math_cursor = (self.math_cursor - 1) % len(challenge.options)
                self.audio.play(SoundManager.SOUND_SELECT)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.math_cursor = (self.math_cursor + 1) % len(challenge.options)
                self.audio.play(SoundManager.SOUND_SELECT)

            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                selected_val = challenge.options[self.math_cursor]
                self.math_answered = True
                self.math_correct = abs(selected_val - challenge.answer) < 0.01

                if self.math_correct:
                    self.audio.play(SoundManager.SOUND_MATH_CORRECT)
                else:
                    self.audio.play(SoundManager.SOUND_ALARM)

                # Apply outcome to model
                cash, eff = self.state.apply_choice(self.active_choice, math_correct=self.math_correct)
                self.last_net_cash = cash
                self.summary_text = self.active_choice.reaction
                self.flash_timer = 20
        else:
            # Answer submitted: wait for player to press Enter/Space
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                self.transition_to(StateEnum.WEEK_SUMMARY)

    def _update_week_summary(self):
        # Check immediate loss first
        lost, reason = self.state.check_immediate_loss()
        if lost:
            self.audio.play(SoundManager.SOUND_GAME_OVER)
            self.transition_to(StateEnum.GAME_OVER)
            return

        # Player advances to next week
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self.state.advance_week()
            if self.state.is_season_finished():
                won, msg = self.state.check_victory()
                if won:
                    self.audio.play(SoundManager.SOUND_VICTORY)
                    self.transition_to(StateEnum.VICTORY)
                else:
                    self.audio.play(SoundManager.SOUND_GAME_OVER)
                    self.transition_to(StateEnum.GAME_OVER)
            else:
                self.transition_to(StateEnum.WEEK_START)

    def _update_game_over(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.transition_to(StateEnum.SETUP)
            self.audio.play_title_music()
        elif pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def _update_victory(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.transition_to(StateEnum.SETUP)
            self.audio.play_title_music()
        elif pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    # ------------------------------------------------------------------
    # DRAW ROUTINES
    # ------------------------------------------------------------------

    def draw(self):
        pyxel.cls(COL_BLACK)

        if self.current_state == StateEnum.TITLE:
            self._draw_title()
        elif self.current_state == StateEnum.SETUP:
            self._draw_setup()
        elif self.current_state == StateEnum.WEEK_START:
            self._draw_week_start()
        elif self.current_state == StateEnum.SCENARIO:
            self._draw_scenario()
        elif self.current_state == StateEnum.MATH_CHALLENGE:
            self._draw_math_challenge()
        elif self.current_state == StateEnum.WEEK_SUMMARY:
            self._draw_week_summary()
        elif self.current_state == StateEnum.GAME_OVER:
            self._draw_game_over()
        elif self.current_state == StateEnum.VICTORY:
            self._draw_victory()

    def _draw_title(self):
        # Decorative border
        pyxel.rectb(4, 4, 248, 184, COL_CYAN)
        pyxel.rectb(6, 6, 244, 180, COL_NAVY)

        # Music and control status indicator in corners
        audio_tag = "[M] Audio: OFF" if self.audio.muted else "[M] Audio: ON"
        audio_col = COL_RED if self.audio.muted else COL_GREEN
        pyxel.text(12, 12, audio_tag, audio_col)

        pyxel.text(176, 12, "Theme: 8-Bit", COL_CYAN)

        # Title shadow and text
        pyxel.text(48, 38, "==========================", COL_DARK_GRAY)
        pyxel.text(48, 48, "   CLUB BUDGET: THE GAME  ", COL_YELLOW)
        pyxel.text(48, 58, "==========================", COL_DARK_GRAY)

        pyxel.text(38, 76, "The 8-Bit Afterschool Math Club Sim", COL_LIGHT_GRAY)

        # Little chalkboard icon art
        pyxel.rect(98, 92, 60, 36, COL_DARK_GREEN)
        pyxel.rectb(98, 92, 60, 36, COL_BROWN)
        pyxel.text(104, 98, "$ Budget", COL_GREEN)
        pyxel.text(104, 108, "+ Math", COL_CYAN)
        pyxel.text(104, 118, "= Success!", COL_YELLOW)

        # Blinking prompt
        if (pyxel.frame_count // 20) % 2 == 0:
            pyxel.text(64, 145, "[ PRESS ENTER OR SPACE TO START ]", COL_WHITE)

        # Objective hint
        pyxel.text(26, 168, "Keep Student, Coach, & Parent happiness >= 80%!", COL_CYAN)
        pyxel.text(40, 178, "Avoid immediate loss trigger: Morale < 40%", COL_RED)

    def _draw_setup(self):
        draw_box(16, 12, 224, 168, bg_col=COL_NAVY, border_col=COL_CYAN)

        pyxel.text(68, 20, "--- CLUB REGISTRATION ---", COL_YELLOW)
        pyxel.text(24, 34, "Customize your school math club parameters:", COL_LIGHT_GRAY)

        items = [
            ("Club Name:", f"< {self.setup_name} >"),
            ("Season Budget:", f"< ${self.setup_budget:.2f} > (Use Left/Right)"),
            ("Active Students:", f"< {self.setup_students} Kids > (Use Left/Right)"),
            ("School Weeks:", f"< {self.setup_weeks} Weeks > (Use Left/Right)"),
        ]

        y = 52
        for idx, (label, val) in enumerate(items):
            is_active = (self.setup_cursor == idx)
            prefix = "> " if is_active else "  "
            col = COL_YELLOW if is_active else COL_WHITE
            pyxel.text(26, y, f"{prefix}{label}", col)
            pyxel.text(106, y, val, COL_CYAN if is_active else COL_LIGHT_GRAY)
            y += 20

        # Start button
        is_start = (self.setup_cursor == len(items))
        s_col = COL_GREEN if is_start else COL_DARK_GRAY
        pyxel.rect(78, 140, 100, 16, COL_BLACK)
        pyxel.rectb(78, 140, 100, 16, s_col)
        prefix = ">> " if is_start else "   "
        pyxel.text(82, 145, f"{prefix}[ START SIMULATION ]", s_col)

        pyxel.text(34, 165, "[UP/DOWN] Select Field   [LEFT/RIGHT] Adjust", COL_LIGHT_GRAY)

    def _draw_week_start(self):
        draw_hud(self.state, self.flash_timer)
        draw_vignette_stage("Coach", self.state.happiness)

        if self.current_event:
            # Unexpected event alert box
            draw_box(16, 98, 224, 88, bg_col=COL_PURPLE, border_col=COL_RED)
            pyxel.text(24, 104, "! UNEXPECTED EVENT ALERT !", COL_RED)
            pyxel.text(24, 114, self.current_event.title, COL_YELLOW)

            next_y = draw_word_wrapped(24, 126, self.current_event.description, max_chars_per_line=48, col=COL_WHITE)

            # Impact
            cost_str = f"Treasury Impact: -${self.current_event.cost:.2f}" if self.current_event.cost >= 0 else f"Grant Received: +${-self.current_event.cost:.2f}"
            pyxel.text(24, next_y + 4, cost_str, COL_ORANGE if self.current_event.cost >= 0 else COL_GREEN)

            pyxel.text(60, 172, "[ PRESS ENTER TO CONTINUE ]", COL_WHITE)
        else:
            draw_box(16, 98, 224, 88, bg_col=COL_NAVY, border_col=COL_WHITE)
            pyxel.text(24, 110, f"Welcome to Week {self.state.current_week} of {self.state.total_weeks}!", COL_YELLOW)
            pyxel.text(24, 125, "Planning weekly activities and math drills...", COL_WHITE)
            pyxel.text(60, 165, "[ PRESS ENTER TO PLAN ]", COL_CYAN)

    def _draw_scenario(self):
        draw_hud(self.state, self.flash_timer)
        speaker = self.current_scenario.speaker if self.current_scenario else "Coach"
        draw_vignette_stage(speaker, self.state.happiness)

        # Dialog and choices box
        draw_box(8, 96, 240, 92, bg_col=COL_NAVY, border_col=COL_WHITE)

        if not self.current_scenario:
            return

        # Speaker tag & scenario title
        pyxel.text(14, 100, f"[{speaker.upper()}]:", COL_YELLOW)
        pyxel.text(54, 100, self.current_scenario.title[:38], COL_WHITE)

        # Scenario description
        next_y = draw_word_wrapped(14, 110, self.current_scenario.description, max_chars_per_line=54, col=COL_LIGHT_GRAY, line_height=7)

        # Divider line
        choice_start_y = max(next_y + 2, 124)
        pyxel.line(12, choice_start_y - 2, 244, choice_start_y - 2, COL_DARK_GRAY)

        # Choices list
        cy = choice_start_y
        for idx, choice in enumerate(self.current_scenario.choices):
            is_active = (idx == self.scenario_cursor)
            col = COL_YELLOW if is_active else COL_WHITE
            prefix = "> " if is_active else "  "

            pyxel.text(14, cy, f"{prefix}{choice.text}", col)
            cy += 9

        # Footer hints
        pyxel.text(14, 180, "[UP/DOWN] Options   [ENTER] Select", COL_CYAN)

    def _draw_math_challenge(self):
        draw_hud(self.state, self.flash_timer)
        draw_vignette_stage("Student", self.state.happiness)

        # Math chalkboard overlay
        draw_box(10, 96, 236, 92, bg_col=COL_DARK_GREEN, border_col=COL_BROWN)

        if not self.active_choice or not self.active_choice.math_challenge:
            return

        challenge = self.active_choice.math_challenge

        # Header
        pyxel.text(16, 100, "=== 5TH-GRADE MATH CHALLENGE ===", COL_YELLOW)
        pyxel.text(180, 100, "[BONUS PTS]", COL_GREEN)

        # Word-wrapped problem
        ny = draw_word_wrapped(16, 110, challenge.prompt, max_chars_per_line=50, col=COL_WHITE, line_height=7)

        # Answers layout
        opts_y = max(ny + 4, 128)
        letters = ["A", "B", "C", "D"]

        for idx, opt_val in enumerate(challenge.options):
            is_hover = (idx == self.math_cursor)
            opt_x = 20 if idx % 2 == 0 else 130
            opt_row_y = opts_y + (idx // 2) * 12

            border_c = COL_YELLOW if is_hover else COL_DARK_GRAY
            text_c = COL_YELLOW if is_hover else COL_WHITE

            pyxel.rectb(opt_x, opt_row_y, 96, 10, border_c)
            tag = f"[{letters[idx]}]"
            val_str = f"{challenge.unit}{opt_val:.2f}" if challenge.unit == "$" else f"{opt_val}"
            prefix = "> " if is_hover else "  "
            pyxel.text(opt_x + 4, opt_row_y + 2, f"{prefix}{tag} {val_str}", text_c)

        # Feedback banner if answered
        if self.math_answered:
            banner_col = COL_GREEN if self.math_correct else COL_RED
            msg = "CORRECT! +Happiness bonus earned!" if self.math_correct else f"MISCALCULATION! Correct: ${challenge.answer:.2f}"
            pyxel.rect(14, 160, 228, 14, banner_col)
            pyxel.text(20, 164, msg, COL_WHITE)
            pyxel.text(64, 178, "[ PRESS ENTER TO CONTINUE ]", COL_WHITE)
        else:
            pyxel.text(16, 178, "[UP/DOWN] Pick Answer   [ENTER] Submit", COL_CYAN)

    def _draw_week_summary(self):
        draw_hud(self.state, self.flash_timer)
        draw_vignette_stage("Coach", self.state.happiness)

        draw_box(10, 96, 236, 92, bg_col=COL_NAVY, border_col=COL_WHITE)
        pyxel.text(16, 100, f"--- WEEK {self.state.current_week} RESULTS & OUTCOMES ---", COL_YELLOW)

        # Reaction text
        ny = draw_word_wrapped(16, 112, self.summary_text, max_chars_per_line=50, col=COL_WHITE, line_height=7)

        # Ledger changes
        delta_y = max(ny + 6, 134)
        pyxel.line(14, delta_y - 3, 242, delta_y - 3, COL_DARK_GRAY)

        cash_color = COL_GREEN if self.last_net_cash > 0 else (COL_ORANGE if self.last_net_cash < 0 else COL_CYAN)
        cash_str = f"Treasury Delta: ${self.last_net_cash:+.2f}"
        pyxel.text(16, delta_y, cash_str, cash_color)

        eff = self.state.last_effects_delta
        s_str = f"Student: {eff.get('students', 0):+d}%"
        c_str = f"Coach: {eff.get('coaches', 0):+d}%"
        p_str = f"Parent: {eff.get('parents', 0):+d}%"
        pyxel.text(16, delta_y + 10, f"Morale: {s_str}   {c_str}   {p_str}", COL_LIGHT_GRAY)

        # Next prompt
        weeks_left = self.state.total_weeks - self.state.current_week
        if weeks_left > 0:
            pyxel.text(54, 176, f"[ PRESS ENTER FOR WEEK {self.state.current_week + 1} ]", COL_GREEN)
        else:
            pyxel.text(54, 176, "[ PRESS ENTER FOR FINAL SEASON RESULTS ]", COL_YELLOW)

    def _draw_game_over(self):
        draw_hud(self.state, self.flash_timer)

        draw_box(16, 40, 224, 140, bg_col=COL_BLACK, border_col=COL_RED)
        pyxel.text(80, 48, "!!! SEASON DISASTER !!!", COL_RED)
        pyxel.text(82, 58, "=== GAME OVER ===", COL_RED)

        pyxel.line(24, 70, 232, 70, COL_DARK_GRAY)

        # Reason for dismissal
        reason = self.state.loss_reason or "The club failed to maintain minimum morale."
        draw_word_wrapped(24, 76, reason, max_chars_per_line=46, col=COL_YELLOW, line_height=8)

        # Stats summary
        pyxel.text(24, 114, f"Final Club Balance: ${self.state.budget:.2f}", COL_WHITE)
        pyxel.text(24, 124, f"Weeks Completed: {self.state.current_week - 1} of {self.state.total_weeks}", COL_WHITE)
        pyxel.text(24, 134, f"Student: {int(self.state.happiness['students'])}%  Coach: {int(self.state.happiness['coaches'])}%  Parent: {int(self.state.happiness['parents'])}%", COL_LIGHT_GRAY)

        # Rules reminder
        pyxel.text(24, 150, "Rule: Keep all scores >= 40% to survive!", COL_ORANGE)

        pyxel.text(48, 168, "[ R ] Play Again      [ Q ] Quit", COL_CYAN)

    def _draw_victory(self):
        draw_hud(self.state, self.flash_timer)

        draw_box(16, 40, 224, 140, bg_col=COL_NAVY, border_col=COL_YELLOW)
        pyxel.text(64, 48, "*** GOLD RIBBON SEASON! ***", COL_YELLOW)
        pyxel.text(78, 58, "=== CHAMPIONS! ===", COL_GREEN)

        # Confetti particles based on frame count
        for i in range(12):
            cx = (i * 21 + pyxel.frame_count * 2) % 240 + 8
            cy = (i * 17 + pyxel.frame_count) % 30 + 40
            c_col = [COL_YELLOW, COL_CYAN, COL_PINK, COL_GREEN][i % 4]
            pyxel.pset(cx, cy, c_col)

        pyxel.line(24, 70, 232, 70, COL_DARK_GRAY)

        # Accolades
        msg = f"Congratulations! {self.state.club_name} finished all {self.state.total_weeks} weeks with flying colors!"
        draw_word_wrapped(24, 76, msg, max_chars_per_line=46, col=COL_WHITE, line_height=8)

        pyxel.text(24, 106, f"Treasury Surplus: ${self.state.budget:.2f}", COL_GREEN)
        pyxel.text(24, 118, f"Student Happiness: {int(self.state.happiness['students'])}% (Goal >= 80%)", COL_GREEN)
        pyxel.text(24, 128, f"Coach Happiness:   {int(self.state.happiness['coaches'])}% (Goal >= 80%)", COL_GREEN)
        pyxel.text(24, 138, f"Parent Happiness:  {int(self.state.happiness['parents'])}% (Goal >= 80%)", COL_GREEN)

        pyxel.text(48, 166, "[ R ] Start New Season    [ Q ] Quit", COL_CYAN)
