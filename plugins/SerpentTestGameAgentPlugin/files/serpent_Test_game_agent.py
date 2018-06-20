#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import os
import pickle
import serpent.cv
import numpy as np
import collections
from datetime import datetime
from serpent.frame_transformer import FrameTransformer
from serpent.frame_grabber import FrameGrabber
from serpent.game_agent import GameAgent
from serpent.input_controller import KeyboardKey
from serpent.sprite import Sprite
from serpent.sprite_locator import SpriteLocator
from serpent.sprite_identifier import SpriteIdentifier
import skimage.io
from serpent.visual_debugger.visual_debugger import VisualDebugger

from .helpers.game_status import Game
from .helpers.terminal_printer import TerminalPrinter
from .helpers.ppo import SerpentPPO
from .helpers.dqn import KerasAgent

import random

class MyFrame:
    def __init__ (self, frame):
        self.frame = frame

class SerpentTestGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers['PLAY'] = self.handle_play

        self.frame_handler_setups['PLAY'] = self.setup_play

        self.value = None
        #print('Sprites')
        #print(type(self.game.sprites))
        #print('game')
        #print(self.game)
        #print('game type')
        #print(type(self.game))

        self.spriteGO = self.game.sprites.get('SPRITE_GAME_OVER')
        self.spriteWO = self.game.sprites.get('SPRITE_GAME_WON')
        self.spriteGirl = self.game.sprites.get('SPRITE_BETTY_0')

        self.printer = TerminalPrinter()
        self.visual_debugger = VisualDebugger()
        self.gamestate = Game()

    def setup_play(self):

        game_inputs = {
            "MoveUp": [KeyboardKey.KEY_UP],
            "MoveDown": [KeyboardKey.KEY_DOWN],
            "MoveLeft": [KeyboardKey.KEY_LEFT],
            "MoveRight": [KeyboardKey.KEY_RIGHT],
            "LeaveBomb": [KeyboardKey.KEY_SPACE],
            "None": [0]
        }
        self.game_inputs = game_inputs
        self.game_actions = [
            KeyboardKey.KEY_UP, 
            KeyboardKey.KEY_DOWN, 
            KeyboardKey.KEY_LEFT, 
            KeyboardKey.KEY_RIGHT,
            KeyboardKey.KEY_SPACE,
            None]

        ##120, 137
        self.dqn_agent = KerasAgent(shape=(104, 136, 1), action_size=len(self.game_actions))
        #load model
        #self.ppo_agent.restore_model()

        self.first_run = True
        
        ##states trainning
        self.epoch = 1
        self.total_reward = 0

        ##state & action
        self.prev_state = None
        self.prev_action = None
        self.prev_reward = 0


        print("Enter - Auto Save")
        self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
        self.gamestate.restartState()
        time.sleep(2)

    def extract_game_area(self, frame_buffer):
        game_area_buffer = []

        for game_frame in frame_buffer.frames:
            game_area = \
                serpent.cv.extract_region_from_image(game_frame.grayscale_frame,self.game.screen_regions['GAME_REGION'])

            frame = FrameTransformer.rescale(game_area, 0.25)
            game_area_buffer.append(frame)

        return np.array(game_area_buffer)

    def convert_to_rgba(self, matrix):
        #print(matrix)
        new_matrix = []
        for x in range(0,len(matrix)):
            line = []
            for y in range(0,len(matrix[x])):
                #pixel
                pixel = matrix[x][y]
                new_pixel = [pixel[0],pixel[1],pixel[2], 255]
                line.append(new_pixel)
            new_matrix.append(line)
        return np.array(new_matrix)


    def update_game_state(self, frame):
        game_area = \
                serpent.cv.extract_region_from_image(frame,self.game.screen_regions['GAME_REGION'])
        #game ...
        # 0,0
        # 32,32
        game_squares = [[None for j in range(0,11)] for i in range(0,15)]
        const_offset = 8
        const = 32
        #game variables
        self.gamestate.bombs = [] #{x, y}
        self.gamestate.enemies = [] #{x,y}
        #force girl to die if not found
        girl_found = False
        for i in range(0,15):
            for j in range(0, 11):
                izq = ((j+1)*const - const_offset, (i+1)*const - const_offset)
                der = ((j+2)*const + const_offset, (i+2)*const + const_offset)
                reg = (izq[0], izq[1], der[0], der[1])
                square =  serpent.cv.extract_region_from_image(game_area, reg)
                square = self.convert_to_rgba(square)
                sprite_to_locate = Sprite("QUERY", image_data=square[..., np.newaxis])
                sprite = self.sprite_identifier.identify(sprite_to_locate, mode="SIGNATURE_COLORS")
                game_squares[i][j] = sprite
                if("SPRITE_BETTY" in sprite):
                    self.girl = {"x": i, "y": j}
                    girl_found = True
                elif("SPRITE_GEORGE" in sprite):
                    self.gamestate.enemies.append({"x": i, "y": j})
                elif("SPRITE_BOMB" in sprite):
                    self.gamestate.bombs.append({"x": i, "y": j})
        self.gamestate.girl_alive = girl_found
        self.gamestate.done = not girl_found
        return game_squares

    def handle_play(self, game_frame):
        #self.printer.add("")
        #self.printer.add("BombermanAI")
        #self.printer.add("Reinforcement Learning: Training a PPO Agent")
        #self.printer.add("")
        #self.printer.add(f"Stage Started At: {self.started_at}")
        #self.printer.add(f"Current Run: #{self.current_attempts}")
        #self.printer.add("")

        self.check_game_state(game_frame)

        if(self.gamestate.done):
            if not self.epoch % 10:
                self.dqn_agent.save_model(f"bombergirl_epoch_{self.epoch}.model")
                self.printer.save_file()
            self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
            self.printer.add(f"{self.epoch},{self.gamestate.time},{self.total_reward}")
            self.total_reward = 0
            self.dqn_agent.replay()
            self.epoch += 1
            self.total_reward = 0
            self.gamestate.restartState()
            self.prev_state = None
            self.prev_action = None
        else:
            #update time
            self.gamestate.updateTime()
            #get buffer
            frame_buffer = FrameGrabber.get_frames([0, 1, 2, 3], frame_type="PIPELINE")
            game_frame_buffer = self.extract_game_area(frame_buffer)
            state = game_frame_buffer.reshape(4, 104, 136, 1)
            #print(np.stack(game_frame_buffer,axis=1).shape)
            #print(game_frame_buffer.shape)
            #print(state.shape)
            if(not (self.prev_state is None) and not (self.prev_action is None)):
                self.dqn_agent.remember(self.prev_state, self.prev_action, self.prev_reward, state, False)

            #do something
            action_index = self.dqn_agent.act(state)
            #get key
            action = self.game_actions[action_index]
            #get random frame from buffer
            game_frame_rand = random.choice(frame_buffer.frames).frame
            #update enviroment accorind to frame
            self.update_game_state(game_frame_rand)
            #get reward
            reward = self.gamestate.getReward(action_index)
            self.total_reward += reward
            self.prev_state = state
            self.prev_action = action_index
            self.prev_reward = reward

            if(action):
                self.input_controller.tap_key(action, 0.1 if action_index < 4 else 0.01)
            print(f"Action: {self.gamestate.game_inputs[action_index]}, reward: {reward}")
            #action, label, value = self.ppo_agent.generate_action(game_frame_buffer)
            #print(action, label, value)
            #key, value = random.choice(list(self.game_inputs.items()))
            #if(value[0]):
            #    self.input_controller.tap_key(value[0])
        #game_squares = self.extract_game_squares(game_frame.frame)
        


    def check_game_state(self, game_frame):
        #game over?
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
        sprite_locator = SpriteLocator()
        locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        #print(locationGO)
        #won game?
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteWO.image_data)
        sprite_locator = SpriteLocator()
        locationWO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        #print(locationWO)
        self.gamestate.girl_alive = locationGO== None and locationWO== None
        self.gamestate.done =  not self.gamestate.girl_alive
        self.gamestate.victory = locationGO== None and locationWO!= None

        #print(f"Is allive? {self.is_alive}")
        #print(f"Won? {self.victory}")