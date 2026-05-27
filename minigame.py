import pygame
import random
import math
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PRIMARY, COLOR_DANGER,
                       COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_WARNING,
                       STATE_MINIGAME, STATE_BATTLE, STATE_GAMEOVER)
from entities import FloatingText

# QTE key pool for the final strike
_QTE_KEYS = [
    (pygame.K_UP,    "UP",    (56,  189, 248)),   # celeste
    (pygame.K_DOWN,  "DOWN",  (16,  185, 129)),   # verde
    (pygame.K_LEFT,  "LEFT",  (245, 158,  11)),   # naranja
    (pygame.K_RIGHT, "RIGHT", (239,  68,  68)),   # rojo
    (pygame.K_SPACE, "SPC",   (168,  85, 247)),   # morado
]


class MinigameMixin:

    # ================================================================ sounds
    def synthesize_minigame_sounds(self):
        try:
            import numpy as np
        except ImportError:
            print("[Minijuego] numpy no disponible — sonidos sintetizados desactivados.")
            self.minigame_sfx_hit  = None
            self.minigame_sfx_warn = None
            self.minigame_bgm      = None
            return

        sample_rate = 44100

        # Warning SFX — double beep
        try:
            dur = 0.2
            n   = int(sample_rate * dur)
            t   = np.linspace(0, dur, n, endpoint=False)
            sig = np.zeros(n)
            h   = n // 2
            t1  = t[:h]
            sig[:h] = (np.where(np.sin(2*np.pi*580*t1) > 0, 0.3, -0.3)
                       * np.exp(-15*t1))
            t2  = t[h:] - t[h]
            sig[h:] = (np.where(np.sin(2*np.pi*780*t2) > 0, 0.3, -0.3)
                       * np.exp(-15*t2))
            audio = (sig * 32767).astype(np.int16)
            self.minigame_sfx_warn = pygame.sndarray.make_sound(
                np.column_stack((audio, audio)))
        except Exception as e:
            print(f"[Minijuego] Warn SFX error: {e}")
            self.minigame_sfx_warn = None

        # Hit SFX
        try:
            dur = 0.15
            n   = int(sample_rate * dur)
            t   = np.linspace(0, dur, n, endpoint=False)
            freqs  = np.linspace(350, 60, n)
            square = np.where(np.sin(2*np.pi*freqs*t) > 0, 0.4, -0.4)
            noise  = np.random.uniform(-0.15, 0.15, n)
            sig    = (square + noise) * np.exp(-10*t)
            m = np.max(np.abs(sig))
            if m > 0: sig /= m
            audio = (sig * 0.4 * 32767).astype(np.int16)
            self.minigame_sfx_hit = pygame.sndarray.make_sound(
                np.column_stack((audio, audio)))
        except Exception as e:
            print(f"[Minijuego] Hit SFX error: {e}")
            self.minigame_sfx_hit = None

        # 8-bit BGM loop — Am/F/C/G arpeggio
        try:
            note_dur  = 0.125
            spn       = int(sample_rate * note_dur)
            chords = {
                'Am': [220.00,261.63,329.63,440.00,329.63,261.63,220.00,261.63],
                'F':  [174.61,220.00,261.63,349.23,261.63,220.00,174.61,220.00],
                'C':  [130.81,164.81,196.00,261.63,196.00,164.81,130.81,164.81],
                'G':  [196.00,246.94,293.66,392.00,293.66,246.94,196.00,246.94],
            }
            melody     = chords['Am']+chords['F']+chords['C']+chords['G']
            bass_roots = [110.0, 87.31, 65.41, 98.0]
            buf        = np.zeros(spn * len(melody), dtype=np.float32)
            for i, freq in enumerate(melody):
                s = i * spn
                e = s + spn
                t = np.linspace(0, note_dur, spn, endpoint=False)
                lead     = (np.where(np.sin(2*np.pi*freq*t) > 0.5, 0.25, -0.25)
                            * np.exp(-4*t))
                bf       = bass_roots[i//8]
                tf       = t * bf
                triangle = 2.0 * np.abs(2.0*(tf-np.floor(tf+0.5))) - 1.0
                buf[s:e] = lead + triangle * 0.2
            m = np.max(np.abs(buf))
            if m > 0: buf /= m
            audio = (buf * 0.4 * 32767).astype(np.int16)
            self.minigame_bgm = pygame.sndarray.make_sound(
                np.column_stack((audio, audio)))
        except Exception as e:
            print(f"[Minijuego] BGM error: {e}")
            self.minigame_bgm = None

    # ============================================================= FINAL STRIKE
    def start_final_strike(self):
        """Triggered when the boss reaches 0 HP — player performs the killing combo."""
        self.final_strike_triggered = True
        self.state             = STATE_MINIGAME
        self.minigame_type     = "final_strike"
        self.minigame_duration = 1200   # 20 s @ 60 FPS
        self.minigame_timer    = 1200
        self.floating_texts    = []

        # Generate 12 QTE prompts (one per ~1.67 s)
        pool = list(_QTE_KEYS)
        prompts = []
        for i in range(12):
            key, name, color = random.choice(pool)
            # Target window: somewhere between 55-75% of prompt duration
            ts = random.uniform(0.55, 0.70)
            prompts.append({
                "key":          key,
                "key_name":     name,
                "key_color":    color,
                "duration":     100,       # frames per prompt
                "timer":        0,
                "target_start": ts,
                "target_end":   ts + 0.20, # 20%-wide green zone
                "pressed":      False,
                "result":       None,      # "perfect","good","late","early","miss"
            })
        self.final_strike_prompts      = prompts
        self.final_strike_current      = 0
        self.final_strike_score        = 0
        self.final_strike_max_score    = 12 * 100
        self.final_strike_result_flash = None   # (text, color)
        self.final_strike_result_timer = 0

        pygame.mixer.music.pause()
        if self.minigame_sfx_warn:
            self.minigame_sfx_warn.play()
        if self.minigame_bgm:
            self.minigame_bgm.play(-1)

    def _register_final_strike_press(self, prompt):
        """Score a QTE prompt based on when the key was pressed."""
        progress = prompt["timer"] / prompt["duration"]
        ts, te   = prompt["target_start"], prompt["target_end"]

        if ts <= progress <= te:
            # How centred in the zone?
            centre = (ts + te) / 2
            half_w = (te - ts) / 2
            ratio  = abs(progress - centre) / half_w
            if ratio < 0.4:
                prompt["result"]            = "perfect"
                self.final_strike_score    += 100
                self.final_strike_result_flash = ("¡¡ PERFECTO !!", (52, 211, 153))
            else:
                prompt["result"]            = "good"
                self.final_strike_score    += 60
                self.final_strike_result_flash = ("BIEN", (245, 158, 11))
            self.shake_intensity = 14
            if self.minigame_sfx_hit:
                self.minigame_sfx_hit.play()
        elif progress < ts:
            prompt["result"]               = "early"
            self.final_strike_score       += 15
            self.final_strike_result_flash = ("PRONTO...", COLOR_TEXT_MUTED)
        else:
            prompt["result"]               = "late"
            self.final_strike_score       += 15
            self.final_strike_result_flash = ("TARDE", COLOR_TEXT_MUTED)

        prompt["pressed"]              = True
        self.final_strike_result_timer = 45
        self.final_strike_current     += 1

    def update_final_strike(self, keys, just_pressed):
        if self.final_strike_result_timer > 0:
            self.final_strike_result_timer -= 1

        if self.final_strike_current >= len(self.final_strike_prompts):
            self.end_final_strike()
            return

        prompt = self.final_strike_prompts[self.final_strike_current]
        prompt["timer"] += 1

        if not prompt["pressed"]:
            if prompt["key"] in just_pressed:
                self._register_final_strike_press(prompt)
            elif prompt["timer"] >= prompt["duration"]:
                # Timed out — MISS
                prompt["result"]               = "miss"
                prompt["pressed"]              = True
                self.final_strike_result_flash = ("FALLADO", COLOR_DANGER)
                self.final_strike_result_timer = 45
                self.final_strike_current     += 1

        # Overall countdown (just for the progress bar)
        self.minigame_timer -= 1
        if self.minigame_timer <= 0:
            self.end_final_strike()

    def draw_final_strike(self):
        # Background — boss battle bg, heavily dimmed
        bg = self.bg_jungle
        if self.current_scene_index == 3: bg = self.bg_swamp
        elif self.current_scene_index == 4: bg = self.bg_mountain
        elif self.current_scene_index == 5: bg = self.bg_cave
        self.screen.blit(bg, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 210))
        self.screen.blit(overlay, (0, 0))

        # Pulsing title
        pulse      = abs(math.sin(pygame.time.get_ticks() * 0.008))
        title_r    = int(239 * pulse + 180 * (1 - pulse))
        title_g    = int( 68 * pulse +  20 * (1 - pulse))
        title_b    = int( 68 * pulse + 180 * (1 - pulse))
        title_surf = self.font_title.render("!! GOLPE FINAL !!", True,
                                            (title_r, title_g, title_b))
        scale_f    = 1.0 + 0.06 * pulse
        title_s    = pygame.transform.scale(
            title_surf,
            (int(title_surf.get_width() * scale_f),
             int(title_surf.get_height() * scale_f)))
        self.screen.blit(title_s,
                         (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 28))

        # Boss portrait (centre, shaking)
        shk = random.randint(-self.shake_intensity, self.shake_intensity) \
            if self.shake_intensity > 0 else 0
        portrait  = self.current_boss["portrait"]
        port_surf = pygame.transform.scale(portrait, (180, 180))
        # Red tint overlay on portrait
        tint = pygame.Surface((180, 180), pygame.SRCALPHA)
        tint.fill((239, 68, 68, int(80 * pulse)))
        port_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.screen.blit(port_surf,
                         (SCREEN_WIDTH // 2 - 90 + shk, 110 + shk // 2))

        # Score circles (top-right strip)
        for i, p in enumerate(self.final_strike_prompts):
            cx = SCREEN_WIDTH - 30 - (11 - i) * 24
            cy = 55
            if p["result"] is None:
                color = (50, 60, 80)
            elif p["result"] == "perfect":
                color = (52, 211, 153)
            elif p["result"] == "good":
                color = (245, 158, 11)
            elif p["result"] == "miss":
                color = (239, 68, 68)
            else:  # early/late
                color = (148, 163, 184)
            pygame.draw.circle(self.screen, color, (cx, cy), 8)
            pygame.draw.circle(self.screen, (200, 200, 200), (cx, cy), 8, width=1)

        # === Current prompt ===
        if self.final_strike_current < len(self.final_strike_prompts):
            prompt   = self.final_strike_prompts[self.final_strike_current]
            progress = min(1.0, prompt["timer"] / prompt["duration"])
            ts       = prompt["target_start"]
            te       = min(1.0, prompt["target_end"])
            key_color= prompt["key_color"]

            # Key icon box
            box_cx = SCREEN_WIDTH // 2
            box_cy = 330
            box_s  = 90
            # Glow ring when cursor is in target zone
            in_zone = ts <= progress <= te
            ring_alpha = int(180 * pulse) if in_zone else 60
            ring_color = (*key_color, ring_alpha)
            ring_surf  = pygame.Surface((box_s + 30, box_s + 30), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, ring_color,
                               ((box_s+30)//2, (box_s+30)//2), (box_s+30)//2)
            self.screen.blit(ring_surf, (box_cx - (box_s+30)//2,
                                          box_cy - (box_s+30)//2))

            pygame.draw.rect(self.screen, (20, 25, 35),
                             (box_cx - box_s//2, box_cy - box_s//2, box_s, box_s),
                             border_radius=10)
            border_col = key_color if in_zone else (80, 90, 110)
            pygame.draw.rect(self.screen, border_col,
                             (box_cx - box_s//2, box_cy - box_s//2, box_s, box_s),
                             width=4, border_radius=10)

            # Arrow drawn with pygame.draw
            self._draw_qte_arrow(self.screen, prompt["key"], box_cx, box_cy,
                                 size=36, color=key_color if in_zone else (160,170,190))

            # Timing bar
            bar_w, bar_h = 500, 18
            bar_x = SCREEN_WIDTH // 2 - bar_w // 2
            bar_y = 440

            # Background track
            pygame.draw.rect(self.screen, (25, 32, 48),
                             (bar_x, bar_y, bar_w, bar_h), border_radius=6)

            # Green zone
            gz_x = bar_x + int(ts * bar_w)
            gz_w = int((te - ts) * bar_w)
            gz_surf = pygame.Surface((gz_w, bar_h), pygame.SRCALPHA)
            gz_surf.fill((*key_color, 90))
            self.screen.blit(gz_surf, (gz_x, bar_y))
            pygame.draw.rect(self.screen, key_color,
                             (gz_x, bar_y, gz_w, bar_h),
                             width=2, border_radius=3)

            # Cursor
            cur_x  = bar_x + int(progress * bar_w)
            cur_col = key_color if in_zone else (200, 200, 200)
            pygame.draw.rect(self.screen, cur_col,
                             (cur_x - 3, bar_y - 5, 6, bar_h + 10),
                             border_radius=3)

            # Bar border
            pygame.draw.rect(self.screen, (100, 110, 130),
                             (bar_x, bar_y, bar_w, bar_h),
                             width=2, border_radius=6)

            # "¡AHORA!" hint
            if in_zone:
                ahora = self.font_subtitle.render("¡AHORA!", True, key_color)
                self.screen.blit(ahora,
                                 (SCREEN_WIDTH//2 - ahora.get_width()//2, bar_y + 30))

        # Result flash
        if self.final_strike_result_flash and self.final_strike_result_timer > 0:
            text, color = self.final_strike_result_flash
            alpha = int(255 * min(1.0, self.final_strike_result_timer / 20))
            fl_surf = self.font_title.render(text, True, color)
            fl_surf.set_alpha(alpha)
            self.screen.blit(fl_surf,
                             (SCREEN_WIDTH//2 - fl_surf.get_width()//2, 490))

        # Overall progress bar (bottom)
        prog_w = 400
        prog_h = 8
        prog_x = SCREEN_WIDTH // 2 - prog_w // 2
        prog_y = SCREEN_HEIGHT - 45
        pygame.draw.rect(self.screen, (30, 41, 59),
                         (prog_x, prog_y, prog_w, prog_h), border_radius=4)
        t_pct = self.minigame_timer / self.minigame_duration
        pygame.draw.rect(self.screen, COLOR_PRIMARY,
                         (prog_x, prog_y, int(prog_w * t_pct), prog_h),
                         border_radius=4)
        pygame.draw.rect(self.screen, COLOR_TEXT,
                         (prog_x, prog_y, prog_w, prog_h),
                         width=1, border_radius=4)

        # Completed count
        done      = self.final_strike_current
        count_lbl = self.font_small.render(
            f"COMBO: {done}/{len(self.final_strike_prompts)}", True, COLOR_TEXT_MUTED)
        self.screen.blit(count_lbl,
                         (SCREEN_WIDTH//2 - count_lbl.get_width()//2, prog_y + 14))

        # Floating texts
        for txt in self.floating_texts[:]:
            if not txt.update():
                self.floating_texts.remove(txt)
            else:
                txt.draw(self.screen)

        # Screen shake decay
        if self.shake_intensity > 0:
            self.shake_intensity = int(self.shake_intensity * self.shake_decay)

    def _draw_qte_arrow(self, surface, key, cx, cy, size, color):
        """Draw a pixel-art direction indicator for QTE prompts."""
        half = size // 2
        if key == pygame.K_UP:
            pts = [(cx, cy - half), (cx - half, cy + half//2), (cx + half, cy + half//2)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.rect(surface, color, (cx - size//6, cy, size//3, half//2))
        elif key == pygame.K_DOWN:
            pts = [(cx, cy + half), (cx - half, cy - half//2), (cx + half, cy - half//2)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.rect(surface, color, (cx - size//6, cy - half//2, size//3, half//2))
        elif key == pygame.K_LEFT:
            pts = [(cx - half, cy), (cx + half//2, cy - half), (cx + half//2, cy + half)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.rect(surface, color, (cx, cy - size//6, half//2, size//3))
        elif key == pygame.K_RIGHT:
            pts = [(cx + half, cy), (cx - half//2, cy - half), (cx - half//2, cy + half)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.rect(surface, color, (cx - half//2, cy - size//6, half//2, size//3))
        elif key == pygame.K_SPACE:
            pygame.draw.rect(surface, color,
                             (cx - half, cy - size//8, size, size//4),
                             border_radius=4)

    def end_final_strike(self):
        self.minigame_active = False
        if self.minigame_bgm:
            self.minigame_bgm.stop()

        score_pct = self.final_strike_score / max(1, self.final_strike_max_score)
        perfects  = sum(1 for p in self.final_strike_prompts if p["result"] == "perfect")
        misses    = sum(1 for p in self.final_strike_prompts if p["result"] == "miss")

        if score_pct >= 0.85:
            hp_bonus = 30
            msg      = f"¡COMBO PERFECTO! ({perfects} perfects) Recuperas {hp_bonus} HP."
        elif score_pct >= 0.60:
            hp_bonus = 15
            msg      = f"¡Buen golpe! Recuperas {hp_bonus} HP."
        elif score_pct >= 0.30:
            hp_bonus = 0
            msg      = f"El jefe cayó... pero pudiste haberlo hecho mejor ({misses} fallos)."
        else:
            hp_bonus = 0
            msg      = f"Golpe torpe... {misses} ataques fallados. El jefe cae de todos modos."

        if hp_bonus > 0:
            self.player_hp = min(self.player_max_hp, self.player_hp + hp_bonus)
            self.floating_texts.append(
                FloatingText(f"+{hp_bonus} HP", SCREEN_WIDTH//2, 350, COLOR_PRIMARY))

        self.add_combat_log(msg)
        pygame.mixer.music.unpause()

        # Trigger VICTORY
        self.state        = STATE_BATTLE
        self.battle_phase = "VICTORY"
        self.battle_timer = pygame.time.get_ticks()
        self.battle_animations.append({
            "type": "death",
            "x": self.boss_visual_x + 128,
            "y": 220 + 128,
            "timer": 0, "max_frames": 30,
        })

    # ============================================================= DODGE MINI-GAME
    def start_minigame(self, attack_name, damage, pattern, boss_color=(255, 255, 255)):
        """Bullet-hell dodge mini-game triggered by boss special attacks."""
        self.state                = STATE_MINIGAME
        self.minigame_type        = "dodge"
        self.minigame_active      = True
        self.minigame_projectiles = []
        self.minigame_hits        = 0
        self.minigame_timer       = self.minigame_duration
        self.minigame_base_damage = damage
        self.minigame_attack_name = attack_name
        self.minigame_boss_color  = boss_color
        self.minigame_pattern     = pattern
        self.minigame_spawn_timer = 0

        arena_w = 500
        arena_h = 350
        self.minigame_player_x = (SCREEN_WIDTH  - arena_w) // 2 + arena_w // 2
        self.minigame_player_y = (SCREEN_HEIGHT - arena_h) // 2 + arena_h // 2

        pygame.mixer.music.pause()
        if self.minigame_sfx_warn:
            self.minigame_sfx_warn.play()
        if self.minigame_bgm:
            self.minigame_bgm.play(-1)

    def update_minigame(self, keys, just_pressed=None):
        if self.minigame_type == "final_strike":
            self.update_final_strike(keys, just_pressed or set())
        else:
            self._update_dodge(keys)

    def _update_dodge(self, keys):
        speed = 4
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += speed

        self.minigame_player_x += dx
        self.minigame_player_y += dy

        arena_w = 500
        arena_h = 350
        arena_x = (SCREEN_WIDTH  - arena_w) // 2
        arena_y = (SCREEN_HEIGHT - arena_h) // 2
        margin  = 12
        self.minigame_player_x = max(arena_x + margin,
                                     min(arena_x + arena_w - margin, self.minigame_player_x))
        self.minigame_player_y = max(arena_y + margin,
                                     min(arena_y + arena_h - margin, self.minigame_player_y))

        self.minigame_spawn_timer += 1

        if self.minigame_pattern == "olas":
            if self.minigame_spawn_timer % 25 == 0:
                lane_h = arena_h / 5
                for lane in random.sample(range(1, 5), 3):
                    self.minigame_projectiles.append({
                        "x": float(arena_x - 15),
                        "y": float(arena_y + lane * lane_h),
                        "vx": 5.0, "vy": 0.0, "size": 8.0,
                        "color": (56, 189, 248),
                    })

        elif self.minigame_pattern == "espiral":
            if self.minigame_spawn_timer % 12 == 0:
                cx   = arena_x + arena_w // 2
                cy   = arena_y + arena_h // 2
                base = (self.minigame_spawn_timer * 0.15) % (2 * math.pi)
                for offset in [0, math.pi]:
                    angle = base + offset
                    spd   = 3.5
                    self.minigame_projectiles.append({
                        "x": float(cx), "y": float(cy),
                        "vx": spd*math.cos(angle), "vy": spd*math.sin(angle),
                        "size": 7.0, "color": (168, 85, 247),
                        "angle": angle, "speed": spd, "type": "spiral",
                    })

        elif self.minigame_pattern == "rocas":
            rate = 12 if self.minigame_attack_name == "Aplastamiento de Puño" else 18
            if self.minigame_spawn_timer % rate == 0:
                rx = random.randint(arena_x + 15, arena_x + arena_w - 15)
                self.minigame_projectiles.append({
                    "x": float(rx), "y": float(arena_y - 15),
                    "vx": 0.0, "vy": random.uniform(3.5, 6.0),
                    "size": random.uniform(10.0, 16.0), "color": (245, 158, 11),
                })

        elif self.minigame_pattern == "espejo":
            if self.minigame_spawn_timer % 30 == 0:
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    bx = random.randint(arena_x, arena_x + arena_w); by = arena_y - 15
                elif side == "bottom":
                    bx = random.randint(arena_x, arena_x + arena_w); by = arena_y + arena_h + 15
                elif side == "left":
                    bx = arena_x - 15; by = random.randint(arena_y, arena_y + arena_h)
                else:
                    bx = arena_x + arena_w + 15; by = random.randint(arena_y, arena_y + arena_h)
                ddx  = self.minigame_player_x - bx
                ddy  = self.minigame_player_y - by
                dist = math.sqrt(ddx**2 + ddy**2)
                vx   = (ddx / dist * 4.5) if dist > 0 else 0.0
                vy   = (ddy / dist * 4.5) if dist > 0 else 4.5
                self.minigame_projectiles.append({
                    "x": float(bx), "y": float(by),
                    "vx": vx, "vy": vy, "size": 8.0, "color": (239, 68, 68),
                })

        for proj in self.minigame_projectiles[:]:
            if proj.get("type") == "spiral":
                proj["angle"] += 0.03
                proj["vx"] = proj["speed"] * math.cos(proj["angle"])
                proj["vy"] = proj["speed"] * math.sin(proj["angle"])

            proj["x"] += proj["vx"]
            proj["y"] += proj["vy"]

            if (proj["x"] < arena_x - 50 or proj["x"] > arena_x + arena_w + 50 or
                    proj["y"] < arena_y - 50 or proj["y"] > arena_y + arena_h + 50):
                self.minigame_projectiles.remove(proj)
                continue

            dist = math.sqrt((proj["x"] - self.minigame_player_x)**2 +
                             (proj["y"] - self.minigame_player_y)**2)
            if dist < (4.0 + proj["size"] - 1.0):
                self.minigame_hits += 1
                if self.minigame_sfx_hit:
                    self.minigame_sfx_hit.play()
                self.floating_texts.append(
                    FloatingText("¡GOLPE!", self.minigame_player_x,
                                 self.minigame_player_y - 15, COLOR_DANGER))
                self.minigame_projectiles.remove(proj)
                self.shake_intensity = 6

        self.minigame_timer -= 1
        if self.minigame_timer <= 0:
            self.end_minigame()

    def draw_minigame(self):
        if self.minigame_type == "final_strike":
            self.draw_final_strike()
        else:
            self._draw_dodge()

    def _draw_dodge(self):
        bg = self.bg_jungle
        if self.current_scene_index == 3: bg = self.bg_swamp
        elif self.current_scene_index == 4: bg = self.bg_mountain
        elif self.current_scene_index == 5: bg = self.bg_cave

        self.screen.blit(bg, (0, 0))
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((15, 23, 42, 180))
        self.screen.blit(dim, (0, 0))

        arena_w = 500
        arena_h = 350
        arena_x = (SCREEN_WIDTH  - arena_w) // 2
        arena_y = (SCREEN_HEIGHT - arena_h) // 2
        arena_r = pygame.Rect(arena_x, arena_y, arena_w, arena_h)

        pulse    = 2 + math.sin(pygame.time.get_ticks() * 0.007) * 0.5
        color    = self.minigame_boss_color

        pygame.draw.rect(self.screen, (5, 5, 8), arena_r)
        pygame.draw.rect(self.screen, color, arena_r,
                         width=int(4 + pulse), border_radius=4)

        for proj in self.minigame_projectiles:
            px, py, ps = int(proj["x"]), int(proj["y"]), int(proj["size"])
            pygame.draw.circle(self.screen, proj["color"], (px, py), ps)
            pygame.draw.circle(self.screen, (255, 255, 255), (px, py), max(1, ps - 3))

        plx = int(self.minigame_player_x)
        ply = int(self.minigame_player_y)
        heart = pygame.Surface((24, 24), pygame.SRCALPHA)
        pixels = [
            (2,0),(3,0),(8,0),(9,0),
            (1,1),(2,1),(3,1),(4,1),(7,1),(8,1),(9,1),(10,1),
            (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),
            (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),
            (0,4),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),
            (1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),
            (2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),
            (3,7),(4,7),(5,7),(6,7),(7,7),(8,7),
            (4,8),(5,8),(6,8),(7,8),
            (5,9),(6,9),
        ]
        for hx, hy in pixels:
            pygame.draw.rect(heart, (239, 68, 68), (hx*2, hy*2, 2, 2))
        pygame.draw.rect(heart, (255, 255, 255), (4,  2, 2, 2))
        pygame.draw.rect(heart, (255, 255, 255), (16, 2, 2, 2))
        self.screen.blit(heart, (plx - 12, ply - 10))
        pygame.draw.circle(self.screen, (74, 222, 128), (plx, ply), 4)
        pygame.draw.circle(self.screen, (255, 255, 255), (plx, ply), 2)

        title_surf = self.font_ui.render(self.minigame_attack_name.upper(), True, color)
        self.screen.blit(title_surf,
                         (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, arena_y - 65))
        hint_surf = self.font_small.render("¡ESQUIVA! Hitbox: Punto Verde",
                                           True, COLOR_TEXT_MUTED)
        self.screen.blit(hint_surf,
                         (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, arena_y - 35))

        bar_w, bar_h = 400, 10
        bx = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = arena_y + arena_h + 25
        pygame.draw.rect(self.screen, (30, 41, 59), (bx, bar_y, bar_w, bar_h),
                         border_radius=4)
        pygame.draw.rect(self.screen, COLOR_PRIMARY,
                         (bx, bar_y, int(bar_w * self.minigame_timer / self.minigame_duration),
                          bar_h), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_TEXT, (bx, bar_y, bar_w, bar_h),
                         width=1, border_radius=4)

        hits_color = COLOR_DANGER if self.minigame_hits > 0 else COLOR_PRIMARY
        hits_surf  = self.font_ui.render(f"Impactos: {self.minigame_hits}",
                                         True, hits_color)
        self.screen.blit(hits_surf,
                         (SCREEN_WIDTH // 2 - hits_surf.get_width() // 2, bar_y + 20))

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

    def end_minigame(self):
        """End the DODGE mini-game (not final_strike)."""
        self.minigame_active = False
        if self.minigame_bgm:
            self.minigame_bgm.stop()

        if self.minigame_hits == 0:
            final_damage = 0
            self.add_combat_log("¡Esquiva perfecta! Bloqueas el 100% del daño del ataque.")
            self.floating_texts.append(
                FloatingText("¡ESQUIVA PERFECTA!", 270, 320, COLOR_PRIMARY))
        elif self.minigame_hits == 1:
            final_damage = int(self.minigame_base_damage * 0.5)
            self.add_combat_log(
                f"Esquivaste la mayoría. Recibes 50% de daño ({final_damage} HP).")
        else:
            final_damage = self.minigame_base_damage
            self.add_combat_log(
                f"¡Fuiste acribillado! Recibes {final_damage} de daño completo.")

        if self.combat_effects["shielded"] and not self.has_improved_shield:
            if self.minigame_attack_name == "Terremoto Terrestre":
                final_damage = int(final_damage * 0.60)
                self.add_combat_log("Tu escudo básico mitiga algo del terremoto (40% menos).")
            else:
                final_damage = int(final_damage * 0.35)
                self.add_combat_log("Tu escudo básico mitiga 65% del daño resultante.")
            self.combat_effects["shielded"] = False

        if final_damage > 0:
            self.player_hp = max(0, self.player_hp - final_damage)
            self.floating_texts.append(
                FloatingText(f"-{final_damage}", 270, 320, COLOR_DANGER))
            self.shake_intensity  = 15
            self.flash_screen_red = 200

        pygame.mixer.music.unpause()

        if self.player_hp <= 0:
            self.state = STATE_GAMEOVER
        else:
            self.state        = STATE_BATTLE
            self.battle_turn  = "PLAYER"
            self.battle_phase = "SELECT"
            self.player_energy = min(self.player_max_energy, self.player_energy + 1)
            self.add_combat_log("¡Tu turno! Recuperas +1 de Energía.")
