import pygame
import sys
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

#ПОДГОТОВКА К КАМЕРЕ
LEVEL_WIDTH = 2200

class Platform:

    def __init__(self,x,y,w,h):
        self.rect = pygame.Rect(x,y,w,h)

    def draw(self,surf,camera_x = 0):
        pygame.draw.rect(surf,(24, 84, 30), (self.rect.x - camera_x,self.rect.y,self.rect.w,self.rect.h))

class Coin:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.timer = 0
        self.frame = 0

    def update(self):
        self.timer += 2

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
        pygame.draw.rect(surf,(220,70,70),(self.rect.x - camera_x,self.rect.y,self.rect.w,self.rect.h))

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

        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed

        #движение по x
        self.rect.x += dx

        #не уходит за левую границу
        if self.rect.left < 0:
            self.rect.left = 0

        #граница мира
        if self.rect.right>LEVEL_WIDTH:
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


    def draw(self,surf,camera_x = 0):
        if self.invuln > 0 and (self.invuln % 10) < 5:
            return
        pygame.draw.rect(surf,(80,140,225), (self.rect.x - camera_x,self.rect.y,self.rect.w,self.rect.h))

class Game:
    def __init__(self):
        self.lives = 3
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

    def lives(self):
        for l in self.lives:
            if self.player.rect.colliderect(e.rect):
                self.lives.remove(l)
                self.lives -=1

    def enemy_hits(self):
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                 self.player.hit()

    def check_finish(self):
        if self.player.rect.colliderect(self.finish):
            self.game_over = True

    def update_camera(self):
        self.camera_x = max(0, min(self.player.rect.centerx - WIDTH // 2,LEVEL_WIDTH - WIDTH))

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not self.game_over:
                       self.player.jump()

                    if event.key == pygame.K_r and self.game_over:
                        self.reset()
            if not self.game_over:
                self.player.update(self.platforms)

                for e in self.enemies:
                    e.update()

                self.enemy_hits()
                self.collect_coins()
                self.check_finish()

                if self.player.lives <= 0:
                    self.game_over = True

                self.update_camera()

            screen.fill((135,206,236))

            for p in self.platforms:
                p.draw(screen,self.camera_x)

            for c in self.coins:
                c.update()
                c.draw(screen,self.camera_x)

            for e in self.enemies:
                e.draw(screen,self.camera_x)

            pygame.draw.rect(screen,(200,200,200), (self.finish.x - self.camera_x,self.finish.y,self.finish.w,self.finish.h))

            self.player.draw(screen,self.camera_x)

            screen.blit(font.render(f"Score: {self.score}",True,(0,0,0)),(10,10))
            screen.blit(font.render(f"Lives: {self.lives}", True, (0,0,0)),(10, 40))

            if self.game_over:
                t1 = big_font.render("Game Over", True,(200,0,0))
                t2 = font.render('Rress R to restart', True,(0,0,0))

                screen.blit(t1, t1.get_rect(center=(WIDTH // 2,HEIGHT // 2 - 20)))
                screen.blit(t2, t2.get_rect(center=(WIDTH // 2,HEIGHT // 2 + 25)))

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        sys.exit()

coin_frames = [
    pygame.transform.scale(pygame.image.load('assets/images/coin1.png').convert_alpha(),(20,20)),
    pygame.transform.scale(pygame.image.load('assets/images/coin2.png').convert_alpha(),(20,20)),
    pygame.transform.scale(pygame.image.load('assets/images/coin3.png').convert_alpha(),(20,20)),
    pygame.transform.scale(pygame.image.load('assets/images/coin4.png').convert_alpha(),(20,20))
]

enemy_frames = [
    pygame.transform.scale(pygame.image.load('assets/images/pig.png').convert_alpha(),(100,100)),
    pygame.transform.scale(pygame.image.load('assets/images/images.png').convert_alpha(),(100,100))
]

Game().run()