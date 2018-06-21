#from .memreader import MemoryReader
import time

class Game:
    enemies = [] #{x,y}
    bombs = [] #{x,y}
    bonus = []
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
    lose = False
    victory = False

    ##const
    TIME_NORM = 10
    MOVEMENT_RW = 5
    BONUS_RW = 10
    ALIVE_RW = 20
    ENEMIES_NORM = 5
    REWARD_BOMB = 25
    REWARD_VICTORY = 100
    REWARD_LOSE = 50

    MAX_DISTANCE = 8

    def restartState(self):
        self.girl_alive = True
        self.done = False
        self.lose = False
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
        # Para castigar por el numero de enemigos
        reward -= self.ENEMIES_NORM*len(self.enemies)
        # Para casticar con el paso del tiempo
        reward -= self.getCurrentTimeNormalized()

        # Para castigar/ premiar si la chica está cerca/lejos a una bomba
        for bomb in self.bombs:
            distance = self.getDistanceNormalized(bomb, self.girl)
            if distance < self.MAX_DISTANCE:
                reward -= distance
            else
                reward += distance

        if(action == 4):
            # Para premiar que esté colocando una bomba
            reward += self.REWARD_BOMB
            for enemy in self.enemies:
                # Para premiar que la bomba está más cerca a un enemigo
                distance = self.getDistanceNormalized(enemy, self.girl)
                if distance< self.MAX_DISTANCE:
                    reward += self.REWARD_BOMB/distance

        if(action < 4):
            # Para premiar que se mueve
            reward += self.MOVEMENT_RW
            # Para premiar que esté más cerca a un bonus
            for bonus in self.bonus:
                reward += self.BONUS_RW / self.getDistanceNormalized(bonus, self.girl)

        # Para premiar que está jugando
        if(self.girl_alive):
            reward += self.ALIVE_RW

        # Para castigar que ha perdido
        if self.lose:
            reward -= self.REWARD_LOSE

        # Para premiar que ha ganado
        if self.victory:
            reward += self.REWARD_VICTORY

        return reward
