import pygame
import sys
import math

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    STATE_MENU, STATE_INTRO_VIDEO, STATE_STORY,
    STATE_BATTLE, STATE_SHOP, STATE_GAMEOVER, STATE_MINIGAME,
)
from entities  import Particle, FloatingText
from assets    import AssetsMixin
from story     import StoryMixin
from combat    import CombatMixin
from minigame  import MinigameMixin
from screens   import ScreensMixin


class GameEngine(AssetsMixin, StoryMixin, CombatMixin, MinigameMixin, ScreensMixin):

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Green Island - Un juego de rol por turnos")
        self.clock = pygame.time.Clock()

        # Fonts (Pixel Art)
        font_path         = "assets/fonts/PressStart2P-Regular.ttf"
        self.font_title    = pygame.font.Font(font_path, 28)
        self.font_subtitle = pygame.font.Font(font_path, 12)
        self.font_ui       = pygame.font.Font(font_path, 10)
        self.font_body     = pygame.font.Font(font_path, 10)
        self.font_small    = pygame.font.Font(font_path,  8)

        # Screen shake
        self.shake_intensity = 0
        self.shake_decay     = 0.9

        # Menu particles
        self.particles = [Particle() for _ in range(50)]

        # State machine
        self.state              = STATE_MENU
        self.current_scene_index = 1
        self.pre_shop_phase     = 0

        # Assets
        self.load_assets()

        # Player stats
        self.reset_player_stats()

        # Boss data
        self.boss_data = {
            1: {"name": "Guardián del Puerto",      "max_hp": 120, "hp": 120,
                "portrait": self.img_boss1,
                "desc": "Un misterioso seguidor de la sombra que vigila los muelles de la isla."},
            2: {"name": "Mago Magaxo",              "max_hp": 150, "hp": 150,
                "portrait": self.img_boss2,
                "desc": "Un poderoso hechicero que controla magia arcana inestable."},
            3: {"name": "Gólem de Piedra",          "max_hp": 200, "hp": 200,
                "portrait": self.img_boss3,
                "desc": "Un antiguo coloso de piedra insensible al daño directo básico."},
            4: {"name": "Caballero Oscuro (Espejo)","max_hp": 250, "hp": 250,
                "portrait": self.img_boss4,
                "desc": "Tu propia sombra corrupta. Copiará tus habilidades y mejoras."},
        }

        # Combat helpers
        self.floating_texts   = []
        self.flash_screen_red = 0
        self.battle_animations = []

        # Animation vars (Principles 1, 2, 5, 6, 7)
        self.player_attack_anim  = 0.0
        self.boss_attack_anim    = 0.0
        self.player_squash_timer = 0
        self.boss_squash_timer   = 0
        self.player_offset_y     = 0
        self.boss_offset_y       = 0

        # Mini-game vars
        self.minigame_active      = False
        self.minigame_projectiles = []
        self.minigame_player_x    = 0.0
        self.minigame_player_y    = 0.0
        self.minigame_hits        = 0
        self.minigame_timer       = 0
        self.minigame_duration    = 300   # 5 seconds @ 60 FPS
        self.minigame_base_damage = 0
        self.minigame_attack_name = ""
        self.minigame_boss_color  = (255, 255, 255)
        self.minigame_spawn_timer = 0
        self.minigame_pattern     = ""
        self.minigame_type            = "dodge"

        # Final-strike QTE vars
        self.final_strike_prompts      = []
        self.final_strike_current      = 0
        self.final_strike_score        = 0
        self.final_strike_max_score    = 0
        self.final_strike_result_flash = None
        self.final_strike_result_timer = 0
        self.final_strike_triggered    = False

        # Synthesized sounds (populated by synthesize_minigame_sounds)
        self.minigame_sfx_hit  = None
        self.minigame_sfx_warn = None
        self.minigame_bgm      = None
        self.synthesize_minigame_sounds()

    # ===================================================================== run
    def run(self):
        running = True

        self.play_music("intro_audio.mp3")

        dialogs         = []
        dialog_index    = 0
        dialog_progress = 0.0
        dialog_speed    = 0.5

        mouse_clicked = False

        while running:
            mouse_clicked     = False
            keys_just_pressed = set()
            keys_pressed      = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                if event.type == pygame.KEYDOWN:
                    keys_just_pressed.add(event.key)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.state == STATE_STORY:
                        current_dialog = dialogs[dialog_index]
                        if dialog_progress < len(current_dialog["text"]):
                            dialog_progress = float(len(current_dialog["text"]))
                        else:
                            dialog_index    += 1
                            dialog_progress  = 0.0
                            if dialog_index >= len(dialogs):
                                if hasattr(self, "pre_shop_phase") and self.pre_shop_phase > 0:
                                    self.play_music("assets/video/tienssound.mp3",
                                                    fade_ms=1000)
                                    self.state        = STATE_SHOP
                                    self.pre_shop_phase = 0
                                elif self.current_scene_index == 6:
                                    pygame.mixer.music.fadeout(1000)
                                    self.state = STATE_MENU
                                else:
                                    if self.current_scene_index in (2, 3, 4, 5):
                                        self.state = STATE_BATTLE
                                        self.init_battle()
                                    else:
                                        next_idx = self.current_scene_index + 1
                                        if next_idx == 2:
                                            self.play_music("hambiente-junga.mp3",
                                                            fade_ms=1500)
                                        self.state               = STATE_STORY
                                        self.current_scene_index = next_idx
                                        dialogs         = self.get_scene_story()
                                        dialog_index    = 0
                                        dialog_progress = 0.0

            # ================================================================ state handlers
            if self.state == STATE_MENU:
                is_start, is_exit = self.draw_menu_screen()
                if mouse_clicked:
                    if is_start:
                        self.state = STATE_INTRO_VIDEO
                    elif is_exit:
                        running = False

            elif self.state == STATE_INTRO_VIDEO:
                self.play_video("video introduccion.mp4", "intro_audio.mp3")
                self.screen.fill((0, 0, 0))
                llegada = self.font_subtitle.render("EL REINO DE OAKHAVEN...", True,
                                                    (241, 245, 249))
                self.screen.blit(llegada,
                                 (SCREEN_WIDTH // 2 - llegada.get_width() // 2,
                                  SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(2000)
                self.play_music("intro_audio.mp3", fade_ms=1000)
                self.state               = STATE_STORY
                self.current_scene_index = 1
                dialogs                  = self.get_scene_story()
                dialog_index             = 0
                dialog_progress          = 0.0

            elif self.state == STATE_STORY:
                current_dialog = dialogs[dialog_index]
                self.screen.blit(current_dialog["bg"], (0, 0))
                self.draw_dialog_box(
                    current_dialog["name"],
                    current_dialog["text"],
                    current_dialog["portrait"],
                    dialog_progress,
                )
                if dialog_progress < len(current_dialog["text"]):
                    dialog_progress += dialog_speed

            elif self.state == STATE_BATTLE:
                # --- arc animations (Principles 5, 6, 7)
                if self.player_attack_anim > 0:
                    self.player_attack_anim = min(1.0, self.player_attack_anim + 0.055)
                    t = self.player_attack_anim
                    self.player_offset_x = int(math.sin(math.pi * t) * 90)
                    self.player_offset_y = int(-math.sin(math.pi * t) * 22)
                    if t > 0.82:   # Follow-through (Principle 5)
                        self.player_offset_x += int(math.sin(math.pi * (t - 0.82) / 0.18) * -14)
                    if self.player_attack_anim >= 1.0:
                        self.player_attack_anim = 0.0
                        self.player_offset_x    = 0
                        self.player_offset_y    = 0
                elif self.player_offset_x > 0:
                    self.player_offset_x = max(0, self.player_offset_x - 4)

                if self.boss_attack_anim > 0:
                    self.boss_attack_anim = min(1.0, self.boss_attack_anim + 0.055)
                    t = self.boss_attack_anim
                    self.boss_offset_x = int(-math.sin(math.pi * t) * 90)
                    self.boss_offset_y = int(-math.sin(math.pi * t) * 22)
                    if t > 0.82:
                        self.boss_offset_x += int(math.sin(math.pi * (t - 0.82) / 0.18) * 14)
                    if self.boss_attack_anim >= 1.0:
                        self.boss_attack_anim = 0.0
                        self.boss_offset_x    = 0
                        self.boss_offset_y    = 0
                elif self.boss_offset_x < 0:
                    self.boss_offset_x = min(0, self.boss_offset_x + 4)

                self.draw_battle_screen()

                if self.battle_turn == "PLAYER" and self.battle_phase == "SELECT":
                    actions  = self.get_player_actions()
                    mx, my   = pygame.mouse.get_pos()

                    if mouse_clicked:
                        for idx, act in enumerate(actions):
                            btn_x = 615 + (idx % 2) * 190
                            btn_y = SCREEN_HEIGHT - 165 + (idx // 2) * 45
                            btn_rect = pygame.Rect(btn_x, btn_y, 180, 38)
                            if btn_rect.collidepoint(mx, my):
                                if self.execute_player_action(act):
                                    if self.current_boss["hp"] <= 0:
                                        if not self.final_strike_triggered:
                                            self.start_final_strike()
                                        else:
                                            self.add_combat_log(
                                                f"¡Has derrotado al {self.current_boss['name']}!")
                                            self.battle_phase = "VICTORY"
                                            self.battle_timer = pygame.time.get_ticks()
                                            self.battle_animations.append({
                                                "type": "death",
                                                "x": self.boss_visual_x + 128,
                                                "y": 220 + 128,
                                                "timer": 0, "max_frames": 30,
                                            })
                                    else:
                                        self.battle_turn  = "BOSS"
                                        self.battle_phase = "EXECUTE"
                                        self.battle_timer = pygame.time.get_ticks()
                                break

                elif self.battle_turn == "BOSS" and self.battle_phase == "EXECUTE":
                    if pygame.time.get_ticks() - self.battle_timer > 1500:
                        # Player bomb detonation
                        if self.combat_effects["bomb_timer"] > 0:
                            self.combat_effects["bomb_timer"] -= 1
                            if self.combat_effects["bomb_timer"] == 0:
                                damage = 75 if self.bomb_upgrade == "mega" else 55
                                self.current_boss["hp"] = max(0, self.current_boss["hp"] - damage)
                                self.floating_texts.append(
                                    FloatingText(f"-{damage}", SCREEN_WIDTH - 270, 200,
                                                 (239, 68, 68)))
                                self.shake_intensity = 20
                                self.play_sfx(self.sfx_magic)
                                self.add_combat_log(
                                    f"¡La bomba explota a los pies del jefe infligiendo {damage} de daño!")
                                self.battle_animations.append({
                                    "type": "hit",
                                    "x": self.boss_visual_x + 128,
                                    "y": 220 + 128,
                                    "timer": 0, "max_frames": 15,
                                })
                                if self.bomb_upgrade == "fire":
                                    self.combat_effects["burn_turns"] = 3

                        # Enemy burn damage
                        if self.combat_effects["burn_turns"] > 0:
                            self.combat_effects["burn_turns"] -= 1
                            self.current_boss["hp"] = max(0, self.current_boss["hp"] - 10)
                            self.floating_texts.append(
                                FloatingText("-10 Quemadura", SCREEN_WIDTH - 270, 220,
                                             (245, 158, 11)))
                            self.add_combat_log("El jefe sufre 10 de daño por quemaduras.")
                            self.battle_animations.append({
                                "type": "hit",
                                "x": self.boss_visual_x + 128,
                                "y": 220 + 128,
                                "timer": 0, "max_frames": 15,
                            })

                        if self.current_boss["hp"] <= 0:
                            if not self.final_strike_triggered:
                                self.add_combat_log(
                                    f"¡El {self.current_boss['name']} cae por la explosión!")
                                self.start_final_strike()
                            else:
                                self.add_combat_log(
                                    f"¡El {self.current_boss['name']} cae por la explosión!")
                                self.battle_phase = "VICTORY"
                                self.battle_timer = pygame.time.get_ticks()
                                self.battle_animations.append({
                                    "type": "death",
                                    "x": self.boss_visual_x + 128,
                                    "y": 220 + 128,
                                    "timer": 0, "max_frames": 30,
                                })
                        else:
                            self.execute_boss_turn()

                            # Mini-game takes over turn resolution if triggered
                            if self.state == STATE_MINIGAME:
                                pass
                            else:
                                if self.player_hp <= 0:
                                    self.add_combat_log("¡Has sido derrotado!")
                                    self.battle_phase = "DEFEAT"
                                    self.battle_timer = pygame.time.get_ticks()
                                    self.battle_animations.append({
                                        "type": "death",
                                        "x": self.player_visual_x + 128,
                                        "y": 220 + 128,
                                        "timer": 0, "max_frames": 30,
                                    })
                                else:
                                    self.battle_turn   = "PLAYER"
                                    self.battle_phase  = "SELECT"
                                    self.player_energy = min(self.player_max_energy,
                                                             self.player_energy + 1)
                                    self.add_combat_log("¡Tu turno! Recuperas +1 de Energía.")
                                    # Dark Knight burn tick
                                    if self.combat_effects["player_burn_turns"] > 0:
                                        self.combat_effects["player_burn_turns"] -= 1
                                        self.player_hp = max(0, self.player_hp - 10)
                                        self.floating_texts.append(
                                            FloatingText("-10 Quemadura", 270, 340,
                                                         (245, 158, 11)))
                                        self.add_combat_log(
                                            "¡La llama oscura te inflige 10 de daño!")
                                        if self.player_hp <= 0:
                                            self.battle_phase = "DEFEAT"
                                            self.battle_timer = pygame.time.get_ticks()

                elif self.battle_phase == "DEFEAT":
                    if pygame.time.get_ticks() - self.battle_timer > 2000:
                        self.state = STATE_GAMEOVER

                elif self.battle_phase == "VICTORY":
                    if pygame.time.get_ticks() - self.battle_timer > 2000:
                        if self.current_scene_index == 2:
                            self.has_improved_shield = True
                            self.state               = STATE_STORY
                            self.pre_shop_phase      = 1
                            dialogs                  = self.get_pre_shop_story(1)
                            dialog_index             = 0
                            dialog_progress          = 0.0
                        elif self.current_scene_index == 3:
                            self.has_teleport   = True
                            self.state          = STATE_STORY
                            self.pre_shop_phase = 2
                            dialogs             = self.get_pre_shop_story(2)
                            dialog_index        = 0
                            dialog_progress     = 0.0
                        elif self.current_scene_index == 4:
                            self.has_bombs      = True
                            self.state          = STATE_STORY
                            self.pre_shop_phase = 3
                            dialogs             = self.get_pre_shop_story(3)
                            dialog_index        = 0
                            dialog_progress     = 0.0
                        elif self.current_scene_index == 5:
                            self.play_music("intro_audio.mp3", fade_ms=2000)
                            self.state               = STATE_STORY
                            self.current_scene_index = 6
                            dialogs                  = self.get_scene_story()
                            dialog_index             = 0
                            dialog_progress          = 0.0

            elif self.state == STATE_SHOP:
                self.draw_shop_screen()
                if (mouse_clicked and hasattr(self, "hovered_card_index")
                        and self.hovered_card_index != -1):
                    choices        = self.get_shop_choices()
                    chosen_upgrade = choices[self.hovered_card_index]["id"]
                    self.select_shop_upgrade(chosen_upgrade)

                    next_scene = self.current_scene_index + 1
                    if next_scene in (3, 4):
                        self.play_music("assets/video/jungle_music.mp3", fade_ms=1500)
                    elif next_scene == 5:
                        self.play_music("hambiente-junga.mp3", fade_ms=1500)

                    self.state               = STATE_STORY
                    self.current_scene_index = next_scene
                    dialogs                  = self.get_scene_story()
                    dialog_index             = 0
                    dialog_progress          = 0.0

            elif self.state == STATE_GAMEOVER:
                is_retry, is_menu = self.draw_gameover_screen()
                if mouse_clicked:
                    if is_retry:
                        self.player_hp = 100
                        self.state     = STATE_BATTLE
                        self.init_battle()
                    elif is_menu:
                        self.reset_player_stats()
                        self.play_music("intro_audio.mp3", fade_ms=1500)
                        self.state = STATE_MENU

            elif self.state == STATE_MINIGAME:
                self.update_minigame(keys_pressed, keys_just_pressed)
                self.draw_minigame()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
