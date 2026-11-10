"""Costanti di gioco condivise tra tutti i moduli."""

import os
import re

import arcade
from PIL import Image

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Capitano Game"

# Calcola la cartella base del progetto (un livello sopra classes/)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE_FOLDER = os.path.join(_BASE_DIR, "sprites")
IMAGE_FOLDER = os.path.join(_BASE_DIR, "images")

WALK_SPEED = 1.5
RUN_SPEED = 3.0

GRAVITY = 0.6
JUMP_SPEED = 14.0
GROUND_Y = 250

IDLE_FPS = 6.0
WALK_FPS = 10.0
RUN_FPS = 15.0
JUMP_FPS = 10.0
CROUCH_FPS = 6.0
SHOOT_FPS = 12.0

JOY_DEADZONE = 0.15
JOY_RUN_THRESHOLD = 0.7
JOY_TRIGGER_THRESHOLD = 0.5

DEATH_FPS = 10.0

SHOOT_DURATION = 0.35
BULLET_SPEED = 10.0
BULLET_FPS = 15.0

EXPLOSION_FPS = 15.0

UFO_SPEED = 2.0
UFO_VERTICAL_SPEED = 3.0
UFO_SHOOT_INTERVAL = 2.0
UFO_BULLET_SPEED = 5.0

# XInput button masks
XINPUT_GAMEPAD_A = 0x1000
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200


def _resolve_sprite_path(folder, base_name):
    """Trova il file sprite per base_name con suffisso _RxC, o fallback a base_name.png."""
    pattern = re.compile(re.escape(base_name) + r"_\d+x\d+\.png$", re.IGNORECASE)
    try:
        files = os.listdir(folder)
    except FileNotFoundError:
        raise FileNotFoundError(f"Cartella sprite non trovata: {folder}")
    candidates = [f for f in files if pattern.match(f)]
    if len(candidates) == 1:
        return os.path.join(folder, candidates[0])
    if len(candidates) > 1:
        raise ValueError(f"Troppi file sprite per {base_name}: {candidates}")
    fallback = os.path.join(folder, base_name + ".png")
    if os.path.isfile(fallback):
        return fallback
    raise FileNotFoundError(f"Sprite non trovato: {base_name} in {folder}")


def load_sprite_sheet(path):
    """Carica uno sprite sheet deducendo righe e colonne dal nome file (_RxC).

    Se il nome non contiene il pattern _RxC, l'immagine viene trattata come
    sprite sheet con un singolo frame (fallback per retrocompatibilita').
    """
    basename = os.path.basename(path)
    name, _ = os.path.splitext(basename)
    m = re.search(r"_(\d+)x(\d+)$", name)
    if not m:
        # Fallback: immagine singola
        with Image.open(path) as img:
            total_w, total_h = img.size
        sheet = arcade.load_spritesheet(path)
        return sheet.get_texture_grid(size=(total_w, total_h), columns=1, count=1)
    rows = int(m.group(1))
    cols = int(m.group(2))
    with Image.open(path) as img:
        total_w, total_h = img.size
    frame_w = total_w // cols
    frame_h = total_h // rows
    count = rows * cols
    sheet = arcade.load_spritesheet(path)
    return sheet.get_texture_grid(size=(frame_w, frame_h), columns=cols, count=count)


def _read_settings_md():
    """Legge settings.md dalla root del progetto e restituisce il testo."""
    md_path = os.path.join(_BASE_DIR, "settings.md")
    with open(md_path, "r", encoding="utf-8-sig") as f:
        return f.read()


