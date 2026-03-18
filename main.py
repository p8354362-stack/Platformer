import pygame
import sys
pygame.init()

WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")
clock = pygame.time.Clock()

try:
    font = pygame.font.Font('FNAF Pixel One.zip',32)
    big_font = pygame.font.Font('FNAF Pixel One.zip',64)
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
        self.rect = pygame.Rect(x, y, 30, 30)

    def draw(self, surf, camera_x = 0):
        pygame.draw.circle(surf,(73, 31, 115), (self.rect.centrex - camera_x,self.rect.centery),20)

class Enemy:
    def __init__(self,x,y,left_limit,right_limit):
        self.rect =pygame.Rect(x, y, 40, 40)
        self.speed = 3
        self.dir = 1
        self.left_limit = left_limit
        self.right_limit = right_limit

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
        if self.rect.left<0:
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