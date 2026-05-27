import pygame
import os
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, MUSIC_VOLUME, SFX_VOLUME,
                       COLOR_PRIMARY, COLOR_TEXT, COLOR_WARNING)


class AssetsMixin:

    # ------------------------------------------------------------------ audio
    def load_sound(self, path):
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(SFX_VOLUME)
            return snd
        except Exception as e:
            print(f"[SFX] No se pudo cargar '{path}': {e}")
            return None

    def play_sfx(self, sound):
        if sound:
            sound.play()

    def play_music(self, track, loops=-1, fade_ms=800):
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
        except Exception as e:
            print(f"[Música] No se pudo cargar '{track}': {e}")

    # --------------------------------------------------------------- loaders
    def load_background_or_gradient(self, path, color_top, color_bottom):
        try:
            if os.path.exists(path):
                img     = pygame.image.load(path).convert()
                low_res = pygame.transform.scale(img, (256, 192))
                return pygame.transform.scale(low_res, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error cargando imagen {path}: {e}")

        surf        = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        band_height = 8
        for y in range(0, SCREEN_HEIGHT, band_height):
            ratio = y / SCREEN_HEIGHT
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.rect(surf, (r, g, b), (0, y, SCREEN_WIDTH, band_height))
        return surf

    def load_portrait_or_fallback(self, path, name_text):
        try:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (256, 256))
        except Exception as e:
            print(f"Error cargando retrato {path}: {e}")

        surf = pygame.Surface((256, 256), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 41, 59), (0, 0, 256, 256))
        pygame.draw.rect(surf, COLOR_PRIMARY, (0, 0, 256, 256), width=4)
        font      = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 36)
        char      = name_text[0] if name_text else "?"
        text_surf = font.render(char, True, COLOR_TEXT)
        surf.blit(text_surf, (128 - text_surf.get_width() // 2,
                               128 - text_surf.get_height() // 2))
        return surf

    def load_image_or_fallback(self, path, size=(96, 96)):
        try:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, size)
        except Exception as e:
            print(f"Error cargando imagen {path}: {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_WARNING, (0, 0, size[0], size[1]), width=2)
        return surf

    # --------------------------------------------------------- button builder
    def create_menu_buttons(self):
        def make_button(w, h, label, icon_type, base_color, glow_color):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 0, 0, 120), (4, 4, w, h))
            for row in range(0, h - 4, 4):
                ratio = row / (h - 4)
                r = int(base_color[0] * (1 - ratio * 0.4))
                g = int(base_color[1] * (1 - ratio * 0.4))
                b = int(base_color[2] * (1 - ratio * 0.4))
                pygame.draw.rect(surf, (r, g, b), (0, row, w - 4, 4))
            pygame.draw.rect(surf, glow_color, (0, 0, w - 4, h - 4), width=4)
            pygame.draw.rect(surf, (255, 255, 255, 60), (4, 4, w - 12, h - 12), width=2)
            for cx, cy in [(0, 0), (w - 12, 0), (0, h - 12), (w - 12, h - 12)]:
                pygame.draw.rect(surf, (0, 0, 0), (cx, cy, 12, 12))
                pygame.draw.rect(surf, glow_color, (cx + 2, cy + 2, 8, 8))
                pygame.draw.rect(surf, (255, 255, 255), (cx + 4, cy + 4, 4, 4))
            icon_x, icon_y = 16, h // 2 - 10
            if icon_type == "sword":
                blade = [(icon_x+8, icon_y), (icon_x+10, icon_y+2),
                         (icon_x+8, icon_y+12), (icon_x+6, icon_y+2)]
                pygame.draw.polygon(surf, (200, 220, 255), blade)
                pygame.draw.rect(surf, (200, 160, 30), (icon_x+3, icon_y+12, 10, 3))
                pygame.draw.rect(surf, (160, 100, 20), (icon_x+6, icon_y+15, 4, 5))
            elif icon_type == "skull":
                sg = [[0,1,1,1,0],[1,1,1,1,1],[1,2,1,2,1],
                      [1,1,1,1,1],[0,1,0,1,0]]
                ps = 4
                for ri, row in enumerate(sg):
                    for ci, v in enumerate(row):
                        c = (220,220,220) if v==1 else ((20,20,20) if v==2 else None)
                        if c:
                            pygame.draw.rect(surf, c,
                                             (icon_x + ci*ps, icon_y + ri*ps, ps, ps))
            font   = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 10)
            txt    = font.render(label, True, (255, 255, 255))
            tx     = (w - 4) // 2 - txt.get_width() // 2 + 10
            ty     = (h - 4) // 2 - txt.get_height() // 2
            shadow = font.render(label, True, (0, 0, 0))
            surf.blit(shadow, (tx + 2, ty + 2))
            surf.blit(txt, (tx, ty))
            return surf

        btn_w, btn_h = 320, 60
        self.img_btn_play_normal = make_button(btn_w, btn_h, "INICIAR JUEGO", "sword",
                                               (16, 100, 70), (52, 211, 153))
        self.img_btn_play_hover  = make_button(btn_w, btn_h, "INICIAR JUEGO", "sword",
                                               (30, 180, 110), (255, 255, 255))
        self.img_btn_exit_normal = make_button(btn_w, btn_h, "SALIR", "skull",
                                               (100, 20, 20), (239, 68, 68))
        self.img_btn_exit_hover  = make_button(btn_w, btn_h, "SALIR", "skull",
                                               (180, 30, 30), (255, 255, 255))

    def create_dialog_box_image(self):
        w, h = SCREEN_WIDTH - 40, 200
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((15, 23, 42, 220))
        pygame.draw.rect(surf, (217, 119, 6), (0, 0, w, h), width=4)
        pygame.draw.rect(surf, (251, 191, 36), (6, 6, w - 12, h - 12), width=2)
        corners = [(0, 0), (w - 16, 0), (0, h - 16), (w - 16, h - 16)]
        for cx, cy in corners:
            pygame.draw.rect(surf, (180, 83, 9), (cx, cy, 16, 16))
            pygame.draw.rect(surf, (251, 191, 36), (cx + 2, cy + 2, 12, 12))
            pygame.draw.rect(surf, (255, 255, 255), (cx + 4, cy + 4, 4, 4))
        os.makedirs("assets/images", exist_ok=True)
        pygame.image.save(surf, "assets/images/dialog_box.png")

    def load_assets(self):
        os.makedirs("assets/images", exist_ok=True)
        self.create_menu_buttons()
        self.create_dialog_box_image()
        self.img_dialog_box = pygame.image.load(
            "assets/images/dialog_box.png").convert_alpha()

        self.img_knight   = self.load_portrait_or_fallback(
            "assets/images/knight_portrait.png", "Caballero")
        self.img_boss1    = self.load_portrait_or_fallback(
            "assets/images/boss1.png", "Guardián")
        self.img_boss2    = self.load_portrait_or_fallback(
            "assets/images/boss2.png", "Magaxo")
        self.img_boss3    = self.load_portrait_or_fallback(
            "assets/images/boss3.png", "Gólem")
        self.img_boss4    = self.load_portrait_or_fallback(
            "assets/images/boss4.png", "Caballero Oscuro")
        self.img_merchant = self.load_portrait_or_fallback(
            "assets/images/merchant.png", "Mercader")
        self.img_king     = self.load_portrait_or_fallback(
            "assets/images/king_portrait.png", "Rey")

        self.shop_item_images = {
            "spiked":       self.load_image_or_fallback(
                "assets/images/item_spiked_shield.png", (96, 96)),
            "rejuvenating": self.load_image_or_fallback(
                "assets/images/item_rejuvenating_shield.png", (96, 96)),
            "counter":      self.load_image_or_fallback(
                "assets/images/item_counter_teleport.png", (96, 96)),
            "recharge":     self.load_image_or_fallback(
                "assets/images/item_recharge_teleport.png", (96, 96)),
            "fire":         self.load_image_or_fallback(
                "assets/images/item_fire_bomb.png", (96, 96)),
            "mega":         self.load_image_or_fallback(
                "assets/images/item_mega_bomb.png", (96, 96)),
        }

        self.img_anim_slash      = self.load_image_or_fallback(
            "assets/images/anim_slash.png",      (256, 256))
        self.img_anim_boss_slash = self.load_image_or_fallback(
            "assets/images/anim_boss_slash.png", (256, 256))
        self.img_anim_hit        = self.load_image_or_fallback(
            "assets/images/anim_hit.png",        (256, 256))
        self.img_anim_block      = self.load_image_or_fallback(
            "assets/images/anim_block.png",      (256, 256))
        self.img_anim_death      = self.load_image_or_fallback(
            "assets/images/anim_death.png",      (256, 256))

        self.sfx_shield = self.load_sound("assets/video/defensaescudo.mp3")
        self.sfx_hit    = self.load_sound("assets/video/efectodegolpe.mp3")
        self.sfx_magic  = self.load_sound("assets/video/efectodemagia.mp3")

        self.bg_menu     = self.load_background_or_gradient(
            "assets/images/menu_bg.png",    (10, 25, 47),   (2, 6, 12))
        self.bg_jungle   = self.load_background_or_gradient(
            "assets/images/bg_jungle.png",  (6, 50, 32),    (15, 23, 42))
        self.bg_swamp    = self.load_background_or_gradient(
            "assets/images/bg_swamp.png",   (20, 40, 20),   (5, 10, 10))
        self.bg_mountain = self.load_background_or_gradient(
            "assets/images/bg_mountain.png",(50, 50, 70),   (20, 20, 30))
        self.bg_cave     = self.load_background_or_gradient(
            "assets/images/bg_cave.png",    (30, 10, 40),   (10, 2, 15))
        self.bg_shop     = self.load_background_or_gradient(
            "assets/images/bg_shop.png",    (80, 50, 30),   (30, 20, 10))
        self.bg_ending   = self.load_background_or_gradient(
            "assets/images/bg_ending.png",  (120, 80, 20),  (20, 10, 40))
