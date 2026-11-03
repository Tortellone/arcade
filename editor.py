import arcade
from classes import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from classes.editor_view import EditorView

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "Capitano Level Editor", resizable=True)
    import pyglet
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    x = (screen.width - WINDOW_WIDTH) // 2
    y = (screen.height - WINDOW_HEIGHT) // 2
    window.set_location(x, y)
    editor = EditorView()
    window.show_view(editor)
    arcade.run()

if __name__ == "__main__":
    main()
