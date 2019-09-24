#python

import keras
from keras import backend as K
import numpy as np
import random
from time import time, sleep
from collections import deque
from colorama import Fore, Style, init

init()

'''
model = keras.models.Sequential([
    keras.layers.Flatten(input_shape=(6,5)),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(number_of_steps*8 + xwidth + yheight)
])'''



class DungeonSimulator:
    def __init__(self, width=6, height=5, loc=np.array([2, 2]), orb_count=6):
        self.width = width
        self.height = height
        self.orb_count = orb_count  # how many different types of orbs there are
        self.loc = loc  # location of the starting orb that is picked up
        self.dirarray4 = np.array([[0,1],[1,0],[0,-1],[-1,0]])
        self.action_index = 0
        self.action_array = [0]*100
        self.reset() #generates a random board to start

    def gen_board(self):
        b = np.random.randint(0, self.orb_count, (self.height, self.width))
        #print(b)
        return b

    def ret_state(self):
        return self.state

    def take_action(self, action):
        dirarray8 = np.array([[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]])
        oldloc = self.state[0]
        board = self.state[1]
        oldval = board[oldloc[0],oldloc[1]]
        newloc = oldloc + dirarray8[action]
        match_count_0 = self.reward_state()
        if newloc[0] >= self.height or newloc[1] >= self.width or newloc[0] < 0 or newloc[1] < 0:
            return self.state, -0.1
        board[oldloc[0], oldloc[1]] = board[newloc[0], newloc[1]]
        board[newloc[0], newloc[1]] = oldval
        self.state = np.array([newloc,board])
        match_count_1 = self.reward_state()
        if match_count_1 > match_count_0:
            return self.state, self.reward_state()**2
        if match_count_1 == match_count_0:
            return self.state, 0
        else:
            return self.state, -1
        #print('.',end='')

    def exists(self, p): # makes sure that the location is within orb bounds
        if (p[0] < self.height and p[1] < self.width and p[1] >= 0 and p[0] >= 0):
            return True
        return False
    def returnPointsOfPiece(self, y, x, di, length):
        point_list = []
        for i in range(length):
            point_list.append([y+di[0]*i,x+di[1]*i])
        return point_list
    def fill(self, b, y, x, num):
        b[y,x] = num
        pos = np.array([y,x])
        for di in self.dirarray4:
            if self.exists(pos+di) and b[y+di[0],x+di[1]] == 1:
                self.fill(b,y+di[0],x+di[1],num)

    def reward_state(self):
        b = self.state[1].copy()
        colorMatches = np.zeros((self.orb_count, self.height, self.width))
        for y in range(self.height-2):
            for x in range(self.width):
                a = self.returnPointsOfPiece(y,x,[1,0],3)
                color = b[a[0][0],a[0][1]]
                if b[a[1][0],a[1][1]] == color and b[a[2][0],a[2][1]] == color:
                    for loc in a:
                        colorMatches[color,loc[0],loc[1]] = 1
        for y in range(self.height):
            for x in range(self.width-2):
                a = self.returnPointsOfPiece(y,x,[0,1],3)
                color = b[a[0][0],a[0][1]]
                if b[a[1][0],a[1][1]] == color and b[a[2][0],a[2][1]] == color:
                    for loc in a:
                        colorMatches[color,loc[0],loc[1]] = 1
        num = 2
        totalMatches = 0
        for b in colorMatches:
            for y in range(self.height):
                for x in range(self.width):
                    if b[y,x] == 1:
                        self.fill(b,y,x,num)
                        num += 1
            totalMatches += num - 2
            num = 2
        return totalMatches

    def format_state(self, s, reward, tot_reward):
        pos = s[0]
        board = s[1]
        print("\n")
        for y in range(self.height):
            for x in range(self.width):
                if y == pos[0] and x == pos[1]:
                    print(Fore.GREEN + str(board[y,x]) + Style.RESET_ALL, end="  ")
                else:
                    print(str(board[y,x]), end="  ")
            print("")
        print('reward:{:^3} tot_reward:{:>4}'.format(reward, tot_reward))
        sleep(0.3)

    #def get_extra_info(self):
    #    stored_state = self.state.copy()

    def get_valid_actions(self, old_action):
        valid_actions = np.array([1]*8)
        pos = self.state[0]
        if pos[0] == 0:
            valid_actions[5:8] = 0
        if pos[0] == self.height-1:
            valid_actions[1:4] = 0
        if pos[1] == 0:
            valid_actions[3:6] = 0
        if pos[1] == self.width-1:
            valid_actions[0:2] = 0
            valid_actions[7] = 0
        if old_action >= 0:
            valid_actions[old_action] = 0
        return valid_actions
            
    def reset(self):
        # Reset state to zero, the beginning of the dungeon
        self.state = np.array([[2, 2], self.gen_board()])
        while self.reward_state() > 0:
            self.state = np.array([[2, 2], self.gen_board()])

