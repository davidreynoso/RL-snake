import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)
        
    def load(self, file_name='model.pth'):
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)

        if os.path.isfile(file_name):
            self.load_state_dict(torch.load(file_name))
            self.eval()
            print ('Loading existing state dict.')
            return True
        
        print ('No existing state dict found. Starting from scratch.')
        return False
        
class QTrain:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)
        self.loss = nn.MSELoss()

    def step(self, initial_state, new_move, happiness, new_state, game_over):
        initial_state = torch.tensor(initial_state, dtype=torch.float)
        new_state = torch.tensor(new_state, dtype=torch.float)
        new_move = torch.tensor(new_move, dtype=torch.long)
        happiness = torch.tensor(happiness, dtype=torch.float)

        if len(initial_state.shape) == 1:
            initial_state = torch.unsqueeze(initial_state, 0)
            new_state = torch.unsqueeze(new_state, 0)
            new_move = torch.unsqueeze(new_move, 0)
            happiness = torch.unsqueeze(happiness, 0)
            game_over = (game_over, )

        prediction = self.model(initial_state)
        target = prediction.clone()

        for i in range(len(game_over)):
            new_Q = happiness[i]
            if not game_over[i]:
                new_Q = happiness[i] + self.gamma * torch.max(self.model(new_state[i]))

            target[i][torch.argmax(new_move[i]).item()] = new_Q

        self.optimizer.zero_grad()
        loss = self.loss(target,prediction)
        loss.backward()
        self.optimizer.step()


