"""8-bit chiptune sound effects and audio management using Pyxel sound generator."""

import pyxel


class SoundManager:
    """Configures and plays authentic 8-bit sound effects and chiptune music."""

    # SFX Sound IDs
    SOUND_SELECT = 0
    SOUND_CONFIRM = 1
    SOUND_CASH = 2
    SOUND_ALARM = 3
    SOUND_GAME_OVER = 4
    SOUND_VICTORY = 5
    SOUND_MATH_CORRECT = 6

    # Title Theme Song Sound IDs (Melody, Harmony, Bass across 4 phrases)
    # Phrase A (Bars 1-2)
    THEME_MEL_A = 10
    THEME_HAR_A = 11
    THEME_BAS_A = 12

    # Phrase B (Bars 3-4)
    THEME_MEL_B = 13
    THEME_HAR_B = 14
    THEME_BAS_B = 15

    # Phrase C (Bars 5-6)
    THEME_MEL_C = 16
    THEME_HAR_C = 17
    THEME_BAS_C = 18

    # Phrase D (Bars 7-8, Turnaround & Loop)
    THEME_MEL_D = 19
    THEME_HAR_D = 20
    THEME_BAS_D = 21

    MUSIC_TITLE = 0

    def __init__(self):
        self.muted = False
        self.music_playing = False
        self._init_sounds()
        self._init_theme_music()

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

    def _init_theme_music(self):
        """Composes an original upbeat 8-bit chiptune theme song: 'The Mathletes Anthem'."""
        # Phrase A (Bars 1-2): Opening energetic fanfare
        pyxel.sounds[self.THEME_MEL_A].set(
            notes="c3 e3 g3 c4 e4 d4 c4 g3 a3 c4 d4 e4 d4 c4 b3 g3",
            tones="s",
            volumes="6 6 7 7 7 6 7 6 6 7 7 7 6 6 5 6",
            effects="n n n n v n n n n n n v f n n v",
            speed=8,
        )
        pyxel.sounds[self.THEME_HAR_A].set(
            notes="c3 g3 e3 g3 b2 g3 d3 g3 a2 e3 c3 e3 g2 d3 b2 d3",
            tones="t",
            volumes="5 4 5 4 5 4 5 4 5 4 5 4 5 4 5 4",
            effects="n",
            speed=8,
        )
        pyxel.sounds[self.THEME_BAS_A].set(
            notes="c2 c2 g1 g1 b1 b1 g1 g1 a1 a1 e1 e1 g1 g1 d1 d1",
            tones="s",
            volumes="6 5 6 5 6 5 6 5 6 5 6 5 6 5 6 5",
            effects="n",
            speed=8,
        )

        # Phrase B (Bars 3-4): Rising adventure progression
        pyxel.sounds[self.THEME_MEL_B].set(
            notes="a3 c4 e4 g4 f4 e4 d4 c4 d4 e4 f4 g4 a4 b4 c4 r",
            tones="s",
            volumes="6 7 7 7 6 6 6 6 6 7 7 7 7 7 7 0",
            effects="n n n v n n n n n n n n n n s n",
            speed=8,
        )
        pyxel.sounds[self.THEME_HAR_B].set(
            notes="f2 c3 a2 c3 g2 d3 b2 d3 a2 e3 c3 e3 g2 d3 b2 d3",
            tones="t",
            volumes="5 4 5 4 5 4 5 4 5 4 5 4 5 4 5 4",
            effects="n",
            speed=8,
        )
        pyxel.sounds[self.THEME_BAS_B].set(
            notes="f1 f1 c2 c2 g1 g1 d2 d2 a1 a1 e2 e2 g1 g1 g1 g1",
            tones="s",
            volumes="6 5 6 5 6 5 6 5 6 5 6 5 6 6 6 6",
            effects="n",
            speed=8,
        )

        # Phrase C (Bars 5-6): Bouncing playful rhythm
        pyxel.sounds[self.THEME_MEL_C].set(
            notes="c4 g4 e4 c4 f4 a4 c4 b4 a4 g4 e4 c4 d4 e4 d4 r",
            tones="s",
            volumes="7 7 6 6 6 7 7 6 6 6 5 5 6 6 5 0",
            effects="v n n n n n v n n n n n n n f n",
            speed=8,
        )
        pyxel.sounds[self.THEME_HAR_C].set(
            notes="a2 e3 c3 e3 f2 c3 a2 c3 c3 g3 e3 g3 g2 d3 b2 d3",
            tones="t",
            volumes="5 4 5 4 5 4 5 4 5 4 5 4 5 4 5 4",
            effects="n",
            speed=8,
        )
        pyxel.sounds[self.THEME_BAS_C].set(
            notes="a1 a1 e2 e2 f1 f1 c2 c2 c2 c2 g1 g1 g1 g1 d2 d2",
            tones="s",
            volumes="6 5 6 5 6 5 6 5 6 5 6 5 6 5 6 5",
            effects="n",
            speed=8,
        )

        # Phrase D (Bars 7-8): Turnaround and triumphant loop back
        pyxel.sounds[self.THEME_MEL_D].set(
            notes="e3 f3 g3 a3 b3 c4 d4 b3 c4 g3 e3 d3 c3 r r r",
            tones="s",
            volumes="6 6 7 7 7 7 7 6 7 6 6 5 6 0 0 0",
            effects="n n n n n v n n v f f f f n n n",
            speed=8,
        )
        pyxel.sounds[self.THEME_HAR_D].set(
            notes="f2 c3 a2 c3 g2 d3 b2 d3 c3 g3 e3 g3 c3 r r r",
            tones="t",
            volumes="5 4 5 4 5 4 5 4 6 5 5 4 5 0 0 0",
            effects="n",
            speed=8,
        )
        pyxel.sounds[self.THEME_BAS_D].set(
            notes="f1 f1 a1 a1 g1 g1 b1 b1 c2 e2 g2 c2 c2 r r r",
            tones="s",
            volumes="6 5 6 5 6 5 6 5 7 6 6 5 6 0 0 0",
            effects="n",
            speed=8,
        )

        # Assemble the 8-measure piece into Pyxel's Music channel 0
        pyxel.musics[self.MUSIC_TITLE].set(
            [self.THEME_MEL_A, self.THEME_MEL_B, self.THEME_MEL_C, self.THEME_MEL_D],
            [self.THEME_HAR_A, self.THEME_HAR_B, self.THEME_HAR_C, self.THEME_HAR_D],
            [self.THEME_BAS_A, self.THEME_BAS_B, self.THEME_BAS_C, self.THEME_BAS_D],
        )

    def play(self, sound_id: int, channel: int = 3):
        """Plays a one-shot sound effect (defaults to channel 3 to avoid clipping music)."""
        if self.muted:
            return
        try:
            pyxel.play(channel, sound_id)
        except Exception:
            pass

    def play_title_music(self):
        """Plays the opening theme song on loop."""
        if self.muted or self.music_playing:
            return
        try:
            pyxel.playm(self.MUSIC_TITLE, loop=True)
            self.music_playing = True
        except Exception:
            pass

    def stop_music(self):
        """Stops background music playback."""
        try:
            pyxel.stop()
            self.music_playing = False
        except Exception:
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.stop_music()
        return self.muted
