import pygame
from pygame import *
import random

pygame.init()

CLOCK = pygame.time.Clock()
FPS = 60

# screen size
SCREEN_WIDTH = 864
SCREEN_HEIGHT = 936

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# define score text
font1 = pygame.font.SysFont('Flappy Bird Font', 60)
font2 = pygame.font.SysFont('Flappy Bird', 120)
white = (255, 255, 255)

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 170
pipe_freq = 1500
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
coin_score = []
pass_pipe = False

# Load images
bg = pygame.image.load('img/bg.png').convert_alpha()
ground_img = pygame.image.load('img/ground.png').convert_alpha()
button_img = pygame.image.load('img/restart.png').convert_alpha()

# Score function
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

# Reset game function
def reset_game():
    pipe_group.empty()
    coin_group.empty()
    coin_score.clear()
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HEIGHT / 2)
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
            img = pygame.image.load(f'img/bird{num}.png').convert_alpha()
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True: 
            # Gravity
            self.apply_gravity()
        
        if game_over == False:
            # Jump
            if pygame.key.get_pressed()[K_SPACE] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.key.get_pressed()[K_SPACE] == 0:
                self.clicked = False

            # Handle animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate bird
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
        self.image = pygame.image.load('img/pipe.png').convert_alpha()
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

# Button class
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
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

        return action

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/Coin.png').convert_alpha()
        self.rect = self.image.get_rect(center = [x, y])
    
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# Create bird instance
flappy = Bird(100, int(SCREEN_HEIGHT / 2))
bird_group.add(flappy)

# Create restart button instance
button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100, button_img)

run = True
while run:

    CLOCK.tick(FPS)

    # Draw background 
    SCREEN.blit(bg, (0, 0))

    # Draw groups
    bird_group.draw(SCREEN)
    bird_group.update()
    pipe_group.draw(SCREEN)
    coin_group.draw(SCREEN)

    # Draw ground
    SCREEN.blit(ground_img, (ground_scroll, 768))

    # Check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font1, white, int(SCREEN_WIDTH / 2) - 55, 20)
    draw_text(str(len(coin_score)), font1, white, 100, 20)

    if score >= 100:
        draw_text(str("You Win"), font2, white, int(SCREEN_WIDTH / 2) - 150, 275)
        if len(coin_score) == 1:
            draw_text(str(f"You got {len(coin_score)} coin"), font2, white, int(SCREEN_WIDTH / 2) - 300, 400)
        else:
            draw_text(str(f"You got {len(coin_score)} coins"), font2, white, int(SCREEN_WIDTH / 2) - 300, 400)
        game_over = True

    # Look for collision pipe
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    if pygame.sprite.groupcollide(bird_group, coin_group, False, True):
        i = 1
        coin_score.append(i)

    # Check if bird has hit ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if game_over == False and flying == True:

        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            coin = Coin((SCREEN_WIDTH + 200), int(SCREEN_HEIGHT / 2) + random.randint(-200, 200))
            coin_group.add(coin)
            last_pipe = time_now

        # Draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()
        coin_group.update()

    # Check for game over
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()
        if score < 100:
            draw_text(str("You Lose"), font2, white, int(SCREEN_WIDTH / 2) - 175, 275)
            if len(coin_score) == 1:
                draw_text(str(f"You got {len(coin_score)} coin"), font2, white, int(SCREEN_WIDTH / 2) - 300, 400)
            else:
                draw_text(str(f"You got {len(coin_score)} coins"), font2, white, int(SCREEN_WIDTH / 2) - 300, 400)

    # Stop / Start game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            if event.key == pygame.K_SPACE:
                flying = True

    pygame.display.flip()

pygame.quit()