import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_DANGER


class Particle:
    def __init__(self):
        self.x     = random.randint(0, SCREEN_WIDTH)
        self.y     = random.randint(0, SCREEN_HEIGHT)
        self.vx    = random.uniform(-0.5, 0.5)
        self.vy    = random.uniform(-1.0, -0.2)
        self.size  = random.uniform(2.0, 5.0)
        self.color = random.choice([
            (52, 211, 153, 100),
            (56, 189, 248, 100),
            (241, 245, 249, 80),
        ])
        self.life = random.randint(100, 200)

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.life -= 1
        if self.life <= 0:
            self.__init__()

    def draw(self, surface):
        part_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(part_surf, self.color,
                           (int(self.size), int(self.size)), int(self.size))
        surface.blit(part_surf, (int(self.x - self.size), int(self.y - self.size)))


class FloatingText:
    def __init__(self, text, x, y, color=COLOR_DANGER, size=32):
        self.text  = text
        self.x     = x
        self.y     = y
        self.color = color
        self.vy    = -1.5
        self.alpha = 255
        self.font  = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 10)

    def update(self):
        self.y     += self.vy
        self.alpha -= 5
        return self.alpha > 0

    def draw(self, surface):
        text_surf  = self.font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, self.alpha))
        text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(text_surf, (self.x - text_surf.get_width() // 2, self.y))
