import random
from constants import (SCREEN_WIDTH, COLOR_DANGER, COLOR_WARNING, COLOR_TEXT_MUTED,
                       COLOR_PRIMARY, COLOR_ACCENT, COLOR_TEXT)
from entities import FloatingText


class CombatMixin:

    def reset_player_stats(self):
        self.player_hp         = 100
        self.player_max_hp     = 100
        self.player_energy     = 3
        self.player_max_energy = 3

        self.has_improved_shield = False
        self.has_teleport        = False
        self.has_bombs           = False

        self.shield_upgrade = None
        self.tp_upgrade     = None
        self.bomb_upgrade   = None

        self.combat_effects = {
            "shielded":         False,
            "tpd":              False,
            "bomb_timer":       0,
            "boss_bomb_timer":  0,
            "burn_turns":       0,
            "player_burn_turns": 0,
        }

    def init_battle(self):
        self.combat_effects["shielded"]          = False
        self.combat_effects["tpd"]               = False
        self.combat_effects["bomb_timer"]        = 0
        self.combat_effects["boss_bomb_timer"]   = 0
        self.combat_effects["burn_turns"]        = 0
        self.combat_effects["player_burn_turns"] = 0

        self.player_energy   = self.player_max_energy
        self.battle_animations = []

        self.current_boss = self.boss_data[self.current_scene_index - 1]
        self.current_boss["hp"] = self.current_boss["max_hp"]

        self.combat_log = [
            f"Un enfrentamiento a muerte comienza contra el {self.current_boss['name']}.",
            "¡Tu turno! Elige una acción táctica."
        ]

        self.battle_turn  = "PLAYER"
        self.battle_phase = "SELECT"
        self.battle_timer = 0
        self.selected_action_index = 0

        self.player_visual_x = 150
        self.boss_visual_x   = SCREEN_WIDTH - 400
        self.player_offset_x = 0
        self.boss_offset_x   = 0

        # Reset mirror-boss flags (bug: used to persist between battles)
        self.boss_charged  = False
        self.boss_shielded = False
        self.boss_tpd      = False
        self.final_strike_triggered = False

        # Reset animation state
        self.player_attack_anim  = 0.0
        self.boss_attack_anim    = 0.0
        self.player_squash_timer = 0
        self.boss_squash_timer   = 0
        self.player_offset_y     = 0
        self.boss_offset_y       = 0

        music_tracks = {
            2: "hambiente-junga.mp3",
            3: "assets/video/jungle_music.mp3",
            4: "assets/video/jungle_music.mp3",
            5: "hambiente-junga.mp3",
        }
        track = music_tracks.get(self.current_scene_index)
        if track:
            self.play_music(track)

    def get_player_actions(self):
        actions = []

        actions.append({
            "name":   "Ataque Espada",
            "energy": 1,
            "prob":   90,
            "desc":   "Un tajo preciso con tu espada. Inflige 15-20 de daño físico."
        })

        if self.has_improved_shield:
            shield_name = "Escudo Mejorado"
            shield_desc = "Bloquea el 100% del daño del próximo ataque recibido."
            if self.shield_upgrade == "spiked":
                shield_name = "Escudo Espinas"
                shield_desc = "Bloquea el 100% del daño y refleja 50% de daño al atacante."
            elif self.shield_upgrade == "rejuvenating":
                shield_name = "Escudo Rejuve."
                shield_desc = "Bloquea el 100% del daño y te cura 10 HP al activarse."
            actions.append({"name": shield_name, "energy": 1,
                            "prob": 100, "desc": shield_desc})
        else:
            actions.append({
                "name":   "Bloqueo Básico",
                "energy": 0,
                "prob":   100,
                "desc":   "Te cubres detrás de tu escudo básico. Reduce 50% del daño del siguiente ataque."
            })

        if self.has_teleport:
            tp_name = "Teletransporte"
            tp_desc = "Esquiva completamente el siguiente ataque del jefe."
            if self.tp_upgrade == "counter":
                tp_name = "TP Contra"
                tp_desc = "Esquiva el ataque y realiza un corte sorpresa de 20 de daño."
            elif self.tp_upgrade == "recharge":
                tp_name = "TP Recarga"
                tp_desc = "Esquiva el ataque y recupera +2 de energía en el acto."
            actions.append({"name": tp_name, "energy": 2,
                            "prob": 100, "desc": tp_desc})

        if self.has_bombs:
            bomb_name = "Bomba Reloj"
            bomb_desc = "Planta una bomba que explota tras 1 turno infligiendo 55 de daño."
            if self.bomb_upgrade == "fire":
                bomb_name = "Bomba Ígnea"
                bomb_desc = "Detona al siguiente turno. Hace 40 de daño e inflige Quemadura (10/turno por 3 turnos)."
            elif self.bomb_upgrade == "mega":
                bomb_name = "Gran Mega Bomba"
                bomb_desc = "Detona al siguiente turno infligiendo 75 de daño masivo."
            actions.append({"name": bomb_name, "energy": 2,
                            "prob": 100, "desc": bomb_desc})

        return actions

    def add_combat_log(self, text):
        self.combat_log.append(text)
        if len(self.combat_log) > 5:
            self.combat_log.pop(0)

    # -------------------------------------------------------- player actions
    def execute_player_action(self, action):
        if self.player_energy < action["energy"]:
            self.add_combat_log("¡No tienes suficiente Energía para esa acción!")
            return False

        self.player_energy      -= action["energy"]
        self.player_attack_anim  = 0.01   # arc start (Principles 6 & 7)

        roll = random.randint(1, 100)
        if roll > action["prob"]:
            self.floating_texts.append(
                FloatingText("¡Falló!", SCREEN_WIDTH - 270, 200, COLOR_TEXT_MUTED))
            self.add_combat_log("¡Tu ataque ha fallado en la niebla!")
            return True

        action_name = action["name"]

        if "Espada" in action_name:
            # Mirror dodge check
            if self.current_scene_index == 5 and getattr(self, "boss_tpd", False):
                self.boss_tpd = False
                self.floating_texts.append(
                    FloatingText("¡Esquivado!", SCREEN_WIDTH - 270, 200, COLOR_ACCENT))
                self.add_combat_log(
                    "¡El Caballero Oscuro se teletransporta en humo y esquiva tu golpe!")
                return True

            damage = random.randint(15, 20)

            # Mirror shield check
            if self.current_scene_index == 5 and getattr(self, "boss_shielded", False):
                self.boss_shielded = False
                reflected = max(1, damage // 2)
                self.current_boss["hp"] = max(0, self.current_boss["hp"] - reflected)
                self.floating_texts.append(
                    FloatingText(f"-{reflected} Bloqueado", SCREEN_WIDTH - 270, 200,
                                 COLOR_TEXT_MUTED))
                self.boss_squash_timer = 6
                self.add_combat_log(
                    f"¡El Caballero Oscuro bloquea tu espada! Solo infliges {reflected} de daño.")
                return True

            # Golem armor reduction
            if self.current_scene_index == 4:
                damage = max(5, damage - 5)
                self.add_combat_log("La armadura rocosa del Gólem reduce el daño recibido.")

            self.current_boss["hp"] = max(0, self.current_boss["hp"] - damage)
            self.floating_texts.append(
                FloatingText(f"-{damage}", SCREEN_WIDTH - 270, 200, COLOR_DANGER))
            self.boss_squash_timer = 8
            self.shake_intensity   = 15
            self.play_sfx(self.sfx_hit)
            self.add_combat_log(f"Atacas con tu espada e infliges {damage} de daño al jefe.")

            boss_cx = self.boss_visual_x + 128
            boss_cy = 220 + 128
            self.battle_animations.append(
                {"type": "slash", "x": boss_cx, "y": boss_cy, "timer": 0, "max_frames": 12})
            self.battle_animations.append(
                {"type": "hit",   "x": boss_cx, "y": boss_cy, "timer": 0, "max_frames": 15})

        elif "Escudo" in action_name or "Bloqueo" in action_name:
            self.combat_effects["shielded"] = True
            self.floating_texts.append(FloatingText("¡Bloqueo!", 270, 320, COLOR_PRIMARY))
            self.play_sfx(self.sfx_shield)
            self.add_combat_log(
                f"Te preparas en posición defensiva usando tu {action_name}.")

            pcx = self.player_visual_x + 128
            pcy = 220 + 128
            self.battle_animations.append(
                {"type": "block", "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})

        elif "Teletransporte" in action_name or "TP" in action_name:
            self.combat_effects["tpd"] = True
            self.floating_texts.append(FloatingText("¡Evasión!", 270, 320, COLOR_ACCENT))
            self.play_sfx(self.sfx_magic)
            self.add_combat_log(
                "Activas teletransportación. Esquivarás el siguiente golpe.")

            pcx = self.player_visual_x + 128
            pcy = 220 + 128
            self.battle_animations.append(
                {"type": "block", "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})

        elif "Bomba" in action_name:
            self.combat_effects["bomb_timer"] = 2
            self.floating_texts.append(
                FloatingText("¡Bomba!", SCREEN_WIDTH - 270, 250, COLOR_WARNING))
            self.play_sfx(self.sfx_magic)
            self.add_combat_log("¡Plantas una bomba temporizada a los pies del jefe!")

            boss_cx = self.boss_visual_x + 128
            boss_cy = 220 + 200
            self.battle_animations.append(
                {"type": "hit", "x": boss_cx, "y": boss_cy, "timer": 0, "max_frames": 15})

        return True

    # --------------------------------------------------------- boss AI
    def execute_boss_turn(self):
        self.boss_attack_anim = 0.01   # arc start

        if self.current_scene_index == 2:   # Guardián del Puerto
            if getattr(self, "boss_charged", False):
                self.boss_charged = False
                self.execute_boss_attack("Golpe de Ola Devastador", 28, 90)
            else:
                roll = random.random()
                if roll < 0.4:
                    self.boss_charged = True
                    self.add_combat_log("El Guardián del Puerto junta fuerza... El mar ruge.")
                else:
                    self.execute_boss_attack("Zarpazo Rápido", 12, 85)

        elif self.current_scene_index == 3:  # Mago Magaxo
            if getattr(self, "boss_charged", False):
                self.boss_charged = False
                self.execute_boss_attack("Desintegración Arcana", 35, 95)
            else:
                roll = random.random()
                if roll < 0.35:
                    self.boss_charged = True
                    self.add_combat_log("Magaxo canaliza un rayo desintegrador brillante...")
                elif roll < 0.7:
                    shield_val = 20
                    self.current_boss["hp"] = min(
                        self.current_boss["max_hp"], self.current_boss["hp"] + shield_val)
                    self.floating_texts.append(
                        FloatingText(f"+{shield_val} Barrera",
                                     SCREEN_WIDTH - 270, 200, COLOR_ACCENT))
                    self.add_combat_log("Magaxo invoca una barrera mágica que absorbe daño (sana).")
                else:
                    self.execute_boss_attack("Proyectil Arcano", 15, 85)

        elif self.current_scene_index == 4:  # Gólem de Piedra
            if getattr(self, "boss_charged", False):
                self.boss_charged = False
                self.execute_boss_attack("Aplastamiento de Puño", 45, 90)
            else:
                roll = random.random()
                if roll < 0.3:
                    self.boss_charged = True
                    self.add_combat_log("El colosal Gólem levanta sus masivos puños de piedra...")
                elif roll < 0.65:
                    self.execute_boss_attack("Terremoto Terrestre", 26, 90,
                                             ignore_basic_block=True)
                else:
                    self.execute_boss_attack("Lanzamiento de Roca", 18, 85)

        elif self.current_scene_index == 5:  # Caballero Oscuro (Espejo)
            bomb_exploded = False
            if self.combat_effects["boss_bomb_timer"] > 0:
                self.combat_effects["boss_bomb_timer"] -= 1
                if self.combat_effects["boss_bomb_timer"] == 0:
                    bomb_exploded = True
                    damage = 75 if self.bomb_upgrade == "mega" else 55
                    if self.combat_effects["tpd"]:
                        self.combat_effects["tpd"] = False
                        self.floating_texts.append(
                            FloatingText("¡Esquivado!", 270, 320, COLOR_ACCENT))
                        self.play_sfx(self.sfx_magic)
                        self.add_combat_log(
                            "¡Te teletransportas y esquivas la bomba oscura a tiempo!")
                    elif self.combat_effects["shielded"]:
                        self.combat_effects["shielded"] = False
                        self.play_sfx(self.sfx_shield)
                        if self.has_improved_shield:
                            self.floating_texts.append(
                                FloatingText("¡Bloqueado!", 270, 320, COLOR_PRIMARY))
                            self.add_combat_log(
                                "¡Tu escudo absorbe la explosión de la bomba oscura!")
                            if self.shield_upgrade == "rejuvenating":
                                self.player_hp = min(self.player_max_hp, self.player_hp + 10)
                                self.floating_texts.append(
                                    FloatingText("+10 HP", 270, 360, COLOR_PRIMARY))
                        else:
                            reduced = damage // 2
                            self.player_hp = max(0, self.player_hp - reduced)
                            self.player_squash_timer = 5
                            self.floating_texts.append(
                                FloatingText(f"-{reduced}", 270, 320, COLOR_DANGER))
                            self.shake_intensity = 12
                            self.add_combat_log(
                                f"Tu escudo mitiga la explosión. Recibes {reduced} de daño.")
                    else:
                        self.player_hp = max(0, self.player_hp - damage)
                        self.floating_texts.append(
                            FloatingText(f"-{damage}", 270, 320, COLOR_DANGER))
                        self.player_squash_timer = 8
                        self.shake_intensity     = 20
                        self.flash_screen_red    = 200
                        self.play_sfx(self.sfx_magic)
                        self.add_combat_log(
                            f"¡La bomba oscura explota infligiendo {damage} de daño!")
                    if self.bomb_upgrade == "fire" and not self.combat_effects["tpd"]:
                        self.combat_effects["player_burn_turns"] = 3

            if not bomb_exploded:
                roll = random.random()
                if roll < 0.4:
                    damage = random.randint(15, 20)
                    self.execute_boss_attack("Espada Oscura", damage, 90)
                elif roll < 0.6:
                    self.boss_shielded = True
                    self.floating_texts.append(
                        FloatingText("¡Escudo Oscuro!", SCREEN_WIDTH - 270, 200, COLOR_PRIMARY))
                    self.play_sfx(self.sfx_shield)
                    self.add_combat_log(
                        "El Caballero Oscuro se alza detrás de su escudo corrupto.")
                elif roll < 0.8:
                    self.boss_tpd = True
                    self.floating_texts.append(
                        FloatingText("¡Esquiva Oscura!", SCREEN_WIDTH - 270, 200, COLOR_ACCENT))
                    self.play_sfx(self.sfx_magic)
                    self.add_combat_log(
                        "Tu copia se teletransporta en ráfagas de humo oscuro.")
                else:
                    self.combat_effects["boss_bomb_timer"] = 2
                    self.floating_texts.append(
                        FloatingText("¡Bomba Oscura!", 270, 320, COLOR_WARNING))
                    self.add_combat_log(
                        "¡El Caballero Oscuro planta una bomba oscura a tus pies!")

    # ------------------------------------------------------- boss attack resolver
    def execute_boss_attack(self, attack_name, damage, prob, ignore_basic_block=False):
        roll = random.randint(1, 100)
        if roll > prob:
            self.floating_texts.append(
                FloatingText("¡Falló!", 270, 320, COLOR_TEXT_MUTED))
            self.add_combat_log(
                f"El ataque '{attack_name}' del jefe falló en las sombras.")
            return

        pcx = self.player_visual_x + 128
        pcy = 220 + 128

        # 1. TP evasion
        if self.combat_effects["tpd"]:
            self.combat_effects["tpd"] = False
            self.floating_texts.append(
                FloatingText("¡Esquivado!", 270, 320, COLOR_ACCENT))
            self.play_sfx(self.sfx_magic)
            self.add_combat_log("¡Te teletransportas y esquivas completamente el golpe!")
            self.battle_animations.append(
                {"type": "block", "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})

            if self.tp_upgrade == "counter":
                self.current_boss["hp"] = max(0, self.current_boss["hp"] - 20)
                self.floating_texts.append(
                    FloatingText("-20 Contra", SCREEN_WIDTH - 270, 200, COLOR_DANGER))
                self.add_combat_log(
                    "¡Realizas un contraataque inmediato infligiendo 20 de daño!")
                bcx = self.boss_visual_x + 128
                bcy = 220 + 128
                self.battle_animations.append(
                    {"type": "slash", "x": bcx, "y": bcy, "timer": 0, "max_frames": 12})
                self.battle_animations.append(
                    {"type": "hit",   "x": bcx, "y": bcy, "timer": 0, "max_frames": 15})
            elif self.tp_upgrade == "recharge":
                self.player_energy = min(self.player_max_energy, self.player_energy + 2)
                self.add_combat_log("¡El esquive oportuno te devuelve +2 de Energía!")
            return

        # 2. Improved shield — full block
        if self.combat_effects["shielded"] and self.has_improved_shield:
            self.combat_effects["shielded"] = False
            self.floating_texts.append(
                FloatingText("¡Bloqueado!", 270, 320, COLOR_PRIMARY))
            self.play_sfx(self.sfx_shield)
            self.add_combat_log("¡Bloqueas el 100% del daño del ataque del jefe!")
            self.battle_animations.append(
                {"type": "block", "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})

            if self.shield_upgrade == "spiked":
                reflected = int(damage * 0.5)
                self.current_boss["hp"] = max(0, self.current_boss["hp"] - reflected)
                self.floating_texts.append(
                    FloatingText(f"-{reflected} Reflejo",
                                 SCREEN_WIDTH - 270, 200, COLOR_DANGER))
                self.add_combat_log(
                    f"¡El escudo de espinas refleja {reflected} de daño al jefe!")
                bcx = self.boss_visual_x + 128
                bcy = 220 + 128
                self.battle_animations.append(
                    {"type": "hit", "x": bcx, "y": bcy, "timer": 0, "max_frames": 15})
            elif self.shield_upgrade == "rejuvenating":
                self.player_hp = min(self.player_max_hp, self.player_hp + 10)
                self.floating_texts.append(
                    FloatingText("+10 HP", 270, 320, COLOR_PRIMARY))
                self.add_combat_log(
                    "¡El escudo restaurador regenera 10 de tus puntos de vida!")
            return

        # 3. Special attacks → trigger mini-game (basic shield still active = reduction later)
        special_attacks = {
            "Golpe de Ola Devastador": ("olas",    (56, 189, 248)),
            "Desintegración Arcana":   ("espiral", (168, 85, 247)),
            "Terremoto Terrestre":     ("rocas",   (245, 158, 11)),
            "Aplastamiento de Puño":   ("rocas",   (245, 158, 11)),
            "Espada Oscura":           ("espejo",  (239, 68, 68)),
        }
        if attack_name in special_attacks:
            pattern, color = special_attacks[attack_name]
            self.start_minigame(attack_name, damage, pattern, color)
            return

        # 4. Basic shield — partial block
        if self.combat_effects["shielded"]:
            self.combat_effects["shielded"] = False
            self.play_sfx(self.sfx_shield)
            self.battle_animations.append(
                {"type": "block", "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})

            if ignore_basic_block:
                reduced = int(damage * 0.60)
                self.player_hp = max(0, self.player_hp - reduced)
                self.floating_texts.append(
                    FloatingText(f"-{reduced} TIERRA", 270, 320, COLOR_DANGER))
                self.player_squash_timer = 6
                self.shake_intensity     = 12
                self.flash_screen_red    = 150
                self.add_combat_log(
                    f"¡El Terremoto traspasa tu escudo básico! Recibes {reduced} de daño.")
            else:
                reduced = int(damage * 0.35)
                self.player_hp = max(0, self.player_hp - reduced)
                self.floating_texts.append(
                    FloatingText(f"-{reduced} BLOQ.", 270, 320, COLOR_WARNING))
                self.player_squash_timer = 3
                self.shake_intensity     = 5
                self.flash_screen_red    = 60
                self.add_combat_log(
                    f"¡Escudo básico! Reduces el 65% del daño. Solo recibes {reduced}.")

            self.battle_animations.append(
                {"type": "boss_slash", "x": pcx, "y": pcy, "timer": 0, "max_frames": 12})
            self.battle_animations.append(
                {"type": "hit",        "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})
            return

        # 5. Direct hit — Exaggeration (Principle 10)
        self.player_hp = max(0, self.player_hp - damage)
        self.floating_texts.append(FloatingText(f"-{damage}", 270, 320, COLOR_DANGER))
        self.player_squash_timer = 8
        self.shake_intensity     = 18
        self.flash_screen_red    = 200

        magic_keywords = ("Arcano", "Desintegración", "Proyectil", "Oscura", "Teletransporte")
        if any(w in attack_name for w in magic_keywords):
            self.play_sfx(self.sfx_magic)
        else:
            self.play_sfx(self.sfx_hit)

        self.add_combat_log(
            f"¡Recibes un golpe directo de '{attack_name}' e infliges {damage} de daño!")
        self.battle_animations.append(
            {"type": "boss_slash", "x": pcx, "y": pcy, "timer": 0, "max_frames": 12})
        self.battle_animations.append(
            {"type": "hit",        "x": pcx, "y": pcy, "timer": 0, "max_frames": 15})
