"""Vista principale del gioco."""

import os
import re
import arcade
from pyglet.math import Mat4, Vec3

from . import config
from .config import (
    LEVELS,
    WINDOW_WIDTH, WINDOW_HEIGHT, GROUND_Y,
    JOY_DEADZONE, JOY_RUN_THRESHOLD,
)
from .xinput_reader import XInputReader
from .background_parallax import Background_Parallax
from .capitano import Capitano
from .ufo import UFO
from .explosion import Explosion
from .portal import Portal
from .piattaforma import Piattaforma


class GameView(arcade.View):
    """Vista principale del gioco."""

    def __init__(self, window=None):
        super().__init__()
        self.background_color = arcade.color.AMAZON
        self._window_ref = window

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ufo_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()

        # Esplosioni
        self.explosion_list = arcade.SpriteList()

        # Personaggio
        self.player = Capitano(center_x=WINDOW_WIDTH / 2, center_y=GROUND_Y)
        self.player_list.append(self.player)

        # Livello corrente e camera
        self.current_level_index = 0
        self.identity_matrix = Mat4()
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Sfondo (parallax o immagine fissa)
        self.background = None
        self.background_image_texture = None

        # UFO nemici e portali (creati da setup_level)

        # Imposta il livello iniziale (carica sfondo, UFO e portali)
        self.setup_level(0)

        # FPS tracking
        self._fps = 0.0
        self._fps_accum = 0.0
        self._fps_frames = 0

        # Input
        self.key_left = False
        self.key_right = False
        self.key_run = False
        self.key_jump = False
        self.key_crouch = False
        self.key_shoot = False

        self.xinput = XInputReader()

        # Hot-reload di settings.md
        self._reload_timer = 0.0
        try:
            self._game_md_mtime = os.path.getmtime(config.SETTINGS_MD_PATH)
        except OSError:
            self._game_md_mtime = 0.0

    def _load_background_for_level(self, index):
        """Carica lo sfondo appropriato per il livello indicato."""
        level = LEVELS[index]
        bg_type = level.get("backgroundtype", "parallax")

        if bg_type == "parallax":
            images = level.get("parallaximages", [])
            self.background = Background_Parallax(image_paths=images)
            self.background_image_texture = None
        elif bg_type == "image":
            self.background = None
            path = level.get("backgroundimage", "")
            if path:
                if not os.path.isabs(path):
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    path = os.path.join(base_dir, path)
                self.background_image_texture = arcade.load_texture(path)
            else:
                self.background_image_texture = None
        else:
            # Fallback a vuoto
            self.background = Background_Parallax(image_paths=[])
            self.background_image_texture = None

    def _handle_player_platforms(self, player_prev_y: float):
        """Gestisce atterraggio e caduta del capitano sulle piattaforme.

        Il capitano atterra su una piattaforma solo se ne attraversa la
        superficie superiore dall'alto verso il basso. Non è richiesta una
        sovrapposizione completa: basta che il piede del capitano passi dalla
        superficie nel frame corrente.
        """
        if not self.platform_list:
            return

        player = self.player
        player_half_width = abs(player.width) / 2
        player_left = player.center_x - player_half_width
        player_right = player.center_x + player_half_width
        player_bottom = player.center_y - player.height / 2
        prev_player_bottom = player_prev_y - player.height / 2
        threshold = 2.0

        landing_platform = None
        landing_top = None

        for platform in self.platform_list:
            platform_half_width = platform.width / 2
            platform_left = platform.center_x - platform_half_width
            platform_right = platform.center_x + platform_half_width
            platform_top = platform.center_y + platform.height / 2

            # Sovrapposizione orizzontale
            if player_right <= platform_left or player_left >= platform_right:
                continue

            # Atterraggio: il piede del capitano ha attraversato il top della
            # piattaforma dall'alto verso il basso (o è appoggiato sopra).
            if prev_player_bottom >= platform_top - threshold and player_bottom <= platform_top + threshold:
                if landing_top is None or platform_top > landing_top:
                    landing_platform = platform
                    landing_top = platform_top

        if landing_platform is not None:
            player.center_y = landing_top + player.height / 2
            player.change_y = 0.0
            player.on_ground = True
        else:
            player.on_ground = False

    def _parse_portal_target(self, extra):
        """Converte una stringa 'LEVEL N' o 'N' nell'indice 0-based del livello target."""
        if not extra:
            return None
        m = re.match(r"(?:LEVEL\s+)?(\d+)", str(extra), re.IGNORECASE)
        if m:
            return int(m.group(1)) - 1
        return None

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.close()
            return
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right = True
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.key_jump = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.key_crouch = True
        elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.key_run = True
        elif key == arcade.key.Z or key == arcade.key.X:
            self.key_shoot = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right = False
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.key_jump = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.key_crouch = False
        elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.key_run = False
        elif key == arcade.key.Z or key == arcade.key.X:
            self.key_shoot = False

    def on_draw(self):
        self.clear()

        # Calcola camera per il livello corrente
        current_level = LEVELS[self.current_level_index]
        level_width = current_level.get("width", WINDOW_WIDTH)
        level_height = current_level.get("height", WINDOW_HEIGHT)
        max_camera_x = max(0, level_width - WINDOW_WIDTH)
        self.camera_x = max(0, min(self.player.center_x - WINDOW_WIDTH / 2, max_camera_x))
        max_camera_y = max(0, level_height - WINDOW_HEIGHT)
        self.camera_y = max(0, min(self.player.center_y - WINDOW_HEIGHT / 2, max_camera_y))

        # Disegna sfondo (fisso sullo schermo, non scrolla con la camera verticale)
        if self.background_image_texture:
            # Sfondo immagine fissa con tiling orizzontale
            tex = self.background_image_texture
            w = tex.width
            total_offset = self.camera_x % w
            start_x = total_offset - w
            x = start_x
            while x < WINDOW_WIDTH:
                arcade.draw_texture_rect(
                    tex,
                    arcade.LBWH(x, 0, w, WINDOW_HEIGHT),
                )
                x += w
        elif self.background:
            self.background.draw(self.camera_x)

        # Applica view matrix per il mondo di gioco (scroll orizzontale e verticale)
        self.window.ctx.view_matrix = Mat4.from_translation(Vec3(-self.camera_x, -self.camera_y, 0))

        self.platform_list.draw()
        self.player_list.draw()
        self.portal_list.draw()
        self.bullet_list.draw()
        self.ufo_list.draw()
        self.explosion_list.draw()

        # Reset view matrix per UI (HUD)
        self.window.ctx.view_matrix = self.identity_matrix

        # FPS counter e info livello in basso a sinistra con sfondo nero
        info_text = f"FPS: {self._fps:.0f}  |  LIV: {self.current_level_index + 1}  |  LAR: {level_width}  |  ALT: {level_height}  |  POS: {int(self.player.center_x)},{int(self.player.center_y)}"
        arcade.draw_lbwh_rectangle_filled(
            5, 5, 500, 24,
            arcade.color.BLACK,
        )
        arcade.draw_text(
            info_text,
            x=10,
            y=10,
            color=arcade.color.YELLOW,
            font_size=14,
            bold=True,
        )

    def on_update(self, delta_time: float):
        # Calcola FPS manualmente
        self._fps_accum += delta_time
        self._fps_frames += 1
        if self._fps_accum >= 0.5:
            self._fps = self._fps_frames / self._fps_accum
            self._fps_accum = 0.0
            self._fps_frames = 0

        # Hot-reload di settings.md (controlla una volta al secondo)
        self._reload_timer += delta_time
        if self._reload_timer >= 1.0:
            self._reload_timer = 0.0
            try:
                mtime = os.path.getmtime(config.SETTINGS_MD_PATH)
                if mtime != self._game_md_mtime:
                    self._game_md_mtime = mtime
                    config.reload_game_config()
            except OSError:
                pass

        # --- Leggi input dal controller ---
        joy_x = 0.0
        joy_crouch = False
        joy_jump = False
        joy_shoot = False
        joy_run = False

        if self.xinput.is_connected():
            jx = self.xinput.get_left_x()
            jy = self.xinput.get_left_y()
            if abs(jx) > JOY_DEADZONE:
                joy_x = jx
            if jy < -JOY_DEADZONE:
                joy_crouch = True
            if self.xinput.is_button_pressed(button_mask=0x1000):
                joy_jump = True
            if self.xinput.is_button_pressed(button_mask=config.XINPUT_GAMEPAD_RIGHT_SHOULDER):
                joy_shoot = True
            if abs(jx) > JOY_RUN_THRESHOLD:
                joy_run = True

        if not self.player.is_dead:
            # --- Calcola movimento ---
            move_left = self.key_left or joy_x < -JOY_DEADZONE
            move_right = self.key_right or joy_x > JOY_DEADZONE
            run = self.key_run or joy_run
            crouch = self.key_crouch or joy_crouch

            speed = config.RUN_SPEED if run else config.WALK_SPEED
            dx = 0.0

            if move_left:
                dx = -speed
                self.player.set_facing(False)
            elif move_right:
                dx = speed
                self.player.set_facing(True)

            self.player.change_x = dx

            # --- Salto ---
            if self.key_jump or joy_jump:
                if self.player.on_ground:
                    self.player.jump()
                    self.key_jump = False

            # --- Sparo ---
            if (self.key_shoot or joy_shoot) and not self.player.is_shooting:
                self.player.start_shoot()
                bullet = self.player.create_bullet()
                # Il bullet resta alla quota del capitano: per colpire l'UFO
                # il giocatore deve saltare fino all'altezza giusta.
                self.bullet_list.append(bullet)
                self.key_shoot = False

            # --- Aggiorna l'azione animata del capitano (idle/walk/run/jump/crouch + shot) ---
            suffix = "_shot" if self.player.is_shooting else ""
            if crouch:
                self.player.set_action(f"crouch{suffix}")
            elif not self.player.on_ground:
                self.player.set_action(f"jump{suffix}")
            elif move_left or move_right:
                self.player.set_action(f"{'run' if run else 'walk'}{suffix}")
            else:
                self.player.set_action(f"idle{suffix}")

        # Aggiorna fisica e animazioni
        self.portal_list.update(delta_time)
        self.bullet_list.update(delta_time)

        # Salva la Y precedente del capitano per la collisione con le piattaforme
        player_prev_y = self.player.center_y
        self.player_list.update(delta_time)
        if not self.player.is_dead:
            self._handle_player_platforms(player_prev_y)

        if self.player.death_done:
            self.setup_level(self.current_level_index)
            return

        self.explosion_list.update(delta_time)
        self.platform_list.update(delta_time)
        for ufo in self.ufo_list:
            ufo.ai(self.player)
            enemy_bullet = ufo.maybe_shoot(self.player, delta_time)
            if enemy_bullet:
                self.bullet_list.append(enemy_bullet)
        self.ufo_list.update(delta_time)

        # Collisioni bullet del capitano vs UFO
        for bullet in list(self.bullet_list):
            if not bullet.is_enemy:
                hit_list = arcade.check_for_collision_with_list(bullet, self.ufo_list)
                for ufo in hit_list:
                    explosion = Explosion(ufo.center_x, ufo.center_y, scale=1.0)
                    self.explosion_list.append(explosion)
                    ufo.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()
                    break

        # Rimuove i bullet fuori dai limiti del livello (coordinate mondo)
        level_width = LEVELS[self.current_level_index].get("width", WINDOW_WIDTH)
        level_height = LEVELS[self.current_level_index].get("height", WINDOW_HEIGHT)
        for bullet in list(self.bullet_list):
            if (bullet.center_x < 0 or bullet.center_x > level_width
                    or bullet.center_y < 0 or bullet.center_y > level_height):
                bullet.remove_from_sprite_lists()

        # Collisioni capitano vs bullet nemici
        for bullet in list(self.bullet_list):
            if bullet.is_enemy:
                if arcade.check_for_collision(self.player, bullet):
                    bullet.remove_from_sprite_lists()
                    if not self.player.is_dead:
                        self.player.die()

        # Collisione corpo a corpo con gli UFO
        for ufo in list(self.ufo_list):
            if arcade.check_for_collision(self.player, ufo):
                if not self.player.is_dead:
                    self.player.die()
                break

        # Collisione capitano vs portali
        for portal in list(self.portal_list):
            if arcade.check_for_collision(self.player, portal):
                if portal.target_level is not None and 0 <= portal.target_level < len(LEVELS):
                    self.setup_level(portal.target_level)
                break

        # Hot-reload di settings.md
        self._reload_timer += delta_time
        if self._reload_timer >= 1.0:
            self._reload_timer = 0.0
            try:
                mtime = os.path.getmtime(config.SETTINGS_MD_PATH)
                if mtime != self._game_md_mtime:
                    self._game_md_mtime = mtime
                    config.reload_game_config()
                    self._load_background_for_level(self.current_level_index)
            except OSError:
                pass

        # Blocca il capitano ai bordi del livello corrente
        half_width = abs(self.player.width) / 2
        left_bound = half_width
        right_bound = level_width - half_width
        self.player.center_x = max(left_bound, min(self.player.center_x, right_bound))

        # Limite verticale: non uscire dal livello (sopra) e non cadere sotto il terreno
        half_height = abs(self.player.height) / 2
        top_bound = level_height - half_height
        self.player.center_y = min(self.player.center_y, top_bound)
        if self.player.ground_y is not None:
            self.player.center_y = max(self.player.center_y, self.player.ground_y + half_height)

    def setup_level(self, index, start_x=None, start_y=None):
        """Configura lo scenario per il livello indicato (o ricarica quello corrente)."""
        self.current_level_index = index
        level = LEVELS[index]
        level_width = level.get("width", WINDOW_WIDTH)

        # Svuota le liste nemiche e piattaforme prima di ricrearle dal settings.md
        self.ufo_list.clear()
        self.portal_list.clear()
        self.platform_list.clear()

        level_height = level.get("height", WINDOW_HEIGHT)

        # Crea le piattaforme definite in settings.md
        for platform_def in level.get("platforms", []):
            platform = Piattaforma(
                x=platform_def["x"],
                y=platform_def["y"],
                width=platform_def["width"],
                height=platform_def["height"],
                color=platform_def["color"],
            )
            self.platform_list.append(platform)

        # Posiziona gli sprite definiti in settings.md per questo livello
        sprites = level.get("sprites", [])
        player_set = False
        for sprite_def in sprites:
            name = sprite_def["name"].upper()
            x = sprite_def["x"]
            y = sprite_def["y"]
            if name == "CAPITANO":
                self.player.center_x = x
                self.player.center_y = y + self.player.height / 2
                self.player.ground_y = y
                self.player.change_y = 0.0
                self.player.on_ground = True
                player_set = True
            elif name == "UFO":
                ufo = UFO(start_x=x, start_y=y, bounds_width=level_width, bounds_height=level_height)
                self.ufo_list.append(ufo)
            elif name == "PORTAL":
                target = self._parse_portal_target(sprite_def.get("extra"))
                portal = Portal(center_x=x, center_y=y, target_level=target)
                self.portal_list.append(portal)

        # Fallback se mancano definizioni
        if not player_set:
            if start_x is None:
                start_x = WINDOW_WIDTH / 2
            if start_y is None:
                start_y = GROUND_Y
            self.player.center_x = start_x
            self.player.center_y = start_y
            self.player.ground_y = start_y
            self.player.change_y = 0.0
            self.player.on_ground = True

        self.player.change_x = 0.0

        self._load_background_for_level(index)

        # Fallback UFO se non definito nel livello
        if not self.ufo_list:
            fallback_y = min(WINDOW_HEIGHT - 200, level_height - 200)
            self.ufo_list.append(UFO(start_x=WINDOW_WIDTH / 2, start_y=fallback_y, bounds_width=level_width, bounds_height=level_height))

        # Pulisce proiettili ed esplosioni residui
        self.bullet_list.clear()
        self.explosion_list.clear()
