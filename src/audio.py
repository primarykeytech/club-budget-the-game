"""8-bit chiptune sound effects and audio management using Pyxel sound generator."""

import pyxel


class SoundManager:
    """Configures and plays authentic 8-bit sound effects."""

    SOUND_SELECT = 0
    SOUND_CONFIRM = 1
    SOUND_CASH = 2
    SOUND_ALARM = 3
    SOUND_GAME_OVER = 4
    SOUND_VICTORY = 5
    SOUND_MATH_CORRECT = 6

    def __init__(self):
        self.muted = False
        self._init_sounds()

    def _init_sounds(self):
        # 0: Menu cursor tick
        pyxel.sounds[self.SOUND_SELECT].set(
            notes="c3",
            tones="p",
            volumes="4",
            effects="n",
            speed=3,
        )

        # 1: Option confirm
        pyxel.sounds[self.SOUND_CONFIRM].set(
            notes="c3e3",
            tones="s",
            volumes="65",
            effects="nn",
            speed=4,
        )

        # 2: Coin / Cash transaction
        pyxel.sounds[self.SOUND_CASH].set(
            notes="b3e4",
            tones="s",
            volumes="67",
            effects="nn",
            speed=5,
        )

        # 3: Low alarm / Budget drop / Danger
        pyxel.sounds[self.SOUND_ALARM].set(
            notes="f2c2",
            tones="t",
            volumes="77",
            effects="sn",
            speed=12,
        )

        # 4: Game Over (Sad downward slide)
        pyxel.sounds[self.SOUND_GAME_OVER].set(
            notes="c3b2a2g2f2e2d2c2",
            tones="s",
            volumes="77665543",
            effects="sssssssf",
            speed=12,
        )

        # 5: Victory fanfare
        pyxel.sounds[self.SOUND_VICTORY].set(
            notes="c3e3g3c4g3c4",
            tones="s",
            volumes="667777",
            effects="nnnnvv",
            speed=9,
        )

        # 6: Correct math answer chime
        pyxel.sounds[self.SOUND_MATH_CORRECT].set(
            notes="g3c4e4g4",
            tones="t",
            volumes="5677",
            effects="nnnn",
            speed=5,
        )

    def play(self, sound_id: int, channel: int = 0):
        if self.muted:
            return
        try:
            pyxel.play(channel, sound_id)
        except Exception:
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted
