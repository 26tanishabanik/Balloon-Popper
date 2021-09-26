import pygame,sys
import random
import cv2
import HandTrackingModule as htm
import time
import random
import numpy as np
pygame.init()

screen_height =800
screen_width = 1300

screen = pygame.display.set_mode((screen_width, screen_height))

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
darkGray = (40, 55, 71)
score = 0
lowerBound = 100
font = pygame.font.SysFont("Snap ITC", 50)
bursted = 0

def lowerPlatform():
    pygame.draw.rect(screen, darkGray, (0,screen_height - lowerBound, screen_width, lowerBound))

def showScore():
    scoreText = font.render("Score: " + str(score), True,(230, 230, 230))
    burstednum = font.render("Balloons Bursted : " + str(bursted), True,(230, 230, 230))
    screen.blit(scoreText, (screen_width - 800, screen_height // 2 + 350))
    screen.blit(burstednum, (screen_width - 600, screen_height // 2 + 350))


class Splash():

    def __init__(self, screen, x, y):
        self.screen = screen
        self.image = pygame.image.load('yellow.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 210))
        self.image = pygame.transform.rotozoom(self.image, 0, 1.5)
        self.visible = 12
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
    def blitme(self):
        draw_pos = self.image.get_rect().move(self.x, self.y)
        self.screen.blit(self.image, draw_pos)

class Balloon(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = balloon_img
        self.image = pygame.transform.scale(self.image, (70, 80))
        self.image = pygame.transform.rotozoom(self.image, 0, 1.9)
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(50,screen_width - 200)
        self.rect.y = random.randrange(5,screen_height - 15)
        self.speed_y = random.randrange(4,6)

    def update(self):
        self.rect.y -= self.speed_y
        if self.rect.bottom <= self.speed_y:
            if self.rect.bottom < -10:
                self.rect.x = random.randrange(50,screen_width - 50)
                self.rect.y = random.randrange(5,screen_height - 15)
                self.speed = random.randrange(3,6)

background = screen.fill((174, 214, 241))

balloon_img = pygame.image.load('green_balloon_50px.png')

all_sprites = pygame.sprite.Group()

balloons = pygame.sprite.Group()


for i in range(2):
    balloon = Balloon()
    all_sprites.add(balloon)
    balloons.add(balloon)

cap = cv2.VideoCapture(0)

fps = cap.get(cv2.CAP_PROP_FPS)

cap.set(cv2.CAP_PROP_FPS, 60)
detector = htm.handDetector(detectionCon=0.8)
clock = pygame.time.Clock()
splash = 0
while True:

    success, frame = cap.read()
    frame = cv2.resize(frame,(1300,800),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
    if not success:
        break
    

    frame = cv2.flip(frame, 1)
    
    _, frame = detector.findHands(frame)
    center_x = int(frame.shape[0]/2)
    center_y = int(frame.shape[0]/2)
    lmList, bboxInfo = detector.findPosition(frame)
    
    frame = np.fliplr(frame)
    frame = np.rot90(frame)
    

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    surf = pygame.surfarray.make_surface(frame)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    for balloon in balloons:
        
        if lmList:
            if balloon.rect.x < lmList[8][1] < balloon.rect.x + balloon.rect.w and \
                balloon.rect.y < lmList[8][2]  < balloon.rect.y + balloon.rect.h:
                
                l, _, _ = detector.findDistance(8, 4, frame)
                print("Distance: ",l)
                if l < 150:

                    score += 0.5
                    bursted += 1
                    splash = Splash(screen, balloon.rect.x - 80, balloon.rect.y-120)
                    #print(splash.rect)
                    # splash.blitme(balloon.rect.x, balloon.rect.y)
                    balloons.remove(balloon)
                    balloon = Balloon()
                    all_sprites.add(balloon)
                    balloons.add(balloon)
                

    screen.blit(surf, (0,0))
    all_sprites.update()
    all_sprites.draw(screen)
    
    if splash != 0:
        if splash.visible > 0:
            splash.blitme()
            splash.visible -= 1
    lowerPlatform()
    showScore()

    pygame.display.update()
    
    
    pygame.display.flip()
    
    clock.tick(30)
    
