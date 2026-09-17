# Club Budget: The Game 🧮🎮

An 8-bit state-machine-driven resource management simulation built with **[Pyxel](https://github.com/kitao/pyxel)**, designed specifically for afterschool math clubs.

Players take on the role of club treasurer and leadership, steering their math club through a full school year. You must make strategic budgetary decisions (supplies, competition travel, t-shirts, fundraisers, snacks) while balancing the happiness of three vital stakeholders: **Students**, **Coaches**, and **Parents**.

---

## 🎯 Objectives & Win/Loss Rules

* **Goal:** Keep all three happiness scores (Student, Coach, Parent) **$\ge 80\%$** by the end of the club season.
* **Immediate Loss Triggers (< 40%):**
  * If **Student Happiness** drops below $40\%$, students stage a mutiny and stop showing up!
  * If **Coach Happiness** drops below $40\%$, the coach resigns from burnout and frustration.
  * If **Parent Happiness** drops below $40\%$, parents boycott and pull their kids from the program.
  * If **Budget** drops below $\$0.00$, the club goes bankrupt and activities are suspended.

---

## 📐 5th-Grade Math Concepts Integrated

The simulation weaves Common Core 5th-grade math topics directly into gameplay choices:

1. **Decimal Multiplication & Unit Pricing:**
   * Calculating bulk supplies: e.g., $\$0.25 \times 16 \text{ students} = \$4.00$, or $\$1.75 \times 16 = \$28.00$.
2. **Multi-Step Profit & Loss Margins:**
   * Bake sales & mathathons: $\text{Net Profit} = (\text{Quantity} \times \text{Price}) - \text{Supply Cost}$.
3. **Fractions, Division & Percentages:**
   * Calculating $25\%$ coupons on buzzer sets, or sending the top half ($1/2$) of students to state competitions.
4. **Mental Estimation & Burn Rate:**
   * In-game advisor tracks safe weekly burn rates ($\text{Remaining Budget} \div \text{Remaining Weeks}$).
5. **Interactive Math Challenges:**
   * Answering scenario math challenges correctly earns **Bonus Happiness** across stakeholders! Answering incorrectly incurs an administrative penalty fee.

---

## 🕹️ Controls

| Key | Action |
| :--- | :--- |
| **`UP` / `DOWN` Arrow** | Navigate menu items, choices, and multiple-choice math answers |
| **`LEFT` / `RIGHT` Arrow** | Adjust setup parameters (Club name preset, Budget, Student count, Weeks) |
| **`ENTER` / `SPACE` / `Z`** | Confirm selection / Advance turn |
| **`M`** | Toggle audio mute |
| **`R`** | Restart game (after Game Over or Victory) |
| **`Q`** | Quit game |

---

## 🚀 Getting Started

### 1. Requirements
* Python 3.10+ (Tested on Python 3.11 - 3.13)
* `pyxel` library

### 2. Set Up a Virtual Environment (Recommended)
Running in a virtual environment keeps project dependencies isolated and prevents version conflicts.

#### Step A: Create the virtual environment
```bash
# Windows / macOS / Linux
python -m venv .venv
```

#### Step B: Activate the environment
* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(If script execution is disabled on your system, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

* **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
With your virtual environment activated:
```bash
pip install -r requirements.txt
```

### 4. Run the Game
Launch the simulation:
```bash
python main.py
```

### 5. Running the Tests
To run the automated headless test suite:
```bash
python -m unittest discover tests
```

---

## 📁 Project Structure

```
club-budget-the-game/
├── data/
│   ├── scenarios.json      # Dynamic scenario cards, formulas, and math challenges
│   └── events.json         # Unexpected mid-season events (breakages, surcharges, donations)
├── src/
│   ├── model.py            # Simulation engine: ledger, formulas, win/loss rules
│   ├── fsm.py              # Finite State Machine & screens (Title, Setup, Scenario, Math, Summary)
│   ├── ui.py               # 8-bit UI: HUD, health bars, animated student/coach/parent sprites
│   ├── audio.py            # 8-bit chiptune sound generator (blips, coins, fanfare, alarms)
│   └── game.py             # Pyxel application wrapper
├── tests/
│   ├── test_model.py       # Unit tests for economic models, formulas, and loss triggers
│   └── test_fsm.py         # Headless tests for game states and transitions
├── main.py                 # Game entrypoint
└── requirements.txt        # Dependencies
```
