"""Sprite esplosione con animazione una-tantum (5x5 frames 64x64)."""

import os
import arcade

from .config import SPRITE_FOLDER, EXPLOSION_FPS, _resolve_sprite_path, load_sprite_sheet


class Explosion(arcade.Sprite):
    """Esplosione che si riproduce una volta e poi si auto-rimuove."""

    def __init__(self, center_x: float, center_y: float, scale: float = 1.0):
        textures = self._load_textures()
        super().__init__(
            path_or_texture=textures[0],
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )
        self.all_textures = textures
        self.texture = textures[0]
        self.time_counter = 0.0
        self._fps = EXPLOSION_FPS
        self.finished = False

    def _load_textures(self):
        path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_explosion")
        return load_sprite_sheet(path)

    def update_animation(self, delta_time: float = 1 / 60):
        if self.finished:
            return
        self.time_counter += delta_time
        frame = int(self.time_counter * self._fps)
        if frame >= len(self.all_textures):
            frame = len(self.all_textures) - 1
            self.finished = True
        self.texture = self.all_textures[frame]

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.update_animation(delta_time)
        super().update(delta_time, *args, **kwargs)
        if self.finished:
            self.remove_from_sprite_lists()
