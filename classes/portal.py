"""Portale animato per segnare l'ingresso/uscita di un livello."""

import os
import arcade

from .config import SPRITE_FOLDER, _resolve_sprite_path, load_sprite_sheet


class Portal(arcade.Sprite):
    """Portale animato con 9 frame orizzontali presi da sprite_portal.png.

    Le dimensioni dei frame vengono calcolate automaticamente dall'immagine:
    - larghezza = larghezza_immagine // 9
    - altezza = altezza_immagine
    """

    def __init__(self, center_x: float, center_y: float, scale: float = 1.0, target_level: int = None):
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
        self._fps = 12.0
        self.target_level = target_level  # indice 0-based del livello di destinazione

    def _load_textures(self):
        path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_portal")
        return load_sprite_sheet(path)

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_counter += delta_time
        frame = int(self.time_counter * self._fps) % len(self.all_textures)
        self.texture = self.all_textures[frame]

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.update_animation(delta_time)
        super().update(delta_time, *args, **kwargs)