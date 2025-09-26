import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

# screen size
screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# define score text
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 170
pipe_freq = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False

# load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

# Score Func
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# define reset game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flappy.vel = 0
    global game_over, flying, score
    game_over = False
    flying = False
    score = 0
    return score


# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True: 
            # gravity
            self.apply_gravity()
        
        if game_over == False:
            # jump
            if pygame.key.get_pressed()[K_SPACE] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.key.get_pressed()[K_SPACE] == 0:
                self.clicked = False

            # handle animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
    
    def apply_gravity(self):
        self.vel += 0.5
        if self.vel > 10:
            self.vel = 10
        self.rect.y += int(self.vel)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # position 1 is top, -1 is bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
    
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):

        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

# add flappy to group
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    # draw background 
    screen.blit(bg, (0, 0))

    # draw groups
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # draw ground
    screen.blit(ground_img, (ground_scroll, 768))

    # check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # check if bird has hit ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if game_over == False and flying == True:

        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # check for game over
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    # stop / start game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.flip()

pygame.quit()