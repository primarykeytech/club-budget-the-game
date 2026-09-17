"""Retro 8-bit UI rendering routines, HUD, happiness bars, and pixel art vignettes for Pyxel."""

import pyxel
from typing import List, Dict, Tuple


# Color Constants
COL_BLACK = 0
COL_NAVY = 1
COL_PURPLE = 2
COL_DARK_GREEN = 3
COL_BROWN = 4
COL_DARK_GRAY = 5
COL_LIGHT_GRAY = 6
COL_WHITE = 7
COL_RED = 8
COL_ORANGE = 9
COL_YELLOW = 10
COL_GREEN = 11
COL_CYAN = 12
COL_BLUE = 13
COL_PINK = 14
COL_PEACH = 15


def draw_box(x: int, y: int, w: int, h: int, bg_col: int = COL_NAVY, border_col: int = COL_WHITE):
    """Draws a retro double-bordered dialogue or UI frame."""
    pyxel.rect(x, y, w, h, bg_col)
    pyxel.rectb(x, y, w, h, border_col)
    pyxel.rectb(x + 2, y + 2, w - 4, h - 4, COL_DARK_GRAY)


def draw_happiness_bar(x: int, y: int, label: str, value: float, width: int = 72):
    """Draws a labeled health/happiness gauge with separate label/percentage line and bar line."""
    val_clamped = max(0.0, min(100.0, value))
    bw = width
    bh = 4

    # Threshold colors
    if val_clamped >= 80:
        bar_col = COL_GREEN
    elif val_clamped >= 50:
        bar_col = COL_YELLOW
    elif val_clamped >= 40:
        bar_col = COL_ORANGE
    else:
        # Flashing red when in the immediate-loss danger zone (<40)
        bar_col = COL_RED if (pyxel.frame_count // 6) % 2 == 0 else COL_WHITE

    # Line 1: Label and percentage (e.g. "STUDENT: 82%")
    pct_str = f"{int(val_clamped)}%"
    pyxel.text(x, y, f"{label}:", COL_LIGHT_GRAY)
    # Right-align percentage within the gauge width
    px = x + bw - len(pct_str) * 4
    pyxel.text(px, y, pct_str, bar_col)

    # Line 2: Progress bar frame and fill
    by = y + 7
    pyxel.rect(x, by, bw, bh, COL_BLACK)
    pyxel.rectb(x, by, bw, bh, COL_DARK_GRAY)

    fill_w = int((val_clamped / 100.0) * (bw - 2))
    if fill_w > 0:
        pyxel.rect(x + 1, by + 1, fill_w, bh - 2, bar_col)


def draw_hud(state, flash_timer: int = 0):
    """Renders the persistent top status dashboard with clean, non-overlapping rows."""
    # Header bar (Height 35px: y=0 to 35)
    pyxel.rect(0, 0, 256, 35, COL_NAVY)
    pyxel.line(0, 35, 256, 35, COL_DARK_GRAY)

    # Row 1 (y=3): Club name, Week counter, Budget balance
    club_tag = state.club_name[:16].upper()
    pyxel.text(8, 3, club_tag, COL_YELLOW)

    week_str = f"WEEK {state.current_week:02d}/{state.total_weeks:02d}"
    pyxel.text(104, 3, week_str, COL_WHITE)

    # Budget balance (flashes on recent transactions)
    money_col = COL_GREEN if state.budget >= 100 else (COL_YELLOW if state.budget >= 40 else COL_RED)
    if flash_timer > 0 and (pyxel.frame_count // 4) % 2 == 0:
        money_col = COL_WHITE

    budget_str = f"${state.budget:0.2f}"
    bx = 248 - len(budget_str) * 4
    pyxel.text(bx, 3, budget_str, money_col)

    # Rows 2 & 3 (y=11 for labels/pct, y=18 for bars):
    # 3 neatly spaced columns: x=8, x=92, x=176 (each width 72, with 12px margins)
    draw_happiness_bar(8, 11, "STUDENT", state.happiness["students"], width=72)
    draw_happiness_bar(92, 11, "COACH", state.happiness["coaches"], width=72)
    draw_happiness_bar(176, 11, "PARENT", state.happiness["parents"], width=72)

    # Row 4 (y=26): Burn rate and danger warnings on their own dedicated line
    min_score = min(state.happiness.values())
    if min_score < 45:
        if (pyxel.frame_count // 8) % 2 == 0:
            pyxel.text(8, 26, "! MORALE DANGER: SCORE <40% CAUSES IMMEDIATE LOSS !", COL_RED)
    elif state.budget < 30.0:
        if (pyxel.frame_count // 8) % 2 == 0:
            pyxel.text(8, 26, "! LOW BUDGET DANGER: DON'T GO BROKE !", COL_ORANGE)
    else:
        # Safe pace indicator
        weeks_left = max(1, state.total_weeks - state.current_week + 1)
        safe_allowance = state.budget / weeks_left
        pyxel.text(8, 26, f"Target Burn Rate: ~${safe_allowance:.2f}/wk", COL_CYAN)


def draw_word_wrapped(x: int, y: int, text: str, max_chars_per_line: int, col: int, line_height: int = 7) -> int:
    """Renders wrapped retro text and returns the next Y position."""
    words = text.split(" ")
    current_line = []
    current_len = 0
    curr_y = y

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) <= max_chars_per_line:
            current_line.append(word)
            current_len += len(word) + 1
        else:
            line_str = " ".join(current_line)
            pyxel.text(x, curr_y, line_str, col)
            curr_y += line_height
            current_line = [word]
            current_len = len(word)

    if current_line:
        line_str = " ".join(current_line)
        pyxel.text(x, curr_y, line_str, col)
        curr_y += line_height

    return curr_y


# ----------------------------------------------------------------------
# 8-bit Character & Vignette Pixel Art Drawers
# ----------------------------------------------------------------------

def draw_vignette_stage(speaker: str, happiness_dict: Dict[str, float], icon_type: str = "chalkboard"):
    """Draws the central 8-bit stage showing animated characters reacting to the scene."""
    stage_x, stage_y, stage_w, stage_h = 0, 36, 256, 58

    # Classroom chalkboard background
    pyxel.rect(stage_x, stage_y, stage_w, stage_h, COL_DARK_GREEN)
    pyxel.rectb(stage_x, stage_y, stage_w, stage_h, COL_BROWN)
    pyxel.rectb(stage_x + 1, stage_y + 1, stage_w - 2, stage_h - 2, COL_BROWN)

    # Chalk math symbols doodled along the top open area (no overlap with character tags)
    pyxel.text(8, 39, "pi=3.14", COL_LIGHT_GRAY)
    pyxel.text(86, 39, "A=1/2*b*h", COL_LIGHT_GRAY)
    pyxel.text(148, 39, "a^2+b^2=c^2", COL_LIGHT_GRAY)
    pyxel.text(214, 39, "E=mc^2", COL_LIGHT_GRAY)

    # Bobbing animation offset
    bob = (pyxel.frame_count // 16) % 2

    # Draw 3 Stakeholders across the room
    # Student at X=52
    draw_student_sprite(52, 44 + bob, happiness_dict.get("students", 70), is_speaking=(speaker.lower() == "student"))

    # Coach at X=114
    draw_coach_sprite(114, 43 + (1 - bob), happiness_dict.get("coaches", 70), is_speaking=(speaker.lower() == "coach"))

    # Parent at X=176
    draw_parent_sprite(176, 44 + bob, happiness_dict.get("parents", 70), is_speaking=(speaker.lower() == "parent"))


def draw_student_sprite(x: int, y: int, happiness: float, is_speaking: bool = False):
    """Draws an 8-bit student sprite."""
    # Speaking aura
    if is_speaking and (pyxel.frame_count // 6) % 2 == 0:
        pyxel.rectb(x - 3, y - 3, 26, 34, COL_YELLOW)

    # Hair / Baseball cap backwards
    pyxel.rect(x + 5, y, 10, 5, COL_RED)
    pyxel.rect(x + 2, y + 2, 4, 3, COL_RED)  # cap brim

    # Face
    pyxel.rect(x + 4, y + 5, 12, 10, COL_PEACH)

    # Eyes & Mouth based on happiness
    if happiness >= 80:
        # Happy eyes ^^
        pyxel.pset(x + 6, y + 8, COL_BLACK)
        pyxel.pset(x + 12, y + 8, COL_BLACK)
        # Smile
        pyxel.line(x + 7, y + 12, x + 11, y + 12, COL_RED)
        pyxel.pset(x + 6, y + 11, COL_RED)
        pyxel.pset(x + 12, y + 11, COL_RED)
    elif happiness >= 50:
        # Normal eyes
        pyxel.pset(x + 6, y + 8, COL_BLACK)
        pyxel.pset(x + 12, y + 8, COL_BLACK)
        pyxel.line(x + 8, y + 12, x + 11, y + 12, COL_BLACK)
    else:
        # Sad / crying eyes
        pyxel.line(x + 6, y + 8, x + 8, y + 8, COL_BLACK)
        pyxel.line(x + 11, y + 8, x + 13, y + 8, COL_BLACK)
        pyxel.line(x + 8, y + 13, x + 11, y + 13, COL_BLACK)
        # Teardrop
        if (pyxel.frame_count // 8) % 2 == 0:
            pyxel.pset(x + 5, y + 10, COL_CYAN)

    # Torso (Yellow hoodie)
    pyxel.rect(x + 3, y + 15, 14, 11, COL_YELLOW)
    pyxel.rect(x + 5, y + 26, 4, 5, COL_BLUE)   # Left pant leg
    pyxel.rect(x + 11, y + 26, 4, 5, COL_BLUE)  # Right pant leg

    # Tag
    pyxel.text(x + 1, y + 33, "STUDENT", COL_WHITE)


def draw_coach_sprite(x: int, y: int, happiness: float, is_speaking: bool = False):
    """Draws an 8-bit math coach sprite with glasses and clipboard."""
    if is_speaking and (pyxel.frame_count // 6) % 2 == 0:
        pyxel.rectb(x - 3, y - 3, 28, 36, COL_YELLOW)

    # Hair
    pyxel.rect(x + 5, y, 12, 4, COL_BROWN)

    # Face
    pyxel.rect(x + 5, y + 4, 12, 11, COL_PEACH)

    # Glasses
    pyxel.rectb(x + 5, y + 7, 5, 4, COL_CYAN)
    pyxel.rectb(x + 12, y + 7, 5, 4, COL_CYAN)
    pyxel.line(x + 10, y + 8, x + 12, y + 8, COL_CYAN)

    # Mouth
    if happiness >= 80:
        pyxel.line(x + 8, y + 13, x + 13, y + 13, COL_BLACK)
        pyxel.pset(x + 7, y + 12, COL_BLACK)
        pyxel.pset(x + 14, y + 12, COL_BLACK)
    elif happiness >= 50:
        pyxel.line(x + 9, y + 13, x + 12, y + 13, COL_BLACK)
    else:
        # Frown
        pyxel.line(x + 9, y + 14, x + 13, y + 14, COL_BLACK)
        pyxel.pset(x + 8, y + 15, COL_BLACK)
        pyxel.pset(x + 14, y + 15, COL_BLACK)

    # Body (Blue coach polo)
    pyxel.rect(x + 4, y + 15, 14, 13, COL_CYAN)

    # Clipboard in hand
    pyxel.rect(x + 17, y + 17, 6, 9, COL_LIGHT_GRAY)
    pyxel.rectb(x + 17, y + 17, 6, 9, COL_DARK_GRAY)

    # Pants
    pyxel.rect(x + 5, y + 28, 4, 5, COL_DARK_GRAY)
    pyxel.rect(x + 12, y + 28, 4, 5, COL_DARK_GRAY)

    # Tag
    pyxel.text(x + 5, y + 35, "COACH", COL_WHITE)


def draw_parent_sprite(x: int, y: int, happiness: float, is_speaking: bool = False):
    """Draws an 8-bit parent booster sprite."""
    if is_speaking and (pyxel.frame_count // 6) % 2 == 0:
        pyxel.rectb(x - 3, y - 3, 26, 35, COL_YELLOW)

    # Hair
    pyxel.rect(x + 4, y, 13, 6, COL_DARK_GRAY)

    # Face
    pyxel.rect(x + 5, y + 5, 11, 10, COL_PEACH)

    # Eyes & Mouth
    pyxel.pset(x + 7, y + 8, COL_BLACK)
    pyxel.pset(x + 12, y + 8, COL_BLACK)

    if happiness >= 80:
        pyxel.line(x + 8, y + 12, x + 12, y + 12, COL_PINK)
    elif happiness >= 50:
        pyxel.line(x + 8, y + 12, x + 11, y + 12, COL_BLACK)
    else:
        # Angry furrowed brow
        pyxel.line(x + 6, y + 6, x + 8, y + 7, COL_BLACK)
        pyxel.line(x + 13, y + 6, x + 11, y + 7, COL_BLACK)
        pyxel.line(x + 8, y + 13, x + 12, y + 13, COL_RED)

    # Jacket (Purple cardigan)
    pyxel.rect(x + 3, y + 15, 14, 12, COL_PURPLE)

    # Coffee mug in hand
    pyxel.rect(x + 16, y + 19, 4, 5, COL_WHITE)
    pyxel.pset(x + 17, y + 17, (COL_LIGHT_GRAY if (pyxel.frame_count // 10) % 2 == 0 else COL_WHITE))

    # Skirt / Pants
    pyxel.rect(x + 5, y + 27, 10, 6, COL_DARK_GRAY)

    # Tag
    pyxel.text(x + 4, y + 34, "PARENT", COL_WHITE)