def _load_levels(text):
    """Estrae la lista LEVELS dalle sezioni ## level di settings.md."""
    levels = []
    parts = re.split(r"(?:\n|^)##\s*level\s*\n", text, flags=re.IGNORECASE)
    for i in range(1, len(parts)):
        section = parts[i]
        level = {}

        in_platform_section = False
        for raw_line in section.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if re.match(r"^#+\s*Piattaforme\s*$", line, re.IGNORECASE):
                in_platform_section = True
                continue
            if in_platform_section and re.match(r"^#+", line):
                in_platform_section = False
                continue

            if in_platform_section or line.upper().startswith("PIATTAFORMA"):
                m = re.match(r"PIATTAFORMA\s+(.+)", line, re.IGNORECASE)
                if m:
                    parts_pf = [p.strip() for p in m.group(1).split(",")]
                    data = {}
                    for part in parts_pf:
                        if ":" in part:
                            key, val = part.split(":", 1)
                            data[key.strip().lower()] = val.strip()
                    if all(k in data for k in ("x", "y", "width", "height", "color")):
                        if "platforms" not in level:
                            level["platforms"] = []
                        color_name = data["color"].upper()
                        if color_name == "TRANSPARENT":
                            color = (0, 0, 0, 0)
                        else:
                            color = getattr(arcade.color, color_name, arcade.color.GRAY)
                        level["platforms"].append({
                            "x": float(data["x"]),
                            "y": float(data["y"]),
                            "width": float(data["width"]),
                            "height": float(data["height"]),
                            "color": color,
                        })
                continue

            if line.upper().startswith("SPRITE"):
                m = re.match(r"SPRITE\s+(.+)", line, re.IGNORECASE)
                if m:
                    parts_sp = [p.strip() for p in m.group(1).split(",")]
                    data = {}
                    for part in parts_sp:
                        if ":" in part:
                            key, val = part.split(":", 1)
                            data[key.strip().lower()] = val.strip()
                    if "name" in data and "x" in data and "y" in data:
                        if "sprites" not in level:
                            level["sprites"] = []
                        sprite = {
                            "name": data["name"],
                            "x": float(data["x"]),
                            "y": float(data["y"]),
                        }
                        if "extra" in data:
                            sprite["extra"] = data["extra"]
                        if "goto" in data:
                            sprite["extra"] = data["goto"]
                        level["sprites"].append(sprite)
                continue

            m = re.match(r"([A-Za-z][A-Za-z0-9_\s]*)\s*[:=]\s*(.+)", line)
            if m:
                key = m.group(1).strip().lower()
                val = m.group(2).strip()
                if key == "id":
                    level["id"] = int(val)
                elif key in ("larghezza", "width", "lenght", "length"):
                    level["width"] = int(val)
                elif key in ("altezza", "height"):
                    level["height"] = int(val)
                elif key == "backgroundtype":
                    level["backgroundtype"] = val
                elif key == "backgroundimage":
                    level["backgroundimage"] = val
                elif key == "patternfile":
                    level["patternfile"] = val
                elif re.match(r"parallaximage\s*\d*", key):
                    if "parallaximages" not in level:
                        level["parallaximages"] = []
                    level["parallaximages"].append(val)

        if "id" in level:
            level.setdefault("name", f"Livello {level['id']}")
            levels.append(level)
    return levels

def _load_sprites(text):
    """Estrae le specifiche degli sprite dalle sezioni ## NOME prima di '# Levels settings'."""
    sprites = {}
    # Considera solo il testo prima della sezione livelli
    levels_header = re.search(r"^#\s*Levels\s+settings\s*$", text, re.MULTILINE | re.IGNORECASE)
    if levels_header:
        section_text = text[:levels_header.start()]
    else:
        section_text = text
    # Splitta per sottosezioni ## NOME
    parts = re.split(r"\n##\s*([A-Za-z][\w ]*)\s*\n", "\n" + section_text)
    for i in range(1, len(parts) - 1, 2):
        name = parts[i].strip().lower()
        body = parts[i + 1]
        props = {}
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            mm = re.match(r"([A-Za-z][A-Za-z0-9_\.\s]*)\s*[:=]\s*(.+)", line)
            if mm:
                key = mm.group(1).strip().lower().replace(".", "_")
                props[key] = mm.group(2).strip()
        sprites[name] = props
    return sprites


_SETTINGS_MD = _read_settings_md()

LEVELS = _load_levels(_SETTINGS_MD)
SPRITES = _load_sprites(_SETTINGS_MD)

SETTINGS_MD_PATH = os.path.join(_BASE_DIR, "settings.md")


def reload_game_config():
    """Rilegge settings.md e aggiorna LEVELS, SPRITES e le costanti derivate.

    LEVELS e SPRITES vengono aggiornati in-place (mutazione della lista/diz)
    cosi' che tutti i moduli che li hanno importati vedano le modifiche.
    """
    global WALK_SPEED, RUN_SPEED, UFO_SPEED, UFO_VERTICAL_SPEED, BULLET_SPEED, UFO_SHOOT_INTERVAL, UFO_BULLET_SPEED
    text = _read_settings_md()
    new_levels = _load_levels(text)
    if new_levels:
        LEVELS[:] = new_levels
    SPRITES.clear()
    SPRITES.update(_load_sprites(text))
    cap = SPRITES.get("capitano", {})
    if "walk_speed" in cap:
        WALK_SPEED = float(cap["walk_speed"])
    if "run_speed" in cap:
        RUN_SPEED = float(cap["run_speed"])
    ufo = SPRITES.get("ufo", {})
    if "speed" in ufo:
        UFO_SPEED = float(ufo["speed"])
    if "vertical_speed" in ufo:
        UFO_VERTICAL_SPEED = float(ufo["vertical_speed"])
    if "shoot_interval" in ufo:
        UFO_SHOOT_INTERVAL = float(ufo["shoot_interval"])
    if "bullet_speed" in ufo:
        UFO_BULLET_SPEED = float(ufo["bullet_speed"])
    bullet_plasma = SPRITES.get("bullet_plasma", {})
    if "speed" in bullet_plasma:
        BULLET_SPEED = float(bullet_plasma["speed"])


