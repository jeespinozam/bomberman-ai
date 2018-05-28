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

        self.printer = TerminalPrinter()

    def setup_play(self):
        game_inputs = {
            "MoveUp": [KeyboardKey.KEY_UP],
            "MoveDown": [KeyboardKey.KEY_DOWN],
            "MoveLeft": [KeyboardKey.KEY_LEFT],
            "MoveRight": [KeyboardKey.KEY_RIGHT],
            "LeaveBomb": [KeyboardKey.KEY_SPACE]
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
            os.exit()
        else:
            #game_frame_buffer = FrameGrabber.get_frames([0, 1, 2,4], frame_type="PIPELINE")
            #game_frame_buffer = self.extract_game_area(game_frame_buffer)
            #action, label, value = self.ppo_agent.generate_action(game_frame_buffer)
            #print(action, label, value)
            key, value = random.choice(list(self.game_inputs.items()))
            self.input_controller.tap_key(value[0])


    def check_game_state(self, game_frame):
        #game over?
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
        sprite_locator = SpriteLocator()
        locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print(locationGO)
        #won game?
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteWO.image_data)
        sprite_locator = SpriteLocator()
        locationWO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print(locationWO)
        self.is_alive = locationGO== None and locationWO== None
        self.restart_game =  not self.is_alive
        self.victory = locationGO== None and locationWO!= None

        print(f"Is allive? {self.is_alive}")
        print(f"Won? {self.victory}")

        for i, game_frame in enumerate(self.game_frame_buffer.frames):
            self.visual_debugger.store_image_data(
                game_frame.frame,
                game_frame.frame.shape,
                str(i)
            )