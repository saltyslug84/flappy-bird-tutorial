import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 50

screen_width = 864
screen_height = 736

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# define color
white = ((255, 255, 255))

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500    # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency    # how long has passed since last pipe
score = 0
pass_pipe = False    # trigger for score increase

# load images
bg = pygame.image.load('bg.png')
ground = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# reseting all variables when reset button is clicked
def reset_game():
    pipe_group.empty()    # reset pipe group
    # set bird back to intitial position
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0    # reset score to 0
    return score

# creating the bird
class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []    # empty list of images
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)    # append images
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0

    def update(self):

        if flying == True:
            # apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 588:
                self.rect.y += int(self.vel)
        
        if game_over == False:
            # jumping
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:    # if left mouse bar clicked
                self.clicked = True
                self.vel = -8
            if pygame.mouse.get_pressed()[0] == 0:    # if left mouse bar not clicked
                self.clicked = False

            # handle the animation
            self.counter += 1    # increment counter by 1
            flap_cooldown = 5

            # if counter becomes greater than the cooldown, reset counter
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                # if index reaches the number of images in list, reset index
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate bird (counterclockwise by default)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1)
        else:
            # point dead bird at ground :(
            self.image = pygame.transform.rotate(self.images[self.index], -90)
      
class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        
        # position 1 is from top, -1 is from bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)    # flip y axis, not x axis
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed    # move pipes left
        if self.rect.right < 0:
            self.kill()    # destroy pipe once it goes off screen

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False    # mouse clicked trigger

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:    # if left mouse button is clicked
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# with sprit eclasses comes groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
# set initial position of bird
flappy = Bird(100, int(screen_height / 2))

# appending the group
bird_group.add(flappy)

# create restart button instance
button = Button(screen_width / 2 - 50, screen_height / 2 - 100, button_img)

# game loop
run = True
while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, -150))

    # draw the bird
    bird_group.draw(screen)
    bird_group.update()

    # draw the pipe
    pipe_group.draw(screen)

    # draw the ground
    screen.blit(ground, (ground_scroll, 588))

    # check the score
    if len(pipe_group) > 0:    # check if any pipes on the screen yet
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True    # trigger goes off
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1    # increase score
                pass_pipe = False    # set trigger back to False

    draw_text(str(score), font, white, int(screen_width/ 2), 20)

    # check for bird collision with pipe
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:    # the boolean values at False keep the groups visible (if true, collision would delete the group like in a shooter game)
        game_over = True

    # check for bird collision with the ground
    if flappy.rect.bottom >= 588:
        game_over = True
        flying = False

    # while game is running, scroll ground
    if game_over == False:
        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency and flying == True:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # scroll game
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    if game_over == True:
        if button.draw():    # check if button has been clicked
            game_over = False
            score =  reset_game()    # call the reset function


    # if user clicks exit window, game quits
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    

    pygame.display.update()

pygame.quit()