import pygame
import sys
import os
pygame.init()

WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

try:
    font = pygame.font.Font('PakenhamBl Italic.ttf',32)
    big_font = pygame.font.Font('PakenhamBl Italic.ttf',64)
except:
    font = pygame.font.Font(None, 32)
    big_font = pygame.font.Font(None, 64)

GRAVITY = 0.8
LEVEL_WIDTH = 2200

ASSET_DIR = "assets/images"

def load_image(names, size, use_alpha=True):
    for name in names:
        path = os.path.join(ASSET_DIR, name)
        if os.path.exists(path):
            if use_alpha:
                img = pygame.image.load(path).convert_alpha()
            else:
                img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, size)

player_img = load_image(["Red.png","photo_2026-02-12_22-45-01.png"], (40, 50))
enemy_img = load_image(["pig.png","images.png"], (40, 40))
platform_img = load_image(["Brevno.png"], (80, 40))
portal_img = load_image(["portal.png"], (40, 60))
coin_frames = [
    load_image(["coin1.png"], (20, 20)),
    load_image(["coin2.png"], (20, 20)),
    load_image(["coin3.png"], (20, 20)),
    load_image(["coin4.png"], (20, 20)),
]

def draw_tiled_platform(surf, rect, camera_x=0):
    tile = pygame.transform.scale(platform_img, (80, rect.h))
    x = rect.x - camera_x

    for tile_x in range(x, x + rect.w, tile.get_width()):
        surf.blit(tile, (tile_x, rect.y))


class Platform:

    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)

    def draw(self,surf,camera_x=0):
        draw_tiled_platform(surf, self.rect, camera_x)

class Coin:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.timer = 0
        self.frame = 0

    def update(self):
        self.timer += 1

        if self.timer >= 20:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(coin_frames):
                self.frame = 0

    def draw(self, surf, camera_x = 0):
        surf.blit(coin_frames[self.frame],(self.rect.x - camera_x,self.rect.y))

class Enemy:
    def __init__(self,x,y,left_limit,right_limit):
        self.rect =pygame.Rect(x, y, 40, 40)
        self.speed = 3
        self.dir = 1
        self.left_limit = left_limit
        self.right_limit = right_limit

    def update(self):
        self.rect.x += self.speed * self.dir

        if self.rect.left <= self.left_limit or self.rect.right >= self.right_limit:
            self.dir *= -1

    def draw(self,surf,camera_x = 0):
        surf.blit(enemy_img, (self.rect.x - camera_x, self.rect.y))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(60,300,40,50)

        self.vel_y = 0
        self.speed = 5
        self.on_ground = False

        self.lives = 3
        self.invuln = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -14
            self.on_ground = False

    def hit(self):
        if self.invuln == 0:
            self.lives -= 1
            self.vel_y = -10
            self.invuln = 60

    def update(self,platforms):
        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed

        #движение по x
        self.rect.x += dx

        #не уходит за левую границу
        if self.rect.left < 0:
            self.rect.left = 0

        #граница мира
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

        #гравитация
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        self.on_ground = False

        for p in platforms:
            if  self.rect.colliderect(p.rect) and self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.top > HEIGHT:
            self.lives = 0

        if self.invuln > 0:
            self.invuln -= 1

    def draw(self,surf,camera_x=0):
        if self.invuln > 0 and (self.invuln % 10) < 5:
            return
        surf.blit(player_img, (self.rect.x - camera_x, self.rect.y))

class Game:
    def __init__(self):
        self.reset()
    def reset(self):
        self.player = Player()
        self.platforms = [
            Platform(0,HEIGHT - 40,LEVEL_WIDTH,40),

            Platform(140,330,180,20),
            Platform(380,260,160,20),
            Platform(610,320,140,20),

            Platform(900,300,200,20),
            Platform(1200,250,200,20),
            Platform(1500,380,220,20),
            Platform(1800,280,220,20)
        ]
        self.coins = [
            Coin(200,300),
            Coin(430,230),
            Coin(660,290),

            Coin(980,270),
            Coin(1260,220),
            Coin(1560,310),
            Coin(1900,250)
        ]

        self.total_coins = len(self.coins)

        self.enemies = [
            Enemy(170,290,140,320),
            Enemy(420,220,380,540),

            Enemy(930,260,900,1100),
            Enemy(1530,300,1500,1680)
        ]
        #счёт
        self.score = 0
        self.game_over = False
        #камера
        self.camera_x = 0
        #финиш
        self.finish = pygame.Rect(2050,HEIGHT - 100,40,60)

    def collect_coins(self):
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.coins.remove(c)
                self.score +=1

    def enemy_hits(self):
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                 self.player.hit()

    def check_finish(self):
        if self.player.rect.colliderect(self.finish):
            self.win = True

    def update_camera(self):
        self.camera_x = max(
            0,
            min(self.player.rect.centerx - WIDTH // 2, LEVEL_WIDTH - WIDTH)
        )
    def draw_finish(self):
        screen.blit(portal_img,(self.finish.x - self.camera_x, self.finish.y))

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.game_over and not self.win:
                       self.player.jump()

                    if event.key == pygame.K_r and (self.game_over or self.win):
                        self.reset()
            if not self.game_over and not self.win:
                self.player.update(self.platforms)

                for e in self.enemies:
                    e.update()

                for c in self.coins:
                    c.update()

                self.enemy_hits()
                self.collect_coins()
                self.check_finish()

                if self.player.lives <= 0:
                    self.game_over = True

                self.update_camera()

            for p in self.platforms:
                p.draw(screen,self.camera_x)

            for c in self.coins:
                c.draw(screen,self.camera_x)

            for e in self.enemies:
                e.draw(screen,self.camera_x)

            self.draw_finish()

            self.player.draw(screen,self.camera_x)

            screen.blit(font.render(f"Score: {self.score}", True, (0, 0, 0)), (10, 10))
            screen.blit(font.render(f"Lives: {self.player.lives}", True, (0, 0, 0)), (10, 40))

            if self.game_over:
                t1 = big_font.render("Ты проиграл", True, (200, 0, 0))
                t2 = font.render("Press R to restart", True, (0, 0, 0))

                screen.blit(t1, t1.get_rect(center=(WIDTH // 2,HEIGHT // 2 - 20)))
                screen.blit(t2, t2.get_rect(center=(WIDTH // 2,HEIGHT // 2 + 25)))

            if self.win:
                t1 = big_font.render("Ты победил!", True, (0, 150, 0))
                t2 = font.render("Press R to restart", True, (0, 0, 0))
                t3 = font.render(
                    f"Score: {self.score} / {self.total_coins}",
                    True,
                    (0, 0, 0)
                )

                screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
                screen.blit(t3, t3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
                screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

Game().run()