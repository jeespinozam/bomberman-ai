import time
import os
import pickle
#import serpent.cv

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

#from .helpers.game_status import Game
from .helpers.terminal_printer import TerminalPrinter
from .helpers.ppo import SerpentPPO


import random

class SerpentBombermanGameAgent(GameAgent):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.frame_handlers["PLAY"] = self.handle_play

		self.frame_handler_setups["PLAY"] = self.setup_play

		self.value = None
		print("Sprites")
		print(type(self.game.sprites))
		print("game")
		print(self.game)
		print("game type")
		print(type(self.game))
		for i,value in enumerate(self.game.sprites):
			if(i==13):
				print(value)
				self.value = value
		self.spriteGO = self.game.sprites.get("SPRITE_GAME_OVER")
		self.spriteWO = self.game.sprites.get("SPRITE_GAME_WON")
		#self.sprite.image_data
		self.printer = TerminalPrinter()

	def setup_play(self):
		game_inputs = {
		"Move Up": [KeyboardKey.KEY_UP],
		"Move Down": [KeyboardKey.KEY_DOWN],
		"Move Left": [KeyboardKey.KEY_LEFT],
		"Move Right": [KeyboardKey.KEY_RIGHT],
		"Leave Bomb": [KeyboardKey.KEY_SPACE]
		}
		self.game_inputs = game_inputs

		# self.ppo_agent = SerpentPPO(
		# frame_shape=(125, 112, 4),
		# game_inputs=game_inputs
		# )

		self.first_run = True
		self.game_over = False
		self.current_attempts = 0
		self.run_reward = 0
		self.started_at = datetime.utcnow().isoformat()
		self.paused_at = None

		print("Enter - Auto Save")
		self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
		time.sleep(2)

		return

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

		inputs = [KeyboardKey.KEY_UP,
			KeyboardKey.KEY_DOWN,
			KeyboardKey.KEY_LEFT,
			KeyboardKey.KEY_RIGHT,
			KeyboardKey.KEY_SPACE]

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

		if(locationGO!= None or locationWO!= None):
			#enter clic in both cases
			self.input_controller.tap_key(KeyboardKey.KEY_ENTER)
		else:
			self.input_controller.tap_key(inputs[random.randint(0,4)])

		for i, game_frame in enumerate(self.game_frame_buffer.frames):
			self.visual_debugger.store_image_data(
			game_frame.frame,
			game_frame.frame.shape,
			str(i)
			)
