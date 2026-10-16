"""Sfondo parallasse a piu'' strati che scorrono a velocita'' diverse."""

import os
import arcade

from .config import WINDOW_WIDTH, WINDOW_HEIGHT


class Background_Parallax:
    """Sfondo parallasse a piu'' strati che scorrono a velocita'' diverse."""

    def __init__(self, image_paths=None):
        self.layers = []
        if not image_paths:
            return
        for idx, path in enumerate(image_paths):
            # Se il percorso e'' relativo, risolvilo rispetto alla cartella del progetto
            if not os.path.isabs(path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(base_dir, path)
            texture = arcade.load_texture(path)
            speed = 0.1 * (idx + 1)  # strato 1 (lontano)=0.1 ... strato n (vicino)=0.1*n
            self.layers.append({
                "texture": texture,
                "speed": speed,
            })

    def draw(self, camera_x: float = 0.0):
        """Disegna tutti gli strati dal piu'' lontano al piu'' vicino."""
        for layer in self.layers:
            tex = layer["texture"]
            w = tex.width

            # Offset orizzontale basato sulla camera con wrap-around
            total_offset = (-camera_x * layer["speed"]) % w
            start_x = total_offset - w

            # Disegna copie affiancate fino a coprire lo schermo
            x = start_x
            while x < WINDOW_WIDTH:
                arcade.draw_texture_rect(
                    tex,
                    arcade.LBWH(x, 0, w, WINDOW_HEIGHT),
                )
                x += w
