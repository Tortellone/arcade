"""Modulo principale del gioco."""

from .config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    SPRITE_FOLDER,
    WALK_SPEED, RUN_SPEED,
    GRAVITY, JUMP_SPEED, GROUND_Y,
    IDLE_FPS, WALK_FPS, RUN_FPS, JUMP_FPS, CROUCH_FPS, SHOOT_FPS,
    JOY_DEADZONE, JOY_RUN_THRESHOLD,
    SHOOT_DURATION, BULLET_SPEED, BULLET_FPS,
    XINPUT_GAMEPAD_A,
)
from .xinput_reader import XInputReader
from .background_parallax import Background_Parallax
from .bullet_plasma import BulletPlasma
from .bullet_energy import BulletEnergy
from .capitano import Capitano
from .game_view import GameView
from .ufo import UFO
