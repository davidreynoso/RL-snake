import torch
import numpy as np
import random
from snakeGameLearn import RLearnSnakeGame, Point, Direction
import snakeGameLearn
from collections import deque
from model import DQN, QTrain
import matplotlib.pyplot as plt
from IPython import display

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Snake Time')
    plt.xlabel('# of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)

BATCH = 1000
class Bot:
    
    def __init__(self):
        self.game_num = 0
        self.randchance = 0
        self.gamma = 0.9
        self.storage = deque(maxlen=100000)
        self.model = DQN(11,256,3)
        self.train = QTrain(self.model, lr=0.001, gamma=self.gamma)


    def game_state(self, snakeGame):
        head = snakeGame.snake[0]

        pleft = Point(head.x - snakeGameLearn.BLOCK, head.y)
        pright = Point(head.x + snakeGameLearn.BLOCK, head.y)
        pup = Point(head.x, head.y - snakeGameLearn.BLOCK)
        pdown = Point(head.x, head.y + snakeGameLearn.BLOCK)

        dleft = snakeGame.direction == Direction.LEFT
        dright = snakeGame.direction == Direction.RIGHT
        dup = snakeGame.direction == Direction.UP
        ddown = snakeGame.direction == Direction.DOWN

        state = [
            # Danger straight
            (dright and snakeGame.collided(pright)) or 
            (dleft and snakeGame.collided(pleft)) or 
            (dup and snakeGame.collided(pup)) or 
            (ddown and snakeGame.collided(pdown)),

            # Danger right
            (dup and snakeGame.collided(pright)) or 
            (ddown and snakeGame.collided(pleft)) or 
            (dleft and snakeGame.collided(pup)) or 
            (dright and snakeGame.collided(pdown)),

            # Danger left
            (ddown and snakeGame.collided(pright)) or 
            (dup and snakeGame.collided(pleft)) or 
            (dright and snakeGame.collided(pup)) or 
            (dleft and snakeGame.collided(pdown)),
            
            dleft,dright,dup,ddown,

            snakeGame.food.x < snakeGame.head.x,
            snakeGame.food.x > snakeGame.head.x,
            snakeGame.food.y < snakeGame.head.y,
            snakeGame.food.y > snakeGame.head.y
        ]
        return np.array(state, dtype= int)
    
    def store(self, state1, decision, happiness, state2, game_over):
        self.storage.append((state1, decision, happiness, state2, game_over))

    def train_longTerm(self):
        if len(self.storage) > BATCH:
            sample = random.sample(self.storage, BATCH)
        else:
            sample = self.storage
        state1s, decisions, emotions, state2s, game_overs = zip(*sample)
        self.train.step(state1s, decisions, emotions, state2s, game_overs)

    def train_shortTerm(self, state1, decision, happiness, state2, game_over):
        self.train.step(state1, decision, happiness, state2, game_over)

    def decide(self, state):
        self.randchance = 100 - self.game_num
        new_move = [0,0,0]
        if random.randint(100,250) < self.randchance:  #to load
        #if random.randint(0,250) < self.randchance:    #to train
            move = random.randint(0,2)
            new_move[move] = 1
        else:
            mod_state = torch.tensor(state, dtype=torch.float)
            prediction = self.model(mod_state)
            new_move[torch.argmax(prediction).item()] = 1
        return new_move


def train():
    all_scores = []
    avg_scores = []
    total_score = 0
    high_score = 0
    bot = Bot()
    bot.model.load()
    game = RLearnSnakeGame()
    while True:
        initial_state = bot.game_state(game)

        new_move = bot.decide(initial_state)

        happiness, game_over, score = game.play_step(new_move)
        new_state = bot.game_state(game)

        bot.train_shortTerm(initial_state, new_move, happiness, new_state, game_over)
        bot.store(initial_state, new_move, happiness, new_state, game_over)

        if game_over:
            game.reset()
            bot.game_num += 1
            bot.train_longTerm()
            if score > high_score:
                high_score = score
                bot.model.save()

            print("Game", bot.game_num, "Score", score, "High Score", high_score)

            #plot
            all_scores.append(score)
            total_score += score
            avg_score = total_score / bot.game_num
            avg_scores.append(avg_score)
            plot(all_scores, avg_scores)


if __name__ == '__main__':
    train()