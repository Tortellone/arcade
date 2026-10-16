import arcade
from classes import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, GameView


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=True)
    # Centra la finestra quando non e'' in fullscreen
    import pyglet
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    x = (screen.width - WINDOW_WIDTH) // 2
    y = (screen.height - WINDOW_HEIGHT) // 2
    window.set_location(x, y)
    game = GameView(window)
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
