# import time
# import os
# import pickle
# import serpent.cv
#
# import numpy as np
# import collections
#
# from datetime import datetime
#
#
# from serpent.frame_transformer import FrameTransformer
# from serpent.frame_grabber import FrameGrabber
# from serpent.game_agent import GameAgent
# from serpent.input_controller import KeyboardKey
# from serpent.sprite import Sprite
# from serpent.sprite_locator import SpriteLocator
# from serpent.sprite_identifier import SpriteIdentifier
#
# # from .helpers.game_status import Game
# from .helpers.terminal_printer import TerminalPrinter
# from .helpers.ppo import SerpentPPO
#
#
# import random
#
# class SerpentBombermanGameAgent(GameAgent):
#
# 	def __init__(self, **kwargs):
# 		super().__init__(**kwargs)
#
# 		self.frame_handlers["PLAY"] = self.handle_play
#
# 		self.frame_handler_setups["PLAY"] = self.setup_play
#
# 		self.value = None
# 		print("Sprites")
# 		print(type(self.game.sprites))
# 		print("game")
# 		print(self.game)
# 		print("game type")
# 		print(type(self.game))
# 		for i,value in enumerate(self.game.sprites):
# 			if(i==13):
# 				print(value)
# 				self.value = value
# 		self.spriteGO = self.game.sprites.get("SPRITE_GAME_OVER")
# 		self.spriteWO = self.game.sprites.get("SPRITE_GAME_WON")
# 		#self.sprite.image_data
# 		self.printer = TerminalPrinter()
#
# 	def setup_play(self):
# 		game_inputs = {
# 		"Move Up": [KeyboardKey.KEY_UP],
# 		"Move Down": [KeyboardKey.KEY_DOWN],
# 		"Move Left": [KeyboardKey.KEY_LEFT],
# 		"Move Right": [KeyboardKey.KEY_RIGHT],
# 		"Leave Bomb": [KeyboardKey.KEY_SPACE]
# 		}
# 		self.game_inputs = game_inputs
#
# 		# self.ppo_agent = SerpentPPO(
# 		#  frame_shape=(480, 549, 4),
# 		#  game_inputs=game_inputs
# 		# )
#
# 		self.first_run = True
# 		self.game_over = False
# 		self.current_attempts = 0
# 		self.run_reward = 0
# 		self.started_at = datetime.utcnow().isoformat()
# 		self.paused_at = None
#
# 		print("Enter - Auto Save")
# 		self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
# 		time.sleep(2)
#
# 		return
#
# 	def extract_game_area(self, frame_buffer):
# 		game_area_buffer = []
#
# 		for game_frame in frame_buffer.frames:
# 			game_area = serpent.cv.extract_region_from_image(
# 			game_frame.grayscale_frame,
# 			self.game.screen_regions["GAME_REGION"]
# 			)
#
# 			frame = FrameTransformer.rescale(game_area, 0.25)
# 			game_area_buffer.append(frame)
#
# 		return game_area_buffer
#
# 	def handle_play(self, game_frame):
# 		if self.first_run:
# 			self.current_attempts += 1
# 			self.first_run = False
# 			return None
#
# 		self.printer.add("")
# 		self.printer.add("BombermanAI")
# 		self.printer.add("Reinforcement Learning: Training a PPO Agent")
# 		self.printer.add("")
# 		self.printer.add(f"Stage Started At: {self.started_at}")
# 		self.printer.add(f"Current Run: #{self.current_attempts}")
# 		self.printer.add("")
#
# 		inputs = [KeyboardKey.KEY_UP,
# 			KeyboardKey.KEY_DOWN,
# 			KeyboardKey.KEY_LEFT,
# 			KeyboardKey.KEY_RIGHT,
# 			KeyboardKey.KEY_SPACE]
#
# 		#game over?
# 		sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
#
# 		sprite_locator = SpriteLocator()
# 		locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
# 		print(locationGO)
#
# 		#won game?
# 		sprite_to_locate = Sprite("QUERY", image_data=self.spriteWO.image_data)
# 		sprite_locator = SpriteLocator()
# 		locationWO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
# 		print(locationWO)
#
# 		print(type(game_frame))
#
# 		if(locationGO!= None or locationWO!= None):
# 			#enter clic in both cases
# 			self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
# 		else:
# 			game_frame_buffer = FrameGrabber.get_frames([0, 1, 2, 3], frame_type="PIPELINE")
# 			game_frame_buffer = self.extract_game_area(game_frame_buffer)
# 			action, label, value = self.ppo_agent.generate_action(game_frame_buffer)
#
# 			print(action, label, value)
# 			self.input_controller.tap_key(value)

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