# Le specifiche degli sprite caricate da settings.md sovrascrivono i default
reload_game_config()



# ---------------------------------------------------------------------------
# Salvataggio settings.md
# ---------------------------------------------------------------------------

_COLOR_NAME_MAP = {
    arcade.color.TRANSPARENT_BLACK: "TRANSPARENT",
    arcade.color.RED: "RED",
    arcade.color.GREEN: "GREEN",
    arcade.color.BLUE: "BLUE",
    arcade.color.YELLOW: "YELLOW",
    arcade.color.GRAY: "GRAY",
    arcade.color.BLACK: "BLACK",
    arcade.color.WHITE: "WHITE",
    arcade.color.ORANGE: "ORANGE",
    arcade.color.PURPLE: "PURPLE",
    arcade.color.PINK: "PINK",
    arcade.color.BROWN: "BROWN",
    arcade.color.CYAN: "CYAN",
    arcade.color.MAGENTA: "MAGENTA",
}


def _color_to_string(color):
    """Converte un colore Arcade/tuple in stringa per settings.md."""
    if isinstance(color, tuple):
        if len(color) == 4 and color[3] == 0:
            return "TRANSPARENT"
        for key, name in _COLOR_NAME_MAP.items():
            if isinstance(key, tuple) and len(key) >= 3:
                if tuple(key[:3]) == tuple(color[:3]):
                    return name
        # fallback: cerca in arcade.color
        for attr in dir(arcade.color):
            val = getattr(arcade.color, attr)
            if isinstance(val, (tuple, list)) and len(val) >= 3:
                if tuple(val[:3]) == tuple(color[:3]):
                    return attr
        return f"RGB({color[0]},{color[1]},{color[2]})"

    # Oggetto Color (arcade 3.x)
    if hasattr(color, "r") and hasattr(color, "g") and hasattr(color, "b"):
        rgb = (color.r, color.g, color.b)
        for key, name in _COLOR_NAME_MAP.items():
            if isinstance(key, tuple) and len(key) >= 3:
                if tuple(key[:3]) == rgb:
                    return name
        for attr in dir(arcade.color):
            val = getattr(arcade.color, attr)
            if isinstance(val, (tuple, list)) and len(val) >= 3:
                if tuple(val[:3]) == rgb:
                    return attr
        return f"RGB({color.r},{color.g},{color.b})"

    return "GRAY"


def save_levels_to_md(path, levels):
    """Scrive settings.md preservando la sezione '# Sprites settings' e rigenerando i livelli."""
    header = ""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            content = f.read()
        match = re.search(r"(?:\n|^)# Levels settings\s*\n", content, re.IGNORECASE)
        if match:
            header = content[:match.start()]
            if not header.endswith("\n"):
                header += "\n"
        else:
            header = content
            if not header.endswith("\n"):
                header += "\n"

    lines = []
    lines.append("# Levels settings\n")

    for level in levels:
        lines.append("\n## level\n")
        lines.append(f"id={level.get('id', 1)}\n")
        lines.append(f"lenght: {level.get('width', 1920)}\n")
        lines.append(f"height: {level.get('height', 1080)}\n")
        lines.append(f"backgroundtype: {level.get('backgroundtype', 'parallax')}\n")
        if level.get("backgroundimage"):
            lines.append(f"backgroundimage: {level['backgroundimage']}\n")
        for i, img in enumerate(level.get("parallaximages", []), 1):
            lines.append(f"parallaximage {i}: {img}\n")

        lines.append("\n")
        for sprite in level.get("sprites", []):
            extra = sprite.get("extra", "")
            name = sprite.get("name", "UNKNOWN")
            x = sprite.get("x", 0)
            y = sprite.get("y", 0)
            if extra:
                lines.append(f"SPRITE name:{name}, x:{x}, y:{y}, goto:{extra}\n")
            else:
                lines.append(f"SPRITE name:{name}, x:{x}, y:{y}\n")

        lines.append("\n")
        for pf in level.get("platforms", []):
            color_str = _color_to_string(pf.get("color", arcade.color.GRAY))
            lines.append(
                f"PIATTAFORMA x:{pf['x']}, y:{pf['y']}, "
                f"width:{pf['width']}, height:{pf['height']}, color:{color_str}\n"
            )

    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(lines)
