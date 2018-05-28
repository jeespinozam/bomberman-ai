from serpent.game import Game

from .api.api import TestAPI

from serpent.utilities import Singleton

from serpent.game_launchers.web_browser_game_launcher import WebBrowser


class SerpentTestGame(Game, metaclass=Singleton):

	def __init__(self, **kwargs):
		kwargs["platform"] = "web_browser"

		kwargs["window_name"] = "HTML5 Bombergirl - Google Chrome"

		kwargs["url"] = "https://gd-bomberman.herokuapp.com/"
		kwargs["browser"] = WebBrowser.DEFAULT

		super().__init__(**kwargs)

		self.api_class = TestAPI
		self.api_instance = None

	@property
	def screen_regions(self):
		regions = {
			"GAME_REGION": (0, 0, 480, 549),
			"GAME_OVER_REGION": (160,160, 225, 404),
			"WIN_REGION": (175,130, 220, 421),
		}

		return regions

	@property
	def ocr_presets(self):
		presets = {
			"SAMPLE_PRESET": {
				"extract": {
					"gradient_size": 1,
					"closing_size": 1
				},
				"perform": {
					"scale": 10,
					"order": 1,
					"horizontal_closing": 1,
					"vertical_closing": 1
				}
			}
		}

		return presets
