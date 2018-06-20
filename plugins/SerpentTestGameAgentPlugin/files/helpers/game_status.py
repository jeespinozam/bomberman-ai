from .memreader import MemoryReader
import time

class Game:
    enemies = [] #{x,y}
    bombs = [] #{x,y}
    girl = {"x": 0, "y": 0}
    start_time = 0
    time = 0
    game_inputs = {
        0: "MoveUp",
        1: "MoveDown",
        2: "MoveLeft",
        3: "MoveRight",
        4: "LeaveBomb",
        5: "None"
    }
    girl_alive = True
    done = False
    victory = False

    ##const
    TIME_NORM = 1000
    ENEMIES_NORM = 5
    REWARD_BOMB = 50
    REWARD_VICTORY = 1000


    def restartState(self):
        self.girl_alive = True
        self.done = False
        self.victory = False
        self.time = 0
        self.start_time = time.time()

    def getCurrentTimeNormalized(self):
        return self.time / self.TIME_NORM

    def getDistanceNormalized(self, elem1, elem2):
        return abs(elem1['x'] - elem2['x']) + abs(elem1['y'] - elem2['y'])

    def updateTime(self):
        self.time = time.time() - self.start_time

    def getReward(self, action):
        reward = 0
        #enemies 
        reward -= self.ENEMIES_NORM*len(self.enemies)
        #time
        reward -= self.getCurrentTimeNormalized()

        for bomb in self.bombs:
            reward -= self.getDistanceNormalized(bomb, self.girl)

        if(self.game_inputs[action] == "LeaveBomb"):
            reward += self.REWARD_BOMB
            for enemy in self.enemies:
                reward += self.REWARD_BOMB / self.getDistanceNormalized(enemy, self.girl)

        if self.victory:
            reward += self.REWARD_VICTORY

        if not self.girl_alive:
            reward -= self.REWARD_VICTORY

        return reward
