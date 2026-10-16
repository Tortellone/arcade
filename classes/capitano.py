"""Personaggio giocatore Capitano con animazioni e fsm."""

import os
import arcade

from .config import (
    SPRITE_FOLDER, SPRITES, _resolve_sprite_path, load_sprite_sheet,
    WALK_SPEED, RUN_SPEED, GRAVITY, JUMP_SPEED, GROUND_Y,
    IDLE_FPS, WALK_FPS, RUN_FPS, JUMP_FPS, CROUCH_FPS, SHOOT_FPS,
    SHOOT_DURATION, DEATH_FPS,
)
from .bullet_plasma import BulletPlasma


class Capitano(arcade.Sprite):
    """Personaggio giocatore Capitano con animazioni e fsm."""

    def __init__(self, center_x: float, center_y: float):
        textures = self._load_textures()
        super().__init__(
            path_or_texture=textures["idle"][0],
            scale=1.0,
            center_x=center_x,
            center_y=center_y,
        )
        self.all_textures = textures
        self.current_action = "idle"
        self.texture = textures["idle"][0]
        self.textures = textures["idle"]
        self.time_counter = 0.0
        self.facing_right = True

        # Dimensioni da settings.md (calcolate tramite scale per evitare
        # problemi di flip con scale_x negativo)
        sprite_cfg = SPRITES.get("capitano", {})
        tex_w = self.texture.width
        tex_h = self.texture.height
        if "width" in sprite_cfg:
            self.scale_x = float(sprite_cfg["width"]) / tex_w
        if "height" in sprite_cfg:
            self.scale_y = float(sprite_cfg["height"]) / tex_h

        # Fisica
        self.change_x = 0.0
        self.change_y = 0.0
        self.on_ground = False
        self.ground_y = GROUND_Y

        # Tirosi
        self.is_shooting = False
        self.shoot_timer = 0.0

        # Morte
        self.is_dead = False
        self.death_timer = 0.0
        self.death_done = False

    def _load_textures(self):
        actions = [
            "idle", "idle_shot",
            "walk", "walk_shot",
            "run", "run_shot",
            "jump", "jump_shot",
            "crouch", "crouch_shot",
            "death",
        ]
        result = {}
        for action in actions:
            base = f"sprite_capitano_{action}"
            path = _resolve_sprite_path(SPRITE_FOLDER, base)
            result[action] = load_sprite_sheet(path)
        return result

    def set_action(self, action: str):
        """Cambia l''azione visiva se necessario."""
        if self.is_dead and action != "death":
            return
        if self.current_action != action:
            self.current_action = action
            self.textures = self.all_textures[action]
            self.time_counter = 0.0
            self.texture = self.textures[0]

    def set_facing(self, facing_right: bool):
        """Cambia la direzione dello sprite preservando il modulo dello scale."""
        if self.is_dead:
            return
        if self.facing_right != facing_right:
            self.facing_right = facing_right
            self.scale_x = abs(self.scale_x) if facing_right else -abs(self.scale_x)

    def start_shoot(self):
        """Inizia l''animazione di sparo."""
        if self.is_dead:
            return
        self.is_shooting = True
        self.shoot_timer = 0.0

    def update_animation(self, delta_time: float = 1 / 60):
        self.time_counter += delta_time
        fps_map = {
            "idle": IDLE_FPS, "idle_shot": SHOOT_FPS,
            "walk": WALK_FPS, "walk_shot": SHOOT_FPS,
            "run": RUN_FPS, "run_shot": SHOOT_FPS,
            "jump": JUMP_FPS, "jump_shot": SHOOT_FPS,
            "crouch": CROUCH_FPS, "crouch_shot": SHOOT_FPS,
        }
        fps = fps_map.get(self.current_action, IDLE_FPS)
        frame = int(self.time_counter * fps) % len(self.textures)
        self.texture = self.textures[frame]

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        if self.is_dead:
            self.death_timer += delta_time
            total_frames = len(self.textures)
            duration = total_frames / DEATH_FPS if total_frames > 0 else 0.0
            if self.death_timer >= duration:
                self.death_done = True
                self.texture = self.textures[-1]
            else:
                frame = int(self.death_timer * DEATH_FPS)
                self.texture = self.textures[min(frame, total_frames - 1)]
            return

        self.update_animation(delta_time)

        # Aggiorna timer di sparo
        if self.is_shooting:
            self.shoot_timer += delta_time
            if self.shoot_timer >= SHOOT_DURATION:
                self.is_shooting = False
                self.shoot_timer = 0.0

        # Fisica
        self.change_y -= GRAVITY
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Collisione con il terreno (quota personalizzabile per livello, riferita ai piedi)
        feet_y = self.center_y - self.height / 2
        if feet_y <= self.ground_y:
            self.center_y = self.ground_y + self.height / 2
            self.change_y = 0.0
            self.on_ground = True
        else:
            self.on_ground = False

    def jump(self):
        """Fa saltare il personaggio."""
        if self.is_dead:
            return
        if self.on_ground:
            self.change_y = JUMP_SPEED
            self.on_ground = False

    def die(self):
        """Inizia l'animazione di morte."""
        if self.is_dead:
            return
        self.is_dead = True
        self.death_done = False
        self.death_timer = 0.0
        self.change_x = 0.0
        self.change_y = 0.0
        self.set_action("death")

    def create_bullet(self) -> BulletPlasma:
        """Crea un proiettile diretto nella direzione in cui guarda il personaggio."""
        if self.is_dead:
            return None
        bx = self.center_x + (35 if self.facing_right else -35)
        by = self.center_y
        return BulletPlasma(bx, by, self.facing_right)






