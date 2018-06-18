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

# from .helpers.game_status import Game
from .helpers.terminal_printer import TerminalPrinter
from .helpers.ppo import SerpentPPO

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
        print('Sprites')
        print(type(self.game.sprites))
        print('game')
        print(self.game)
        print('game type')
        print(type(self.game))

        self.spriteGO = self.game.sprites.get('SPRITE_GAME_OVER')
        self.spriteWO = self.game.sprites.get('SPRITE_GAME_WON')
        self.spriteGirl = self.game.sprites.get('SPRITE_BETTY_0')

        self.printer = TerminalPrinter()

    def setup_play(self):
        game_inputs = {
            "MoveUp": [KeyboardKey.KEY_UP],
            "MoveDown": [KeyboardKey.KEY_DOWN],
            "MoveLeft": [KeyboardKey.KEY_LEFT],
            "MoveRight": [KeyboardKey.KEY_RIGHT],
            "LeaveBomb": [KeyboardKey.KEY_SPACE],
            "None": None
        }
        self.game_inputs = game_inputs

        #self.ppo_agent = SerpentPPO(frame_shape=(120, 137, 4), game_inputs=game_inputs)
        ##load model
        #self.ppo_agent.restore_model()

        self.first_run = True
        self.game_over = False
        self.current_attempts = 0
        self.run_reward = 0
        self.started_at = datetime.utcnow().isoformat()
        self.paused_at = None

        print("Enter - Auto Save")
        self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
        time.sleep(2)

    def extract_game_area(self, frame_buffer):
        game_area_buffer = []

        for game_frame in frame_buffer.frames:
            game_area = \
                serpent.cv.extract_region_from_image(game_frame.grayscale_frame,self.game.screen_regions['GAME_REGION'])

            frame = FrameTransformer.rescale(game_area, 0.25)
            game_area_buffer.append(frame)

        return game_area_buffer

    def convert_to_rgba(self, matrix):
        #print(matrix)
        for x in range(0,len(matrix)):
            for y in range(0,len(matrix[x])):
                #pixel
                pixel = matrix[x][y]
                matrix[x][y] = [pixel[0],pixel[1],pixel[2], 255]


    def extract_game_squares(self, frame):
        game_area = \
                serpent.cv.extract_region_from_image(frame,self.game.screen_regions['GAME_REGION'])
        #game ...
        # 0,0
        # 32,32
        game_squares = [[None for j in range(0,11)] for i in range(0,15)]
        const = 32
        for i in range(0,15):
            for j in range(0, 11):
                izq = ((i+1)*const - 16, (j+2)*const - 16)
                der = ((i+2)*const + 16, (j+2)*const + 16)
                reg = (izq[0], izq[1], der[0], der[1])
                square =  serpent.cv.extract_region_from_image(game_area, reg)
                game_squares[i][j] = self.convert_to_rgba(square)
        return game_squares

    def handle_play(self, game_frame):
        if self.first_run:
            self.current_attempts += 1
            self.first_run = False
            return None

        self.printer.add("")
        self.printer.add("BombermanAI")
        self.printer.add("Reinforcement Learning: Training a PPO Agent")
        self.printer.add("")
        self.printer.add(f"Stage Started At: {self.started_at}")
        self.printer.add(f"Current Run: #{self.current_attempts}")
        self.printer.add("")

        self.check_game_state(game_frame)

        if(self.restart_game):
            #enter clic in both cases
            if not self.current_attempts % 10:
                self.ppo_agent.save_model()
            self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
        else:
            #game_frame_buffer = FrameGrabber.get_frames([0, 1], frame_type="PIPELINE")
            #game_frame_buffer = self.extract_game_area(game_frame_buffer)
            #action, label, value = self.ppo_agent.generate_action(game_frame_buffer)
            #print(action, label, value)
            key, value = random.choice(list(self.game_inputs.items()))
            if(value):
                self.input_controller.tap_key(value[0])
        game_squares = self.extract_game_squares(game_frame.frame)
        girl_square = game_squares[0][0]
        sprite_to_locate = Sprite("QUERY", image_data=girl_square)
        #sprite_locator = SpriteLocator()
        locationGirl = self.sprite_identifier.identify(sprite_to_locate, mode="SIGNATURE_COLORS")
        #locationGirl = sprite_locator.locate(sprite=sprite_to_locate, game_frame=MyFrame(girl_square))
        print("girl location")
        print(locationGirl)


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
        self.is_alive = locationGO== None and locationWO== None
        self.restart_game =  not self.is_alive
        self.victory = locationGO== None and locationWO!= None

        print(f"Is allive? {self.is_alive}")
        print(f"Won? {self.victory}")

    def reward_girl (self, frame, action):
        reward = 0

        enemies = self.gamestate,getEnemies(frame)
        reward -= 5*enemies.length

        time = self.gamestate.getCurrentTimeNormalized()
        reward -= time

        bombs = self.gamestate.getBombs()
