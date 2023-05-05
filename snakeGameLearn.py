import pygame
import numpy as np
import random
from enum import Enum
from collections import namedtuple

pygame.mixer.pre_init(44100, -16,2,512)
pygame.init()
font = pygame.font.SysFont("comicsans", 22)

Point = namedtuple("Point", "x y")

Direction = Enum("Direction", ["RIGHT", "LEFT", "UP", "DOWN"])

# make sure a divisor of both the width and height for full screen usage
BLOCK = 50
SPEED = 40
BOARD = (173, 220, 75)
class RLearnSnakeGame:
    def __init__(self, w = 900, h = 900):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.reset()
        #extras
        self.apple = pygame.transform.scale(pygame.image.load('Graphics/apple.png').convert_alpha(), (BLOCK,BLOCK))
        self.head_right = pygame.transform.scale(pygame.image.load("Graphics/head_right.png").convert_alpha(), (BLOCK, BLOCK))
        self.head_left = pygame.transform.scale(pygame.image.load("Graphics/head_left.png").convert_alpha(), (BLOCK, BLOCK))
        self.head_up = pygame.transform.scale(pygame.image.load("Graphics/head_up.png").convert_alpha(), (BLOCK, BLOCK))
        self.head_down = pygame.transform.scale(pygame.image.load("Graphics/head_down.png").convert_alpha(), (BLOCK, BLOCK))
        self.yum_sound = pygame.mixer.Sound("Sounds/Yum.mp3")
        self.crunchy_sound = pygame.mixer.Sound("Sounds/crunchy.mp3")
        pygame.mixer.music.load("Sounds/pokeman.mp3")
        pygame.mixer.music.play(-1,0.0)
        pygame.mixer.music.set_volume(0.1)


    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(((self.w/2)//BLOCK)*BLOCK, ((self.h/2)//BLOCK)*BLOCK)
        self.snake = [self.head, Point(self.head.x-BLOCK, self.head.y), Point(self.head.x-(2*BLOCK), self.head.y)]
        self.score = 0
        self.food = None
        self.frame_iter = 0
        self.place_food()

    def place_food(self):
        x = random.randint(0, (self.w//BLOCK)-1)*BLOCK
        y = random.randint(0, (self.h//BLOCK)-1)*BLOCK
        self.food = Point(x,y)
        if self.food in self.snake:
            self.place_food()
        


    def play_step(self, decision):
        self.frame_iter += 1
        for input in pygame.event.get():
            if input.type == pygame.QUIT:
                pygame.quit()
                quit()
        self.move(decision)
        
        self.snake.insert(0, self.head)

        happiness = 0
        game_over = False
        if self.collided() or self.frame_iter > 100*len(self.snake):
            game_over = True
            happiness = -10
            return happiness, game_over, self.score

        if self.head == self.food:
            self.score += 1
            happiness = 10
            if self.score % 10 == 0:
                self.yum_sound.play()
            else:
                self.crunchy_sound.play()
            self.place_food()
        else:
            self.snake.pop()

        self.update_visuals()
        self.clock.tick(SPEED)

        return happiness, game_over, self.score
    
    def collided(self, point = None):
        if point == None:
            point = self.head
        if (point.x > (self.w - BLOCK)) or (point.y > (self.h - BLOCK)) or point.x < 0 or point.y < 0:
            return True
        if point in self.snake[1:]:
            return True
        return False

    def move(self, decision):
        x = self.head.x
        y = self.head.y
        DirectionOrder = [Direction.RIGHT,Direction.DOWN,Direction.LEFT,Direction.UP]
        index = DirectionOrder.index(self.direction)
        if np.array_equal(decision, [1,0,0]):
            self.direction = DirectionOrder[index]
        elif np.array_equal(decision, [0,1,0]):
            new_index = (index +1) % 4
            self.direction = DirectionOrder[new_index]
        elif np.array_equal(decision, [0,0,1]):
            new_index = (index -1) % 4
            self.direction = DirectionOrder[new_index]
        if self.direction == Direction.RIGHT:
            x += BLOCK 
        elif self.direction == Direction.LEFT:
            x -= BLOCK
        elif self.direction == Direction.DOWN:
            y += BLOCK 
        elif self.direction == Direction.UP:
            y -= BLOCK 
        self.head = Point(x,y)

    def head_dir(self):
        diffx = self.snake[1].x - self.snake[0].x
        diffy = self.snake[1].y - self.snake[0].y
        if diffx == BLOCK: #left
            return self.head_left
        elif diffx == -BLOCK: #right
            return self.head_right
        elif diffy == BLOCK: #up
            return self.head_up
        elif diffy == -BLOCK: #down
            return self.head_down


    def update_visuals(self):
        self.display.fill(BOARD)
        for row in range(self.h//BLOCK):
            for col in range(self.w//BLOCK):
                if col % 2 == 0 and row % 2 == 0:
                    grass_chunk = pygame.Rect(col*BLOCK, row*BLOCK, BLOCK, BLOCK)
                    pygame.draw.rect(self.display, (170, 205, 57), grass_chunk)
                elif col % 2 == 1 and row % 2 == 1: 
                    grass_chunk = pygame.Rect(col*BLOCK, row*BLOCK, BLOCK, BLOCK)
                    pygame.draw.rect(self.display, (170, 205, 57), grass_chunk)
        for snakemeat in self.snake:
            meatblock = pygame.Rect(snakemeat.x,snakemeat.y,BLOCK, BLOCK)
            if self.snake.index(snakemeat) == 0:
                self.display.blit(self.head_dir(), meatblock)
            else:
                pygame.draw.rect(self.display, (100, 100, 200), meatblock)
        Yummerz = pygame.Rect(self.food.x, self.food.y, BLOCK, BLOCK)
        #pygame.draw.rect(self.display, (200, 50, 50), Yummerz)
        self.display.blit(self.apple, Yummerz)
        text_score = font.render("Score: " + str(self.score), True, (0,0,0))
        self.display.blit(text_score, [self.w//2 - text_score.get_width()//2, 0])
        pygame.display.flip()
