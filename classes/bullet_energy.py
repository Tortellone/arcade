"""Proiettile energia sparato dai nemici (UFO)."""

import math
import os

import arcade

from . import config
from .config import SPRITE_FOLDER, SPRITES, BULLET_FPS, _resolve_sprite_path, load_sprite_sheet


class BulletEnergy(arcade.Sprite):
    """Proiettile energia sparato dai nemici."""

    def __init__(self, center_x: float, center_y: float, facing_right: bool = True, vx: float = None, vy: float = None):
        textures = self._load_textures()
        super().__init__(
            path_or_texture=textures[0],
            scale=1.0,
            center_x=center_x,
            center_y=center_y,
        )
        self.textures = textures
        self.texture = textures[0]
        self.facing_right = facing_right
        self.is_enemy = True

        # Dimensioni da settings.md (calcolate tramite scale)
        sprite_cfg = SPRITES.get("bullet_energy", {})
        tex_w = self.texture.width
        tex_h = self.texture.height
        if "width" in sprite_cfg:
            self.scale_x = float(sprite_cfg["width"]) / tex_w
        if "height" in sprite_cfg:
            self.scale_y = float(sprite_cfg["height"]) / tex_h

        if vx is not None:
            self.change_x = vx
        else:
            self.change_x = config.UFO_BULLET_SPEED if facing_right else -config.UFO_BULLET_SPEED
        if vy is not None:
            self.change_y = vy
        else:
            self.change_y = 0.0
        self.time_counter = 0.0
        if vx is not None and vy is not None:
            # Proiettile direzionale: ruota verso il movimento
            self.angle = math.degrees(math.atan2(vy, vx))
        elif not facing_right:
            self.scale_x = -abs(self.scale_x)

    def _load_textures(self):
        path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_bullet_energy")
        return load_sprite_sheet(path)

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_counter += delta_time
        frame = int(self.time_counter * BULLET_FPS) % len(self.textures)
        self.texture = self.textures[frame]

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.update_animation(delta_time)
        super().update(delta_time, *args, **kwargs)