#----------------------------------------------------------------------------------------------------------------

class PadAgent:
    def __init__(self, action_size, orb_count, height, width, model=None):
        self.action_size = action_size
        self.orb_count = orb_count
        self.model_layer_count = self.orb_count + 1
        self.height = height
        self.width = width
        self.gamma = 0.95    # discount rate
        self.epsilon = 1  # exploration rate
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.999995
        self.learning_rate = 0.005
        self.memory = deque(maxlen = 3000)
        if model == None:
            print("No model provided, building...")
            sleep(1)
            self.model = self._build_model()
        else:
            print("Model provided")
            sleep(1)
            self.model = model
            model.compile(loss='mse',
                      optimizer=keras.optimizers.Adam(lr=self.learning_rate))
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = keras.models.Sequential()
        model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu', input_shape=(self.height, self.width, self.model_layer_count)))
        model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
        model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu'))
        model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
        model.add(keras.layers.Conv2D(128, kernel_size=3, activation='relu'))
        model.add(keras.layers.MaxPooling2D(pool_size=(2, 2)))
        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=keras.optimizers.Adam(lr=self.learning_rate))
        return model

    def act(self, state, valid_actions):
        state = self.decode_state(state)
        act_values = self.model.predict(state)
        if np.random.rand() <= self.epsilon:
            np.random.shuffle(act_values[0])
        for i in range(self.action_size):
            act_values[0][i] *= valid_actions[i]
        #print(act_values)
        return np.argmax(act_values[0])  # returns action
    def decode_state(self, state):
        pos = state[0]
        board = state[1]
        ret_arr = np.zeros((len(state[1]), len(state[1][0]), self.model_layer_count))
        ret_arr[pos[0], pos[1], 0] = 1
        for y, row in enumerate(board):
            for x, color in enumerate(row):
                ret_arr[y, x, color+1] = 1
        #ret_arr.reshape((self.model_layer_count, len(state[1]), len(state[1][0]), 1))
        ret_arr = np.expand_dims(ret_arr, 0)
        return ret_arr
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            state = self.decode_state(state)
            target = reward
            if not done:
                next_state = self.decode_state(next_state)
                target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            #print(target_f)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        self.memory = deque(maxlen=3000)

#----------------------------------------------------------------------------------------------------------------

def run_sim():
    env = DungeonSimulator()
    
    with open('PAD_architecture.json', 'r') as f:
        model = keras.models.model_from_json(f.read())
    model.load_weights('PAD_weights.h5')
    agent = PadAgent(8, env.orb_count, env.height, env.width, model)
    agent.epsilon = 0

    state = env.ret_state()
    state_list = [state]
    tot_reward = 0
    old_action = -1
    for time_t in range(100):
        action = agent.act(state, env.get_valid_actions(old_action))
        old_action = action
        state, reward = env.take_action(action)
        tot_reward += reward
        env.format_state(state, reward, tot_reward)
        print(agent.model.predict(agent.decode_state(state)))
    #print("score:", tot_reward)

#----------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # initialize gym environment and the agent
    try:
        env = DungeonSimulator()
        #with open('PAD_architecture.json', 'r') as f:
        #    model = keras.models.model_from_json(f.read())
        #model.load_weights('PAD_weights.h5')
        agent = PadAgent(8, env.orb_count, env.height, env.width)
        state = env.ret_state()
        episodes = 1000000
        # Iterate the game
        for e in range(1,episodes):
            # reset state in the beginning of each game
            tot_reward = 0
            old_action = -1
            env.reset()
            if e%10000 == 0:
                agent.model.save_weights('PAD_weights.h5')
                with open('PAD_architecture.json', 'w') as f:
                    f.write(agent.model.to_json())
            for time_t in range(100):
                action = agent.act(state, env.get_valid_actions(old_action))
                old_action = action
                # Advance the game to the next frame based on the action.
                next_state, reward = env.take_action(action)
                tot_reward += reward
                #print(reward, end='')
                done = time_t == 99
                agent.remember(state, action, reward, next_state, done)
                # make next_state the new current state for the next frame.
                state = next_state
            print("episode: {}/{}, score: {:>4}, epsilon: {:>.4f}".format(e, episodes, tot_reward, agent.epsilon))
            agent.replay(16)
    except KeyboardInterrupt:
        pass

    agent.model.save_weights('PAD_weights.h5')
    with open('PAD_architecture.json', 'w') as f:
        f.write(agent.model.to_json())

    run_sim()