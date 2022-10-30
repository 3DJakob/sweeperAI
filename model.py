import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



class Linear_QNet(nn.Module):
  def __init__(self, input_size, hidden_size, output_size):
    super().__init__()
    self.linear1 = nn.Linear(input_size, hidden_size).to(torch.device(device))
    self.linear2 = nn.Linear(hidden_size, output_size).to(torch.device(device))

  def forward(self, x):
    # tensor x is a batch of in
    x = F.relu(self.linear1(x))
    x = self.linear2(x)
    return x

  def save(self, file_name="model.pth"):
    model_folder_path = "./model"
    if not os.path.exists(model_folder_path):
      os.makedirs(model_folder_path)
    file_name = os.path.join(model_folder_path, file_name)
    torch.save(self.state_dict(), file_name)

class QTrainer:
  def __init__(self, model, lr, gamma):
    self.lr = lr
    self.gamma = gamma
    self.model = model
    self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
    self.criterion = nn.MSELoss()

  def train_step(self, stateIn, action, reward, next_stateIn, done):
    state = torch.tensor(stateIn, dtype=torch.float, device=device)
    next_state = torch.tensor(next_stateIn, dtype=torch.float, device=device)
    action = torch.tensor(action, dtype=torch.long, device=device)
    reward = torch.tensor(reward, dtype=torch.float, device=device)
    # done = torch.tensor(done, dtype=torch.float)

    if len(state.shape) == 1:
      # (1, x)
      state = torch.unsqueeze(state, 0)
      next_state = torch.unsqueeze(next_state, 0)
      reward = torch.unsqueeze(reward, 0)
      action = torch.unsqueeze(action, 0)
      done = (done, )
    # 1: get predicted Q values for current state using cuda
    pred = self.model(state)
    target = pred.clone()

    for idx in range(len(done)):
      Q_new = reward[idx]
      if not done[idx]:
        Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
      
      target = reward[idx]

    # 2: Q_new = r + y * max(next predicted Q values) - current predicted Q values

    self.optimizer.zero_grad()
    loss = self.criterion(target, pred)
    loss.backward()

    self.optimizer.step()
    