"""Nemico UFO con animazione e AI di pattugliamento orizzontale."""

import arcade
import math
import os

from . import config
from .bullet_energy import BulletEnergy
from .config import WINDOW_WIDTH, WINDOW_HEIGHT, SPRITE_FOLDER, SPRITES, _resolve_sprite_path, load_sprite_sheet




class UFO(arcade.Sprite):
    """Nemico UFO con sprite sheet 96x96x20 e AI di pattugliamento."""

    def __init__(self, start_x: float, start_y: float, bounds_width: float = WINDOW_WIDTH, bounds_height: float = WINDOW_HEIGHT):
        textures = self._load_textures()
        super().__init__(
            path_or_texture=textures[0],
            scale=1.0,
            center_x=start_x,
            center_y=start_y,
        )
        self.all_textures = textures
        self.texture = textures[0]
        self.time_counter = 0.0

        # Dimensioni da settings.md
        sprite_cfg = SPRITES.get("ufo", {})
        if "width" in sprite_cfg:
            self.width = float(sprite_cfg["width"])
        if "height" in sprite_cfg:
            self.height = float(sprite_cfg["height"])
        self.change_x = config.UFO_SPEED
        self.shoot_timer = 0.0
        self._fps = 12.0
        self.bounds_width = bounds_width
        self.bounds_height = bounds_height

    def _load_textures(self):
        path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_ufo")
        return load_sprite_sheet(path)

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_counter += delta_time
        frame = int(self.time_counter * self._fps) % len(self.all_textures)
        self.texture = self.all_textures[frame]

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        self.update_animation(delta_time)
        super().update(delta_time, *args, **kwargs)

    def ai(self, target):
        """Muove l'UFO verso il target in modo fluido.
        L'UFO cerca sempre di posizionarsi sopra la testa del capitano,
        sia che sia a terra, su una piattaforma o in salto.
        Il movimento verticale è limitato a UFO_VERTICAL_SPEED per evitare scatti.
        """
        if target is None:
            return

        dx = target.center_x - self.center_x

        # --- Movimento orizzontale verso il capitano ---
        if abs(dx) > 1.0:
            self.change_x = math.copysign(config.UFO_SPEED, dx)
        else:
            self.change_x = 0.0

        # --- Movimento verticale: resta sopra la testa del capitano ---
        target_head_y = target.center_y + target.height / 2
        hover_y = target_head_y + self.height / 2
        dy = hover_y - self.center_y
        max_vy = config.UFO_VERTICAL_SPEED

        if dy > max_vy:
            self.change_y = max_vy
        elif dy < -max_vy:
            self.change_y = -max_vy
        else:
            self.change_y = dy

        # Limite inferiore morbido: se è sotto l'altezza di hover, sale senza teletrasporto
        if self.center_y < hover_y:
            self.change_y = max(self.change_y, min(max_vy, hover_y - self.center_y))

        # Limiti orizzontali del livello (smooth: frena sul bordo)
        half_width = self.width / 2
        next_x = self.center_x + self.change_x
        if next_x + half_width > self.bounds_width:
            self.change_x = max(0.0, self.bounds_width - half_width - self.center_x)
        elif next_x - half_width < 0:
            self.change_x = min(0.0, half_width - self.center_x)
        # Se per qualche motivo è già fuori, torna indietro lentamente
        if self.center_x + half_width > self.bounds_width:
            self.center_x = self.bounds_width - half_width
        elif self.center_x - half_width < 0:
            self.center_x = half_width

        # Limiti verticali del livello (smooth: frena sui bordi superiore/inferiore)
        half_height = self.height / 2
        next_y = self.center_y + self.change_y
        if next_y + half_height > self.bounds_height:
            self.change_y = max(0.0, self.bounds_height - half_height - self.center_y)
        elif next_y - half_height < 0:
            self.change_y = min(0.0, half_height - self.center_y)
        # Se per qualche motivo è già fuori, rientra lentamente
        if self.center_y + half_height > self.bounds_height:
            self.center_y = self.bounds_height - half_height
        elif self.center_y - half_height < 0:
            self.center_y = half_height

    def maybe_shoot(self, target, delta_time: float = 1 / 60):
        """Spara un proiettile verso il target se è trascorso l'intervallo configurato.
        Restituisce il Bullet creato oppure None.
        """
        if target is None:
            return None
        self.shoot_timer += delta_time
        if self.shoot_timer >= config.UFO_SHOOT_INTERVAL:
            self.shoot_timer = 0.0
            dx = target.center_x - self.center_x
            dy = target.center_y - self.center_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                vx = (dx / dist) * config.UFO_BULLET_SPEED
                vy = (dy / dist) * config.UFO_BULLET_SPEED
                return BulletEnergy(
                    self.center_x, self.center_y,
                    facing_right=dx > 0, vx=vx, vy=vy,
                )
        return None

