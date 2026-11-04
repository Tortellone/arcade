"""Piattaforma colorata per il level design."""

import arcade


class Piattaforma(arcade.Sprite):
    """Sprite rettangolare pieno usato come superficie di appoggio.

    Il parametro `y` rappresenta la superficie superiore (dove si cammina).
    Lo sprite viene centrato in modo che il suo bordo superiore corrisponda a y.
    """

    def __init__(self, x: float, y: float, width: float, height: float, color):
        name = f"platform_{int(x)}_{int(y)}_{int(width)}_{int(height)}"
        texture = arcade.Texture.create_empty(name, (1, 1), color)
        super().__init__(
            path_or_texture=texture,
            center_x=x,
            center_y=y - height / 2,
        )
        self.width = width
        self.height = height
        self.color = color

    def update(self, delta_time: float = 1 / 60, *args, **kwargs):
        # Le piattaforme sono statiche
        super().update(delta_time, *args, **kwargs)
