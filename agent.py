import torch
import random
import numpy as np
from collections import deque
from sweeper import SweeperGame, GRIDX, GRIDY
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

  def __init__(self):
    self.n_games = 0
    self.epsilon = 0  # randomness
    self.gamma = 0.9  # discount rate
    self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
    self.model = Linear_QNet(GRIDX*GRIDY, 256, GRIDX*GRIDY)
    self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

  def get_state(self, game):
    state = np.array(game.userMap).flatten()
    return np.array(state, dtype=int)

  def remember(self, state, action, reward, next_state, game_over):
    tupleData = (state, action, reward, next_state, game_over)
    self.memory.append(tupleData)

  def train_long_memory(self):
    if len(self.memory) > BATCH_SIZE:
      mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
    else:
      mini_sample = self.memory
    
    states, actions, rewards, next_states, game_overs = zip(*mini_sample)
    self.trainer.train_step(states, actions, rewards, next_states, game_overs)

  def train_short_memory(self, state, action, reward, next_state, game_over):
    self.trainer.train_step(state, action, reward, next_state, game_over)

  def get_action(self, state, game):
    # random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.n_games
    final_move = [0] * GRIDX*GRIDY
    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, GRIDX*GRIDY-1)
      final_move[move] = 1
    else:
      state0 = torch.tensor(state, dtype=torch.float)
      prediciton = self.model(state0)
      predictionArray = prediciton.detach().numpy()
      moveIndex = np.argmax(predictionArray)
      
      # check if valid move
      userMap = np.array(game.userMap).flatten()
      while userMap[moveIndex] != 10:
        # take next best move
        predictionArray[moveIndex] = -100
        moveIndex = np.argmax(predictionArray)
      final_move[moveIndex] = 1
    return final_move

def train():
  plot_scores = []
  plot_mean_scores = []
  total_score = 0
  record = 0
  agent = Agent()
  game = SweeperGame()
  # game.run()
  while True:
    # Get old state
    state_old = agent.get_state(game)

    # Get move
    final_move = agent.get_action(state_old, game)

    # Perform move and get new state
    x = final_move.index(1) // GRIDX
    y = final_move.index(1) % GRIDY
    reward, game_over, score = game.userMove(x, y)
    game.draw()
    state_new = agent.get_state(game)

    # Train short memory
    agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

    # Remember
    agent.remember(state_old, final_move, reward, state_new, game_over)

    if game_over:
      # Train long memory, plot result
      game.reset()
      agent.n_games += 1
      agent.train_long_memory()

      if score > record:
        record = score
        agent.model.save()
      
      print('Game', agent.n_games, 'Score', score, 'Record:', record)

      plot_scores.append(score)
      total_score += score
      mean_score = total_score / agent.n_games
      plot_mean_scores.append(mean_score)
      plot(plot_scores, plot_mean_scores)


      

if __name__ == '__main__':
  train()