import torch
import random
import numpy as np
from collections import deque
from sweeper import SweeperGame, GRIDX, GRIDY
from model import Linear_QNet, QTrainer
from helper import plot
cuda = torch.device('cuda')     # Default CUDA device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

USING5X5MODEL = True

class Agent:

  def __init__(self):
    self.n_games = 0
    self.epsilon = 0  # randomness
    self.gamma = 0.9  # discount rate
    self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
    self.model = Linear_QNet(5*5, 256, 1)
    self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

  def userMapToState(self, game):
    state2D = np.array(game.userMap)
    state3D = np.zeros((GRIDX, GRIDY, 12))
    for x in range(GRIDX):
      for y in range(GRIDY):
        # layer 12 is if explored
        if (state2D[y][x] != 10):
          state3D[x][y][11] = 1

        if state2D[y][x] == 0:
          state3D[y][x][0] = 1
        elif state2D[y][x] == 1:
          state3D[y][x][1] = 1
        elif state2D[y][x] == 2:
          state3D[y][x][2] = 1
        elif state2D[y][x] == 3:
          state3D[y][x][3] = 1
        elif state2D[y][x] == 4:
          state3D[y][x][4] = 1
        elif state2D[y][x] == 5:
          state3D[y][x][5] = 1
        elif state2D[y][x] == 6:
          state3D[y][x][6] = 1
        elif state2D[y][x] == 7:
          state3D[y][x][7] = 1
        elif state2D[y][x] == 8:
          state3D[y][x][8] = 1
        elif state2D[y][x] == 9:
          state3D[y][x][9] = 1
        elif state2D[y][x] == 10:
          state3D[y][x][10] = 1
    return state3D.flatten().flatten()

  def userMapTo5x5State(self, game, x, y):
    state = np.zeros((5,5))
    for i in range(5):
      for j in range(5):
        if (x-2+i < 0 or y-2+j < 0 or x-2+i >= GRIDX or y-2+j >= GRIDY):
          state[i][j] = 10 # simple solution for out of bounds set unexplored
        else:
          state[i][j] = game.userMap[y-2+j][x-2+i]
 
    return state.flatten()



  def get_state(self, game, x, y):
    # state = np.array(game.userMap).flatten()
    # return np.array(state, dtype=int)
    return self.userMapToState(game)

  def train_short_memory(self, state, action, reward, next_state, game_over):
    self.trainer.train_step(state, action, reward, next_state, game_over)

  # returns how much it wants to click the tile
  def get_action5x5(self, game, x, y):
    # random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.n_games
    final_move = 0
    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, GRIDX*GRIDY-1)
      return move
    else:
      state = self.userMapTo5x5State(game, x, y)
      state0 = torch.tensor(state, dtype=torch.float, device=device)
      final_move = self.model(state0).item()
    return final_move

  def get_action(self, state, game):
    # random moves: tradeoff exploration / exploitation
    self.epsilon = 80 - self.n_games
    final_move = [0] * GRIDX*GRIDY
    if random.randint(0, 200) < self.epsilon:
      move = random.randint(0, GRIDX*GRIDY-1)
      final_move[move] = 1
    else:
      state0 = torch.tensor(state, dtype=torch.float, device=device)
      prediciton = self.model(state0)
      #predictionArray = prediciton.detach().numpy()
      #moveIndex = np.argmax(predictionArray)
      moveIndex = torch.argmax(prediciton).item()
      final_move[moveIndex] = 1
    return final_move

def train():
  plot_scores = []
  plot_mean_scores = []
  plot_already_clicked = []
  total_score = 0
  record = 0
  agent = Agent()
  game = SweeperGame()

  currentAlreadyClicked = 0
  # game.run()
  while True:
    # Get old state
    state_old = False

    # Get move
    final_move = [0] * GRIDX*GRIDY
    coordinates = (0,0)
    if USING5X5MODEL:
      theMaxValue = -1000

      # Find the best move
      for x in range(GRIDX):
        for y in range(GRIDY):
          if (game.userMap[y][x] != 10):
            continue
          # Get old state
          # get the state for the 5x5
          moveWeight = agent.get_action5x5(game, x, y)
          if moveWeight > theMaxValue:
            theMaxValue = moveWeight
            coordinates = (x,y)
      
      final_move[coordinates[0] + coordinates[1] * GRIDX] = 1
      state_old = agent.userMapTo5x5State(game, coordinates[0], coordinates[1])
    else:
      state_old = agent.get_state(game)
      final_move = agent.get_action(state_old, game)

    # Perform move and get new state
    x = final_move.index(1) % GRIDX
    y = final_move.index(1) // GRIDY

    reward, game_over, game_won, score = game.userMove(x, y)

    # If clicked on an already clicked cell, give a negative reward
    if reward == 0:
      currentAlreadyClicked += 1
      reward = -100

    game.draw()
    state_new = False
    if USING5X5MODEL:
      state_new = agent.userMapTo5x5State(game, coordinates[0], coordinates[1])
    else:
      state_new = agent.get_state(game)

    # Train short memory
    agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

    if game_over or game_won:
      # Reset, plot result
      game.reset(5)
      agent.n_games += 1

      if score > record:
        record = score
        agent.model.save()
      
      # print('Game', agent.n_games, 'Score', score, 'Record:', record)

      plot_scores.append(score)
      total_score += score
      mean_score = total_score / agent.n_games
      plot_mean_scores.append(mean_score)
      plot_already_clicked.append(currentAlreadyClicked * 100) # times 100 to make it more visible
      plot(plot_scores, plot_mean_scores, plot_already_clicked)

      currentAlreadyClicked = 0


      

if __name__ == '__main__':
  train()