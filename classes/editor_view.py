"""Editor di livelli WYSIWYG per Capitano."""

import arcade
import math
import os

from . import config
from .config import (
    LEVELS,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    SPRITE_FOLDER,
    _resolve_sprite_path,
    load_sprite_sheet,
    SETTINGS_MD_PATH,
    save_levels_to_md,
)


class EditorView(arcade.View):
    """Vista editor per piazzare e modificare livelli."""

    def __init__(self):
        super().__init__()
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.tool = "select"
        self.selected_type = None
        self.selected_index = -1

        self.current_level_idx = 0
        self.level = None
        self.load_level(0)

        self.dragging = False
        self.last_mouse_world = (0, 0)

        # Resize con mouse su handle
        self.resize_handle = None
        self.resize_anchor = None

        self.toolbar_height = 50
        self.panel_width = 280

        self.platform_colors = [
            ("TRANSPARENT", (0, 0, 0, 0)),
            ("RED", arcade.color.RED),
            ("BLUE", arcade.color.BLUE),
            ("GREEN", arcade.color.GREEN),
            ("GRAY", arcade.color.GRAY),
            ("YELLOW", arcade.color.YELLOW),
            ("BLACK", arcade.color.BLACK),
            ("WHITE", arcade.color.WHITE),
        ]

        self._textures = {}
        self._load_preview_textures()

        self.status_msg = ""
        self.status_timer = 0.0

    def _load_preview_textures(self):
        try:
            path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_capitano_idle")
            tex = load_sprite_sheet(path)
            self._textures["capitano"] = tex[0]
        except Exception:
            self._textures["capitano"] = None

        try:
            path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_ufo")
            tex = load_sprite_sheet(path)
            self._textures["ufo"] = tex[0]
        except Exception:
            self._textures["ufo"] = None

        try:
            path = _resolve_sprite_path(SPRITE_FOLDER, "sprite_portal")
            tex = load_sprite_sheet(path)
            self._textures["portal"] = tex[0]
        except Exception:
            self._textures["portal"] = None

    def load_level(self, idx):
        self.current_level_idx = idx
        self.level = LEVELS[idx]
        self.selected_type = None
        self.selected_index = -1
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.status_msg = f"Livello {idx + 1} caricato"
        self.status_timer = 2.0

    def screen_to_world(self, sx, sy):
        wx = sx / self.zoom + self.offset_x
        wy = sy / self.zoom + self.offset_y
        return wx, wy

    def world_to_screen(self, wx, wy):
        sx = (wx - self.offset_x) * self.zoom
        sy = (wy - self.offset_y) * self.zoom
        return sx, sy

    def on_draw(self):
        self.clear()
        w = self.window.width if self.window else WINDOW_WIDTH
        h = self.window.height if self.window else WINDOW_HEIGHT

        # Disegna mondo (coordinate schermo calcolate da world)
        self._draw_background(w, h)
        self._draw_grid(w, h)

        for i, pf in enumerate(self.level.get("platforms", [])):
            sel = self.selected_type == "platform" and self.selected_index == i
            self._draw_platform(pf, selected=sel)

        for i, sp in enumerate(self.level.get("sprites", [])):
            sel = self.selected_type == "sprite" and self.selected_index == i
            self._draw_sprite(sp, selected=sel)

        # UI in coordinate schermo
        self._draw_toolbar(w, h)
        self._draw_property_panel(w, h)

    def _draw_grid(self, w, h):
        level_w = self.level.get("width", 1920)
        level_h = self.level.get("height", 1080)
        for x in range(0, level_w + 1, 100):
            x1, y1 = self.world_to_screen(x, 0)
            x2, y2 = self.world_to_screen(x, level_h)
            if x1 < w and x1 > 0:
                arcade.draw_line(x1, y1, x2, y2, arcade.color.DARK_GRAY, 1)
        for y in range(0, level_h + 1, 100):
            x1, y1 = self.world_to_screen(0, y)
            x2, y2 = self.world_to_screen(level_w, y)
            if y1 < h and y1 > 0:
                arcade.draw_line(x1, y1, x2, y2, arcade.color.DARK_GRAY, 1)
        # bordo livello
        l, b = self.world_to_screen(0, 0)
        r, t = self.world_to_screen(level_w, level_h)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.RED, 2)

    def _draw_background(self, w, h):
        bg_type = self.level.get("backgroundtype", "parallax")
        if bg_type == "image":
            img = self.level.get("backgroundimage", "")
            if img:
                try:
                    tex = arcade.load_texture(img)
                    cx, cy = self.world_to_screen(
                        self.level.get("width", 1920) / 2,
                        self.level.get("height", 1080) / 2,
                    )
                    sw = tex.width * self.zoom
                    sh = tex.height * self.zoom
                    arcade.draw_texture_rect(tex, arcade.XYWH(cx, cy, sw, sh))
                except Exception:
                    pass
        elif bg_type == "parallax":
            for pimg in self.level.get("parallaximages", [])[:1]:
                try:
                    tex = arcade.load_texture(pimg)
                    cx, cy = self.world_to_screen(
                        self.level.get("width", 1920) / 2,
                        self.level.get("height", 1080) / 2,
                    )
                    sw = tex.width * self.zoom
                    sh = tex.height * self.zoom
                    arcade.draw_texture_rect(tex, arcade.XYWH(cx, cy, sw, sh), alpha=80)
                except Exception:
                    pass

    def _draw_platform(self, pf, selected=False):
        x, y = pf["x"], pf["y"]
        width, height = pf["width"], pf["height"]
        color = pf["color"]
        cy = y - height / 2
        l, b = self.world_to_screen(x - width / 2, cy - height / 2)
        r, t = self.world_to_screen(x + width / 2, cy + height / 2)
        if selected:
            arcade.draw_lrbt_rectangle_filled(l - 3, r + 3, b - 3, t + 3, arcade.color.YELLOW)
        arcade.draw_lrbt_rectangle_filled(l, r, b, t, color)
        arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 1)
        if selected:
            # Disegna 4 handle agli angoli
            for hx, hy in [(l, t), (r, t), (l, b), (r, b)]:
                arcade.draw_lrbt_rectangle_filled(hx - 5, hx + 5, hy - 5, hy + 5, arcade.color.WHITE)
                arcade.draw_lrbt_rectangle_outline(hx - 5, hx + 5, hy - 5, hy + 5, arcade.color.BLACK, 1)

    def _draw_sprite(self, sp, selected=False):
        name = sp["name"].upper()
        x, y = sp["x"], sp["y"]
        sx, sy = self.world_to_screen(x, y)
        tex = self._textures.get(name.lower())
        if tex:
            sw = tex.width * self.zoom
            sh = tex.height * self.zoom
            arcade.draw_texture_rect(tex, arcade.XYWH(sx, sy, sw, sh))
        else:
            arcade.draw_circle_filled(sx, sy, 20 * self.zoom, arcade.color.ORANGE)
        if selected:
            arcade.draw_circle_outline(sx, sy, 25 * self.zoom, arcade.color.YELLOW, 2)
        arcade.draw_text(name, sx - 20 * self.zoom, sy + 25 * self.zoom, arcade.color.WHITE, max(10, int(10 * self.zoom)))

    def _draw_toolbar(self, w, h):
        arcade.draw_lrbt_rectangle_filled(
            0, w, h - self.toolbar_height, h, arcade.color.DARK_SLATE_GRAY
        )

        tools = [
            ("select", "Select (1)"),
            ("platform", "Platform (2)"),
            ("ufo", "UFO (3)"),
            ("portal", "Portal (4)"),
            ("capitano", "Capitano (5)"),
        ]
        x = 10
        for key, label in tools:
            color = arcade.color.LIME_GREEN if self.tool == key else arcade.color.GRAY
            arcade.draw_lrbt_rectangle_filled(x, x + 120, h - self.toolbar_height + 5, h - 5, color)
            arcade.draw_text(label, x + 5, h - self.toolbar_height + 18, arcade.color.BLACK, 11)
            x += 130

        lvl_text = f"Level {self.current_level_idx + 1}/{len(LEVELS)} | Zoom {self.zoom:.1f}"
        arcade.draw_text(lvl_text, w - 300, h - self.toolbar_height + 18, arcade.color.WHITE, 12)

    def _draw_property_panel(self, w, h):
        px = w - self.panel_width
        arcade.draw_lrbt_rectangle_filled(
            px, w, 0, h - self.toolbar_height, arcade.color.DARK_SLATE_BLUE
        )

        y = h - self.toolbar_height - 20

        # Status
        if self.status_timer > 0:
            arcade.draw_text(self.status_msg, px + 10, y, arcade.color.YELLOW, 12)
            y -= 20

        # Info generali
        tool_name = self.tool.upper()
        arcade.draw_text(f"Livello {self.current_level_idx + 1}/{len(LEVELS)}", px + 10, y, arcade.color.CYAN, 12, bold=True)
        y -= 18
        arcade.draw_text(f"Zoom: {self.zoom:.1f}x | Tool: {tool_name}", px + 10, y, arcade.color.WHITE, 11)
        y -= 22

        # Sezione TOOLS
        arcade.draw_text("TOOLS", px + 10, y, arcade.color.LIME_GREEN, 12, bold=True)
        y -= 16
        arcade.draw_text("1: Select", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("2: Platform", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("3: UFO", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("4: Portal", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("5: Capitano", px + 10, y, arcade.color.WHITE, 11)
        y -= 22

        # Sezione AZIONI
        arcade.draw_text("AZIONI", px + 10, y, arcade.color.LIME_GREEN, 12, bold=True)
        y -= 16
        arcade.draw_text("PgUp/PgDn: Livello +/-", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("Ctrl+S: Salva", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("F5/P: Playtest", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("Del: Elimina", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("+/-: Zoom", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("Frecce: Pan camera", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("Shift: Precisione 1px", px + 10, y, arcade.color.WHITE, 11)
        y -= 14
        arcade.draw_text("Scroll: Zoom", px + 10, y, arcade.color.WHITE, 11)
        y -= 22

        # Sezione OGGETTO SELEZIONATO
        if self.selected_type is None:
            arcade.draw_text("NESSUNA SELEZIONE", px + 10, y, arcade.color.GRAY, 12, bold=True)
            return

        obj = self._get_selected_obj()
        if obj is None:
            return

        arcade.draw_text("SELEZIONATO", px + 10, y, arcade.color.YELLOW, 12, bold=True)
        y -= 18
        arcade.draw_text(f"Tipo: {self.selected_type.upper()}", px + 10, y, arcade.color.WHITE, 11)
        y -= 16

        if self.selected_type == "platform":
            arcade.draw_text(f"X: {obj['x']:.0f}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            arcade.draw_text(f"Y: {obj['y']:.0f} (superiore)", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            arcade.draw_text(f"W: {obj['width']:.0f}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            arcade.draw_text(f"H: {obj['height']:.0f}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            color_name = self._color_to_name(obj["color"])
            arcade.draw_text(f"Color: {color_name}", px + 10, y, arcade.color.WHITE, 11)
            y -= 20

            arcade.draw_text("MODIFICA", px + 10, y, arcade.color.CYAN, 11, bold=True)
            y -= 14
            arcade.draw_text("Drag: sposta", px + 10, y, arcade.color.WHITE, 10)
            y -= 13
            arcade.draw_text("Angoli: ridimensiona", px + 10, y, arcade.color.WHITE, 10)
            y -= 13
            arcade.draw_text("A/D: larghezza", px + 10, y, arcade.color.WHITE, 10)
            y -= 13
            arcade.draw_text("W/S: altezza", px + 10, y, arcade.color.WHITE, 10)
            y -= 13
            arcade.draw_text("C: colore", px + 10, y, arcade.color.WHITE, 10)
        elif self.selected_type == "sprite":
            arcade.draw_text(f"Name: {obj['name']}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            arcade.draw_text(f"X: {obj['x']:.0f}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            arcade.draw_text(f"Y: {obj['y']:.0f}", px + 10, y, arcade.color.WHITE, 11)
            y -= 14
            extra = obj.get("extra", "")
            if obj["name"].upper() == "PORTAL":
                arcade.draw_text(f"Goto: {extra or '-'}", px + 10, y, arcade.color.WHITE, 11)
                y -= 20
                arcade.draw_text("MODIFICA", px + 10, y, arcade.color.CYAN, 11, bold=True)
                y -= 14
                arcade.draw_text("G: cambia destinazione", px + 10, y, arcade.color.WHITE, 10)
            else:
                y -= 20
                arcade.draw_text("MODIFICA", px + 10, y, arcade.color.CYAN, 11, bold=True)
                y -= 14
                arcade.draw_text("Drag: sposta", px + 10, y, arcade.color.WHITE, 10)
                y -= 13
                arcade.draw_text("Frecce: sposta 10px", px + 10, y, arcade.color.WHITE, 10)
                y -= 13
                arcade.draw_text("Shift: precisione 1px", px + 10, y, arcade.color.WHITE, 10)

    def _color_to_name(self, color):
        if isinstance(color, tuple) and len(color) == 4 and color[3] == 0:
            return "TRANSPARENT"
        for name, val in self.platform_colors:
            if isinstance(val, tuple) and isinstance(color, tuple):
                if val == color:
                    return name
            elif hasattr(val, "__len__") and hasattr(color, "__len__"):
                if tuple(val[:3]) == tuple(color[:3]):
                    return name
        return "CUSTOM"

    def _get_selected_obj(self):
        if self.selected_type == "platform":
            platforms = self.level.get("platforms", [])
            if 0 <= self.selected_index < len(platforms):
                return platforms[self.selected_index]
        elif self.selected_type == "sprite":
            sprites = self.level.get("sprites", [])
            if 0 <= self.selected_index < len(sprites):
                return sprites[self.selected_index]
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        w = self.window.width if self.window else WINDOW_WIDTH
        h = self.window.height if self.window else WINDOW_HEIGHT

        if y > h - self.toolbar_height:
            self._handle_toolbar_click(x, y, w, h)
            return

        if x > w - self.panel_width and y < h - self.toolbar_height:
            return

        wx, wy = self.screen_to_world(x, y)
        self.last_mouse_world = (wx, wy)

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.tool == "select":
                # Prima controlla se c'e' un handle della piattaforma selezionata
                handle = self._pick_handle(wx, wy)
                if handle:
                    obj = self._get_selected_obj()
                    if obj:
                        self.resize_handle = handle
                        self.resize_anchor = {
                            "x": obj["x"], "y": obj["y"],
                            "width": obj["width"], "height": obj["height"],
                        }
                        self.dragging = True
                        return
                found = self._pick_object(wx, wy)
                if found:
                    self.selected_type, self.selected_index = found
                    self.dragging = True
                else:
                    self.selected_type = None
                    self.selected_index = -1
            else:
                self._create_object_at(wx, wy, self.tool)
                self.dragging = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.dragging:
            return
        wx, wy = self.screen_to_world(x, y)

        if self.resize_handle:
            obj = self._get_selected_obj()
            if obj and self.resize_anchor:
                ax = self.resize_anchor["x"]
                ay = self.resize_anchor["y"]
                aw = self.resize_anchor["width"]
                ah = self.resize_anchor["height"]

                if self.resize_handle == "br":
                    anchor_x = ax - aw / 2  # left fisso
                    anchor_y = ay              # top fisso
                    new_w = max(10, wx - anchor_x)
                    new_h = max(5, anchor_y - wy)
                    obj["width"] = new_w
                    obj["height"] = new_h
                    obj["x"] = anchor_x + new_w / 2
                    obj["y"] = anchor_y
                elif self.resize_handle == "bl":
                    anchor_x = ax + aw / 2  # right fisso
                    anchor_y = ay              # top fisso
                    new_w = max(10, anchor_x - wx)
                    new_h = max(5, anchor_y - wy)
                    obj["width"] = new_w
                    obj["height"] = new_h
                    obj["x"] = anchor_x - new_w / 2
                    obj["y"] = anchor_y
                elif self.resize_handle == "tr":
                    anchor_x = ax - aw / 2  # left fisso
                    anchor_y = ay - ah       # bottom fisso
                    new_w = max(10, wx - anchor_x)
                    clamped_wy = max(anchor_y + 5, wy)
                    new_h = clamped_wy - anchor_y
                    obj["width"] = new_w
                    obj["height"] = new_h
                    obj["x"] = anchor_x + new_w / 2
                    obj["y"] = clamped_wy
                elif self.resize_handle == "tl":
                    anchor_x = ax + aw / 2  # right fisso
                    anchor_y = ay - ah       # bottom fisso
                    new_w = max(10, anchor_x - wx)
                    clamped_wy = max(anchor_y + 5, wy)
                    new_h = clamped_wy - anchor_y
                    obj["width"] = new_w
                    obj["height"] = new_h
                    obj["x"] = anchor_x - new_w / 2
                    obj["y"] = clamped_wy
            return

        obj = self._get_selected_obj()
        if obj:
            obj["x"] = wx
            obj["y"] = wy

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = False
        self.resize_handle = None
        self.resize_anchor = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y == 0:
            return
        wx, wy = self.screen_to_world(x, y)
        if scroll_y > 0:
            new_zoom = min(self.zoom * 1.15, 5.0)
        else:
            new_zoom = max(self.zoom / 1.15, 0.1)
        self.offset_x = wx - x / new_zoom
        self.offset_y = wy - y / new_zoom
        self.zoom = new_zoom

    def _handle_toolbar_click(self, x, y, w, h):
        tools = ["select", "platform", "ufo", "portal", "capitano"]
        tx = 10
        for tool in tools:
            if tx <= x <= tx + 120:
                self.tool = tool
                return
            tx += 130

    def _pick_handle(self, wx, wy):
        """Restituisce il nome del handle (tl, tr, bl, br) se il click e' su un angolo della piattaforma selezionata."""
        if self.selected_type != "platform":
            return None
        platforms = self.level.get("platforms", [])
        if not (0 <= self.selected_index < len(platforms)):
            return None
        pf = platforms[self.selected_index]
        x, y, w, h = pf["x"], pf["y"], pf["width"], pf["height"]
        # Angoli in world
        corners = {
            "tl": (x - w / 2, y),
            "tr": (x + w / 2, y),
            "bl": (x - w / 2, y - h),
            "br": (x + w / 2, y - h),
        }
        # Tolleranza in world: 12 pixel schermo convertiti in world
        tol = 12 / self.zoom
        for name, (cx, cy) in corners.items():
            if math.hypot(wx - cx, wy - cy) <= tol:
                return name
        return None

    def _pick_object(self, wx, wy):
        for i, pf in enumerate(self.level.get("platforms", [])):
            half_w = pf["width"] / 2
            half_h = pf["height"] / 2
            cy = pf["y"] - pf["height"] / 2
            if (
                pf["x"] - half_w - 5 <= wx <= pf["x"] + half_w + 5
                and cy - half_h - 5 <= wy <= cy + half_h + 5
            ):
                return ("platform", i)
        for i, sp in enumerate(self.level.get("sprites", [])):
            if math.hypot(sp["x"] - wx, sp["y"] - wy) < 45:
                return ("sprite", i)
        return None

    def _create_object_at(self, wx, wy, tool):
        if tool == "platform":
            _, color_val = self.platform_colors[1]  # RED default
            new_pf = {"x": wx, "y": wy, "width": 200, "height": 20, "color": color_val}
            self.level.setdefault("platforms", []).append(new_pf)
            self.selected_type = "platform"
            self.selected_index = len(self.level["platforms"]) - 1
        elif tool == "ufo":
            new_sp = {"name": "UFO", "x": wx, "y": wy}
            self.level.setdefault("sprites", []).append(new_sp)
            self.selected_type = "sprite"
            self.selected_index = len(self.level["sprites"]) - 1
        elif tool == "portal":
            new_sp = {"name": "PORTAL", "x": wx, "y": wy, "extra": "1"}
            self.level.setdefault("sprites", []).append(new_sp)
            self.selected_type = "sprite"
            self.selected_index = len(self.level["sprites"]) - 1
        elif tool == "capitano":
            sprites = self.level.setdefault("sprites", [])
            for i, sp in enumerate(sprites):
                if sp["name"].upper() == "CAPITANO":
                    sp["x"] = wx
                    sp["y"] = wy
                    self.selected_type = "sprite"
                    self.selected_index = i
                    return
            new_sp = {"name": "CAPITANO", "x": wx, "y": wy}
            sprites.append(new_sp)
            self.selected_type = "sprite"
            self.selected_index = len(sprites) - 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.S and (modifiers & arcade.key.MOD_CTRL):
            self.save_level()
            return
        if key == arcade.key.F5 or key == arcade.key.P:
            self.playtest()
            return
        if key == arcade.key.DELETE:
            self.delete_selected()
            return
        if key == arcade.key.PAGEUP:
            if self.current_level_idx > 0:
                self.load_level(self.current_level_idx - 1)
            return
        elif key == arcade.key.PAGEDOWN:
            if self.current_level_idx < len(LEVELS) - 1:
                self.load_level(self.current_level_idx + 1)
            return

        if key == arcade.key.KEY_1:
            self.tool = "select"
        elif key == arcade.key.KEY_2:
            self.tool = "platform"
        elif key == arcade.key.KEY_3:
            self.tool = "ufo"
        elif key == arcade.key.KEY_4:
            self.tool = "portal"
        elif key == arcade.key.KEY_5:
            self.tool = "capitano"

        if key == arcade.key.EQUAL or key == arcade.key.PLUS:
            self.zoom = min(self.zoom * 1.2, 5.0)
        elif key == arcade.key.MINUS:
            self.zoom = max(self.zoom / 1.2, 0.1)

        obj = self._get_selected_obj()
        if obj is None:
            pan_speed = 50 / self.zoom
            if key == arcade.key.LEFT:
                self.offset_x -= pan_speed
            elif key == arcade.key.RIGHT:
                self.offset_x += pan_speed
            elif key == arcade.key.UP:
                self.offset_y += pan_speed
            elif key == arcade.key.DOWN:
                self.offset_y -= pan_speed
            return

        delta = 1 if modifiers & arcade.key.MOD_SHIFT else 10

        if self.selected_type == "platform":
            if key == arcade.key.LEFT:
                obj["x"] -= delta
            elif key == arcade.key.RIGHT:
                obj["x"] += delta
            elif key == arcade.key.UP:
                obj["y"] += delta
            elif key == arcade.key.DOWN:
                obj["y"] -= delta
            elif key == arcade.key.A:
                obj["width"] = max(10, obj["width"] - delta)
            elif key == arcade.key.D:
                obj["width"] = max(10, obj["width"] + delta)
            elif key == arcade.key.W:
                obj["height"] = max(5, obj["height"] - delta)
            elif key == arcade.key.S:
                obj["height"] = max(5, obj["height"] + delta)
            elif key == arcade.key.C:
                self._cycle_platform_color(obj)
        elif self.selected_type == "sprite":
            if key == arcade.key.LEFT:
                obj["x"] -= delta
            elif key == arcade.key.RIGHT:
                obj["x"] += delta
            elif key == arcade.key.UP:
                obj["y"] += delta
            elif key == arcade.key.DOWN:
                obj["y"] -= delta
            elif key == arcade.key.G:
                if obj["name"].upper() == "PORTAL":
                    current = obj.get("extra", "")
                    try:
                        val = int(current) if current else 1
                        new_val = val + 1
                        if new_val > len(LEVELS):
                            new_val = 1
                        obj["extra"] = str(new_val)
                    except ValueError:
                        obj["extra"] = "1"
                    self.status_msg = f"Portal goto: {obj['extra']}"
                    self.status_timer = 2.0

    def _cycle_platform_color(self, obj):
        colors = self.platform_colors
        current = obj["color"]
        idx = -1
        for i, (name, val) in enumerate(colors):
            if isinstance(current, tuple) and isinstance(val, tuple):
                if current == val:
                    idx = i
                    break
            elif hasattr(current, "__len__") and hasattr(val, "__len__"):
                if tuple(current[:3]) == tuple(val[:3]):
                    idx = i
                    break
        new_idx = (idx + 1) % len(colors)
        obj["color"] = colors[new_idx][1]
        self.status_msg = f"Color: {colors[new_idx][0]}"
        self.status_timer = 2.0

    def delete_selected(self):
        if self.selected_type == "platform":
            platforms = self.level.get("platforms", [])
            if 0 <= self.selected_index < len(platforms):
                del platforms[self.selected_index]
                self.selected_type = None
                self.selected_index = -1
                self.status_msg = "Piattaforma eliminata"
                self.status_timer = 2.0
        elif self.selected_type == "sprite":
            sprites = self.level.get("sprites", [])
            if 0 <= self.selected_index < len(sprites):
                del sprites[self.selected_index]
                self.selected_type = None
                self.selected_index = -1
                self.status_msg = "Sprite eliminato"
                self.status_timer = 2.0

    def save_level(self):
        try:
            save_levels_to_md(SETTINGS_MD_PATH, LEVELS)
            self.status_msg = "Salvato!"
            self.status_timer = 3.0
        except Exception as e:
            self.status_msg = f"Errore save: {e}"
            self.status_timer = 3.0

    def playtest(self):
        try:
            from .game_view import GameView
            game = GameView(window=self.window)
            self.window.show_view(game)
            game.setup_level(self.current_level_idx)
        except Exception as e:
            self.status_msg = f"Errore playtest: {e}"
            self.status_timer = 5.0

    def update(self, delta_time):
        if self.status_timer > 0:
            self.status_timer -= delta_time
