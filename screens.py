import pygame
import sys
import cv2
import math
import random
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, MUSIC_VOLUME,
                       COLOR_BG, COLOR_TEXT, COLOR_TEXT_MUTED,
                       COLOR_PRIMARY, COLOR_PRIMARY_HOVER,
                       COLOR_SECONDARY, COLOR_DANGER, COLOR_WARNING, COLOR_ACCENT)
from entities import FloatingText


class ScreensMixin:

    # ------------------------------------------------------------------ video
    def play_video(self, video_path, audio_path=None):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: No se pudo abrir el video {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 120:
            fps = 30

        audio_playing = False
        if audio_path:
            import os
            if os.path.exists(audio_path):
                try:
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    pygame.mixer.music.play()
                    audio_playing = True
                except Exception as e:
                    print(f"No se pudo reproducir el audio del video: {e}")

        clock_cv      = pygame.time.Clock()
        running_video = True

        while running_video:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RETURN):
                        running_video = False

            ret, frame = cap.read()
            if not ret:
                break

            frame   = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frame   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            surface = pygame.image.frombuffer(frame.tobytes(),
                                              (SCREEN_WIDTH, SCREEN_HEIGHT), "RGB")
            self.screen.blit(surface, (0, 0))

            skip_text = self.font_small.render("Presiona ESPACIO para omitir",
                                               True, (200, 200, 200))
            txt_bg = pygame.Surface(
                (skip_text.get_width() + 10, skip_text.get_height() + 6), pygame.SRCALPHA)
            txt_bg.fill((0, 0, 0, 150))
            self.screen.blit(txt_bg,   (SCREEN_WIDTH - skip_text.get_width() - 25, 20))
            self.screen.blit(skip_text,(SCREEN_WIDTH - skip_text.get_width() - 20, 23))
            pygame.display.flip()
            clock_cv.tick(fps)

        cap.release()
        if audio_playing:
            pygame.mixer.music.fadeout(1000)

    # -------------------------------------------------------------- dialog box
    def draw_dialog_box(self, character_name, text, portrait=None, text_progress=0):
        panel_y = SCREEN_HEIGHT - 220
        self.screen.blit(self.img_dialog_box, (20, panel_y))

        text_offset_x = 40
        if portrait:
            portrait_size = 160
            port_rect     = pygame.Rect(40, panel_y + 20, portrait_size, portrait_size)
            pygame.draw.rect(self.screen, (15, 23, 42), port_rect)
            resized = pygame.transform.scale(portrait, (portrait_size, portrait_size))
            self.screen.blit(resized, (40, panel_y + 20))
            pygame.draw.rect(self.screen, (251, 191, 36), port_rect, width=2)
            pygame.draw.rect(self.screen, (217, 119,  6), port_rect.inflate(4, 4), width=2)
            text_offset_x = 220

        if character_name:
            name_surf = self.font_ui.render(character_name, True, COLOR_PRIMARY)
            self.screen.blit(name_surf, (text_offset_x, panel_y + 20))

        shown_text = text[:int(text_progress)]
        words      = shown_text.split(' ')
        lines      = []
        curr_line  = ""
        max_w      = SCREEN_WIDTH - text_offset_x - 60

        for word in words:
            test = self.font_body.render(curr_line + word + " ", True, COLOR_TEXT)
            if test.get_width() < max_w:
                curr_line += word + " "
            else:
                lines.append(curr_line)
                curr_line = word + " "
        lines.append(curr_line)

        line_y = panel_y + (50 if character_name else 25)
        for line in lines:
            self.screen.blit(
                self.font_body.render(line.strip(), True, COLOR_TEXT),
                (text_offset_x, line_y))
            line_y += 30

        if int(text_progress) >= len(text):
            pulse      = int((math.sin(pygame.time.get_ticks() * 0.007) + 1) * 127)
            cont_color = (pulse, 255, pulse)
            cont_surf  = self.font_small.render(
                "PRESIONA ESPACIO PARA CONTINUAR", True, cont_color)
            self.screen.blit(cont_surf,
                             (SCREEN_WIDTH - cont_surf.get_width() - 40, SCREEN_HEIGHT - 50))

    # --------------------------------------------------------------- battle animations
    def draw_battle_animation(self, anim):
        frame = anim["timer"]
        x, y  = anim["x"], anim["y"]
        atype = anim["type"]
        max_f = anim["max_frames"]

        if atype == "slash":
            alpha   = max(0, 255 - int(frame * (255 / max_f)))
            angle   = -frame * 3
            scale_f = 0.5 + 0.5 * (frame / max_f)
            w = int(256 * scale_f)
            h = int(256 * scale_f)
            scaled  = pygame.transform.scale(self.img_anim_slash, (w, h))
            rotated = pygame.transform.rotate(scaled, angle)
            temp    = rotated.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp, (x - temp.get_width() // 2 - frame * 3,
                                    y - temp.get_height() // 2 + frame * 3))

        elif atype == "boss_slash":
            alpha   = max(0, 255 - int(frame * (255 / max_f)))
            angle   = frame * 3
            scale_f = 0.5 + 0.5 * (frame / max_f)
            w = int(256 * scale_f)
            h = int(256 * scale_f)
            scaled  = pygame.transform.scale(self.img_anim_boss_slash, (w, h))
            rotated = pygame.transform.rotate(scaled, angle)
            temp    = rotated.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp, (x - temp.get_width() // 2 + frame * 3,
                                    y - temp.get_height() // 2 + frame * 3))

        elif atype == "hit":
            progress   = frame / max_f
            scale_size = int(64 + progress * 192)
            alpha      = max(0, 255 - int(progress * 255))
            scaled     = pygame.transform.scale(self.img_anim_hit, (scale_size, scale_size))
            temp       = scaled.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp, (x - scale_size // 2, y - scale_size // 2))

        elif atype == "block":
            progress   = frame / max_f
            scale_size = int(128 + progress * 60)
            alpha      = max(0, 255 - int(progress * 255))
            scaled     = pygame.transform.scale(self.img_anim_block, (scale_size, scale_size))
            temp       = scaled.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp, (x - scale_size // 2, y - scale_size // 2))

        elif atype == "death":
            alpha      = max(0, 255 - int(frame * (255 / max_f)))
            scale_size = int(128 + frame * 3)
            scaled     = pygame.transform.scale(self.img_anim_death, (scale_size, scale_size))
            temp       = scaled.copy()
            temp.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp, (x - scale_size // 2,
                                    y - frame * 4 - scale_size // 2))

    # ---------------------------------------------------------------- battle
    def draw_battle_screen(self):
        bg = self.bg_jungle
        if self.current_scene_index == 3: bg = self.bg_swamp
        elif self.current_scene_index == 4: bg = self.bg_mountain
        elif self.current_scene_index == 5: bg = self.bg_cave
        self.screen.blit(bg, (0, 0))

        shk_x = random.randint(-self.shake_intensity, self.shake_intensity) \
            if self.shake_intensity > 0 else 0
        shk_y = random.randint(-self.shake_intensity, self.shake_intensity) \
            if self.shake_intensity > 0 else 0

        # --- player (Principles 1, 7)
        p_x = self.player_visual_x + self.player_offset_x + shk_x
        p_y = 220 + self.player_offset_y + shk_y

        if self.player_squash_timer > 0:
            t    = self.player_squash_timer / 8.0
            sq_w = int(256 * (1.0 + 0.28 * t))
            sq_h = int(256 * (1.0 - 0.20 * t))
            sq   = pygame.transform.scale(self.img_knight, (sq_w, sq_h))
            self.screen.blit(sq, (p_x - (sq_w - 256) // 2, p_y + (256 - sq_h)))
            self.player_squash_timer -= 1
        else:
            self.screen.blit(self.img_knight, (p_x, p_y))

        self.screen.blit(self.font_ui.render("CABALLERO", True, COLOR_PRIMARY),
                         (p_x, p_y - 65))

        pygame.draw.rect(self.screen, (30, 41, 59), (p_x, p_y - 50, 256, 14))
        hp_pct = self.player_hp / self.player_max_hp
        pygame.draw.rect(self.screen, COLOR_PRIMARY, (p_x, p_y - 50, int(256 * hp_pct), 14))
        pygame.draw.rect(self.screen, COLOR_TEXT,    (p_x, p_y - 50, 256, 14), width=2)
        self.screen.blit(
            self.font_small.render(f"HP: {self.player_hp}/{self.player_max_hp}",
                                   True, COLOR_TEXT), (p_x, p_y - 32))

        self.screen.blit(
            self.font_small.render("ENERGIA:", True, COLOR_TEXT_MUTED), (p_x, p_y - 16))
        for i in range(self.player_max_energy):
            ec = (250, 204, 21) if i < self.player_energy else (71, 85, 105)
            pygame.draw.rect(self.screen, ec,         (p_x + 85 + i * 16, p_y - 16, 10, 10))
            pygame.draw.rect(self.screen, COLOR_TEXT, (p_x + 85 + i * 16, p_y - 16, 10, 10),
                             width=1)

        # --- boss (Principles 1, 2, 7)
        b_x = self.boss_visual_x + self.boss_offset_x + shk_x
        b_y = 220 + self.boss_offset_y + shk_y

        # Anticipation (Principle 2) — wobble when charging
        if getattr(self, "boss_charged", False):
            b_x -= int(18 * math.sin(pygame.time.get_ticks() * 0.009))

        if self.boss_squash_timer > 0:
            t    = self.boss_squash_timer / 8.0
            sq_w = int(256 * (1.0 + 0.28 * t))
            sq_h = int(256 * (1.0 - 0.20 * t))
            sq   = pygame.transform.scale(self.current_boss["portrait"], (sq_w, sq_h))
            self.screen.blit(sq, (b_x - (sq_w - 256) // 2, b_y + (256 - sq_h)))
            self.boss_squash_timer -= 1
        else:
            self.screen.blit(self.current_boss["portrait"], (b_x, b_y))

        self.screen.blit(
            self.font_ui.render(self.current_boss["name"].upper(), True, COLOR_DANGER),
            (b_x, b_y - 65))

        pygame.draw.rect(self.screen, (30, 41, 59), (b_x, b_y - 50, 256, 14))
        bhp_pct = self.current_boss["hp"] / self.current_boss["max_hp"]
        pygame.draw.rect(self.screen, COLOR_DANGER, (b_x, b_y - 50, int(256 * bhp_pct), 14))
        pygame.draw.rect(self.screen, COLOR_TEXT,   (b_x, b_y - 50, 256, 14), width=2)
        self.screen.blit(
            self.font_small.render(
                f"HP: {self.current_boss['hp']}/{self.current_boss['max_hp']}",
                True, COLOR_TEXT), (b_x, b_y - 32))

        # Charge indicator (Principles 9, 10)
        if getattr(self, "boss_charged", False):
            pulse    = abs(math.sin(pygame.time.get_ticks() * 0.007))
            warn_r   = int(245 * pulse + 180 * (1 - pulse))
            warn_g   = int(158 * pulse + 30  * (1 - pulse))
            warn_b   = int( 11 * pulse + 200 * (1 - pulse))
            ch_lbl   = self.font_small.render(
                "!! CARGANDO ATAQUE DEVASTADOR !!", True, (warn_r, warn_g, warn_b))
            scale_f  = 1.0 + 0.10 * pulse
            ch_scaled= pygame.transform.scale(
                ch_lbl, (int(ch_lbl.get_width() * scale_f),
                          int(ch_lbl.get_height() * scale_f)))
            self.screen.blit(ch_scaled, (b_x, b_y - 90))

        # Battle animations
        for anim in self.battle_animations[:]:
            anim["timer"] += 1
            self.draw_battle_animation(anim)
            if anim["timer"] >= anim["max_frames"]:
                self.battle_animations.remove(anim)

        # Combat log
        log_panel = pygame.Surface((560, 160), pygame.SRCALPHA)
        log_panel.fill((15, 23, 42, 220))
        pygame.draw.rect(log_panel, COLOR_SECONDARY, (0, 0, 560, 160), width=2)
        self.screen.blit(log_panel, (20, SCREEN_HEIGHT - 180))

        log_y = SCREEN_HEIGHT - 170
        for log in self.combat_log:
            lc = COLOR_TEXT
            if "daño" in log or "recibes" in log:   lc = (252, 165, 165)
            elif "Bloqueas" in log or "Esquiva" in log or "TP" in log: lc = (167, 243, 208)
            elif "Tu turno" in log:                 lc = COLOR_ACCENT
            self.screen.blit(self.font_small.render(log, True, lc), (35, log_y))
            log_y += 28

        # Action buttons
        actions = self.get_player_actions()
        act_panel = pygame.Surface((400, 160), pygame.SRCALPHA)
        act_panel.fill((30, 41, 59, 220))
        pygame.draw.rect(act_panel, COLOR_PRIMARY, (0, 0, 400, 160), width=2)
        self.screen.blit(act_panel, (600, SCREEN_HEIGHT - 180))

        mx, my        = pygame.mouse.get_pos()
        hovered_index = -1

        for idx, act in enumerate(actions):
            btn_x = 610 + (idx % 2) * 190
            btn_y = SCREEN_HEIGHT - 165 + (idx // 2) * 45
            btn_w, btn_h = 185, 38
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            is_hover = btn_rect.collidepoint(mx, my)
            if is_hover:
                hovered_index = idx
                btn_color  = COLOR_PRIMARY
                text_color = COLOR_BG
            else:
                btn_color  = (47, 55, 71)
                text_color = COLOR_TEXT

            pygame.draw.rect(self.screen, btn_color, btn_rect)
            if not is_hover:
                pygame.draw.rect(self.screen, COLOR_PRIMARY, btn_rect, width=1)
            self.screen.blit(
                self.font_small.render(act["name"], True, text_color), (btn_x + 8, btn_y + 14))
            self.screen.blit(
                self.font_small.render(f"E:{act['energy']}", True,
                                       (234, 179, 8) if is_hover else (253, 224, 71)),
                (btn_x + btn_w - 32, btn_y + 14))

        if hovered_index != -1:
            ha      = actions[hovered_index]
            desc_bg = pygame.Surface((380, 75), pygame.SRCALPHA)
            desc_bg.fill((15, 23, 42, 230))
            pygame.draw.rect(desc_bg, COLOR_ACCENT, (0, 0, 380, 75), width=1)
            self.screen.blit(desc_bg, (610, SCREEN_HEIGHT - 265))
            self.screen.blit(
                self.font_small.render(f"Acierto: {ha['prob']}%", True, COLOR_PRIMARY),
                (620, SCREEN_HEIGHT - 260))

            desc_lines = []
            words = ha["desc"].split(" ")
            curr  = ""
            for word in words:
                if self.font_small.render(curr + word, True, COLOR_TEXT).get_width() < 350:
                    curr += word + " "
                else:
                    desc_lines.append(curr)
                    curr = word + " "
            desc_lines.append(curr)

            lbl_y = SCREEN_HEIGHT - 235
            for line in desc_lines[:2]:
                self.screen.blit(
                    self.font_small.render(line.strip(), True, COLOR_TEXT_MUTED),
                    (620, lbl_y))
                lbl_y += 18

        # Floating texts
        for txt in self.floating_texts[:]:
            if not txt.update():
                self.floating_texts.remove(txt)
            else:
                txt.draw(self.screen)

        if self.shake_intensity > 0:
            self.shake_intensity = int(self.shake_intensity * self.shake_decay)
        if self.flash_screen_red > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((239, 68, 68, self.flash_screen_red))
            self.screen.blit(flash, (0, 0))
            self.flash_screen_red = max(0, self.flash_screen_red - 10)

    # ------------------------------------------------------------------ shop
    def draw_shop_screen(self):
        self.screen.blit(self.bg_shop, (0, 0))

        self.screen.blit(
            self.font_title.render("TIENDA DE MEJORAS", True, COLOR_WARNING),
            (SCREEN_WIDTH // 2 - self.font_title.render(
                "TIENDA DE MEJORAS", True, COLOR_WARNING).get_width() // 2, 40))

        sub = "Elige sabiamente. Solo puedes seleccionar una mejora por habilidad."
        sub_s = self.font_subtitle.render(sub, True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_s, (SCREEN_WIDTH // 2 - sub_s.get_width() // 2, 105))

        self.screen.blit(self.img_merchant, (80, 220))
        self.screen.blit(
            self.font_ui.render("Mercader de la Isla", True, COLOR_PRIMARY), (115, 490))

        dialog_text = {
            2: "Has derrotado al guardián. Su energía ha liberado el Escudo de Acero. Elige qué encantamiento rúnico deseas aplicarle para defenderte.",
            3: "La magia del mago te ha otorgado la habilidad de Teletransportación. ¿Deseas esquivar y contraatacar, o prefieres recuperar tu aliento y energía?",
            4: "El núcleo del Gólem de piedra se ha convertido en bombas. Elige si prefieres hacer arder a tus enemigos con fuego continuo o una explosión masiva.",
        }.get(self.current_scene_index, "")

        bubble = pygame.Rect(380, 180, 560, 100)
        pygame.draw.rect(self.screen, (15, 23, 42, 230), bubble)
        pygame.draw.rect(self.screen, COLOR_WARNING, bubble, width=2)

        words = dialog_text.split(" ")
        lines = []
        curr  = ""
        for w in words:
            if self.font_small.render(curr + w, True, COLOR_TEXT).get_width() < 520:
                curr += w + " "
            else:
                lines.append(curr)
                curr = w + " "
        lines.append(curr)
        ly = 195
        for line in lines[:3]:
            self.screen.blit(
                self.font_small.render(line.strip(), True, COLOR_TEXT), (400, ly))
            ly += 22

        choices    = self.get_shop_choices()
        mx, my     = pygame.mouse.get_pos()
        self.hovered_card_index = -1

        for idx, choice in enumerate(choices):
            card_x, card_y, card_w, card_h = 380 + idx * 290, 310, 270, 360
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            is_hover  = card_rect.collidepoint(mx, my)

            if is_hover:
                self.hovered_card_index = idx
                border_color = COLOR_PRIMARY
                bg_color     = (30, 41, 59)
                scale        = 1.02
            else:
                border_color = COLOR_WARNING
                bg_color     = (15, 23, 42)
                scale        = 1.0

            w_s = int(card_w * scale)
            h_s = int(card_h * scale)
            x_s = card_x - (w_s - card_w) // 2
            y_s = card_y - (h_s - card_h) // 2

            card_surf = pygame.Surface((w_s, h_s), pygame.SRCALPHA)
            card_surf.fill(bg_color)
            pygame.draw.rect(card_surf, border_color, (0, 0, w_s, h_s), width=3)
            self.screen.blit(card_surf, (x_s, y_s))

            self.screen.blit(
                self.font_ui.render(choice["title"], True, border_color), (x_s + 15, y_s + 20))
            self.screen.blit(
                self.font_small.render(f"Precio: {choice['cost']}", True, COLOR_PRIMARY),
                (x_s + 15, y_s + 55))

            item_id = choice["id"]
            if item_id in self.shop_item_images:
                img_x = x_s + (w_s - 96) // 2
                self.screen.blit(self.shop_item_images[item_id], (img_x, y_s + 85))

            pygame.draw.line(self.screen, COLOR_TEXT_MUTED,
                             (x_s + 15, y_s + 190), (x_s + w_s - 15, y_s + 190), width=1)

            desc_words = choice["desc"].split(" ")
            desc_lines = []
            curr_dl    = ""
            for dw in desc_words:
                if self.font_small.render(curr_dl + dw, True, COLOR_TEXT).get_width() < (w_s - 40):
                    curr_dl += dw + " "
                else:
                    desc_lines.append(curr_dl)
                    curr_dl = dw + " "
            desc_lines.append(curr_dl)
            dy_offset = y_s + 205
            for dl in desc_lines[:10]:
                self.screen.blit(
                    self.font_small.render(dl.strip(), True, COLOR_TEXT_MUTED),
                    (x_s + 15, dy_offset))
                dy_offset += 22

            btn_r = pygame.Rect(x_s + 20, y_s + h_s - 60, w_s - 40, 40)
            pygame.draw.rect(self.screen, COLOR_PRIMARY if is_hover else (47, 55, 71), btn_r)
            btn_txt = self.font_small.render("ADQUIRIR", True,
                                             COLOR_BG if is_hover else COLOR_TEXT)
            self.screen.blit(btn_txt, (btn_r.x + btn_r.width // 2 - btn_txt.get_width() // 2,
                                       btn_r.y + 10))

    # ------------------------------------------------------------------- menu
    def draw_menu_screen(self):
        self.screen.blit(self.bg_menu, (0, 0))

        for p in self.particles:
            p.update()
            p.draw(self.screen)

        title_text   = "THE GREEN ISLAND"
        title_shadow = self.font_title.render(title_text, True, (0, 0, 0))
        title_main   = self.font_title.render(title_text, True, COLOR_PRIMARY)
        x = SCREEN_WIDTH  // 2 - title_main.get_width()  // 2
        y = SCREEN_HEIGHT // 3 - title_main.get_height() // 2
        self.screen.blit(title_shadow, (x + 4, y + 4))
        self.screen.blit(title_main,   (x, y))

        sub = "Una leyenda por turnos en tierras oscuras"
        sub_s = self.font_subtitle.render(sub, True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_s, (SCREEN_WIDTH // 2 - sub_s.get_width() // 2, y + 80))

        mx, my  = pygame.mouse.get_pos()
        btn_w, btn_h = 320, 60
        btn_cx  = SCREEN_WIDTH // 2 - btn_w // 2

        btn1_rect = pygame.Rect(btn_cx, SCREEN_HEIGHT // 2 + 30, btn_w, btn_h)
        is_hover1 = btn1_rect.collidepoint(mx, my)
        if is_hover1:
            zoomed = pygame.transform.scale(self.img_btn_play_hover, (btn_w + 8, btn_h + 4))
            self.screen.blit(zoomed, (btn1_rect.x - 4, btn1_rect.y - 2))
            pulse = int((math.sin(pygame.time.get_ticks() * 0.006) + 1) * 80) + 40
            glow  = pygame.Surface((btn_w + 16, btn_h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (52, 211, 153, pulse), (0, 0, btn_w+16, btn_h+12), width=3)
            self.screen.blit(glow, (btn1_rect.x - 8, btn1_rect.y - 6))
        else:
            self.screen.blit(self.img_btn_play_normal, btn1_rect.topleft)

        btn2_rect = pygame.Rect(btn_cx, SCREEN_HEIGHT // 2 + 115, btn_w, btn_h)
        is_hover2 = btn2_rect.collidepoint(mx, my)
        if is_hover2:
            zoomed = pygame.transform.scale(self.img_btn_exit_hover, (btn_w + 8, btn_h + 4))
            self.screen.blit(zoomed, (btn2_rect.x - 4, btn2_rect.y - 2))
            pulse = int((math.sin(pygame.time.get_ticks() * 0.006) + 1) * 80) + 40
            glow  = pygame.Surface((btn_w + 16, btn_h + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (239, 68, 68, pulse), (0, 0, btn_w+16, btn_h+12), width=3)
            self.screen.blit(glow, (btn2_rect.x - 8, btn2_rect.y - 6))
        else:
            self.screen.blit(self.img_btn_exit_normal, btn2_rect.topleft)

        return is_hover1, is_hover2

    # --------------------------------------------------------------- gameover
    def draw_gameover_screen(self):
        self.screen.fill((10, 10, 15))

        title_s = self.font_title.render("TU AVENTURA HA TERMINADO", True, COLOR_DANGER)
        self.screen.blit(title_s,
                         (SCREEN_WIDTH // 2 - title_s.get_width() // 2, SCREEN_HEIGHT // 3))

        sub_s = self.font_subtitle.render(
            "El caballero cayó combatiendo las sombras en The Green Island.",
            True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_s, (SCREEN_WIDTH // 2 - sub_s.get_width() // 2,
                                  SCREEN_HEIGHT // 3 + 80))

        mx, my = pygame.mouse.get_pos()

        btn_retry    = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50,  300, 50)
        is_hov_retry = btn_retry.collidepoint(mx, my)
        pygame.draw.rect(self.screen,
                         COLOR_PRIMARY if is_hov_retry else (30, 41, 59), btn_retry)
        retry_lbl = self.font_ui.render(
            "REINTENTAR BATALLA", True, COLOR_BG if is_hov_retry else COLOR_TEXT)
        self.screen.blit(retry_lbl,
                         (SCREEN_WIDTH // 2 - retry_lbl.get_width() // 2, btn_retry.y + 12))

        btn_menu    = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 120, 300, 50)
        is_hov_menu = btn_menu.collidepoint(mx, my)
        pygame.draw.rect(self.screen,
                         COLOR_DANGER if is_hov_menu else (30, 41, 59), btn_menu)
        menu_lbl = self.font_ui.render(
            "MENÚ PRINCIPAL", True, COLOR_BG if is_hov_menu else COLOR_TEXT)
        self.screen.blit(menu_lbl,
                         (SCREEN_WIDTH // 2 - menu_lbl.get_width() // 2, btn_menu.y + 12))

        return is_hov_retry, is_hov_menu