class SerpentBombermanGameAgent(GameAgent):

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
        print(np.array(game_area_buffer).shape)
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
        #self.check_game_state(game_frame)

        #####################CHECK STATE###########################
        #game over?
        locationGO = None
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
        sprite_locator = SpriteLocator()
        locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print("Location Game over:",locationGO)
        #won game?
        locationWO = None
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteWO.image_data)
        sprite_locator = SpriteLocator()
        locationWO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print("Location Game won:",locationWO)

        self.gamestate.lose = locationGO!=None
        self.gamestate.victory = locationWO!= None
        self.gamestate.girl_alive = (locationGO== None and locationWO== None)
        self.gamestate.done =  not self.gamestate.girl_alive

        print(f"Is alive? {self.gamestate.girl_alive}")
        print(f"Game over? {self.gamestate.lose}")
        print(f"Won? {self.gamestate.victory}")
        #####################VISUAL DEBUGGER###########################
        for i, game_frame in enumerate(self.game_frame_buffer.frames):
            self.visual_debugger.store_image_data(
                game_frame.frame,
                game_frame.frame.shape,
                str(i)
            )

        #####################MODEL###########################
        #get buffer
        frame_buffer = FrameGrabber.get_frames([0, 1, 2, 3], frame_type="PIPELINE")
        game_frame_buffer = self.extract_game_area(frame_buffer)
        state = game_frame_buffer.reshape(4, 104, 136, 1)

        if(self.gamestate.done):
            print(f"Game over, attemp {self.epoch}")
            if (self.epoch % 10)== 0:
                print("saving model")
                self.dqn_agent.save_model(f"bombergirl_epoch_{self.epoch}.model")
                self.printer.save_file()
            self.printer.add(f"{self.gamestate.victory},{self.gamestate.lose},{self.epoch},{self.gamestate.time},{self.total_reward}")
            self.total_reward = 0
            self.dqn_agent.remember(self.prev_state, self.prev_action, self.prev_reward, state, True)
            self.dqn_agent.replay()
            self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
            self.epoch += 1
            self.total_reward = 0
            self.gamestate.restartState()
            self.prev_state = None
            self.prev_action = None
        else:
            #update time
            self.gamestate.updateTime()

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
            ###################FUN UPDATE STATE#########################################
            # self.update_game_state(game_frame_rand)
            game_area = \
                    serpent.cv.extract_region_from_image(game_frame_rand,self.game.screen_regions['GAME_REGION'])
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
            #game over?
            locationGO = None
            sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
            sprite_locator = SpriteLocator()
            locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
            print("Location Game over:",locationGO)

            if(locationGO!= NULL){
                self.gamestate.girl_alive = False
                self.gamestate.lose = True
            }

            ###################REWARD#########################################

            #get reward
            reward = self.gamestate.getReward(action_index)
            self.total_reward += reward
            self.prev_state = state
            self.prev_action = action_index
            self.prev_reward = reward

            if(action):
                self.input_controller.tap_key(action, 0.15 if action_index < 4 else 0.01)
            print(f"Action: {self.gamestate.game_inputs[action_index]}, reward: {reward}, total_reward: {self.total_reward}")
            #action, label, value = self.ppo_agent.generate_action(game_frame_buffer)
            #print(action, label, value)
            #key, value = random.choice(list(self.game_inputs.items()))
            #if(value[0]):
            #    self.input_controller.tap_key(value[0])
        #game_squares = self.extract_game_squares(game_frame.frame)



    def check_game_state(self, game_frame):
        #game over?
        locationGO = None
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteGO.image_data)
        sprite_locator = SpriteLocator()
        locationGO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print("Location Game over:",locationGO)
        #won game?
        locationWO = None
        sprite_to_locate = Sprite("QUERY", image_data=self.spriteWO.image_data)
        sprite_locator = SpriteLocator()
        locationWO = sprite_locator.locate(sprite=sprite_to_locate, game_frame=game_frame)
        print("Location Game won:",locationWO)

        self.gamestate.lose = locationGO!=None
        self.gamestate.victory = locationWO!= None
        self.gamestate.girl_alive = (locationGO== None and locationWO== None)
        self.gamestate.done =  not self.gamestate.girl_alive

        print(f"Is alive? {self.gamestate.girl_alive}")
        print(f"Game over? {self.gamestate.lose}")
        print(f"Won? {self.gamestate.victory}")
