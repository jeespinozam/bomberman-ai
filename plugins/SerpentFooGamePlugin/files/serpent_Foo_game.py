from serpent.game import Game

from .api.api import FooAPI

from serpent.utilities import Singleton

from serpent.game_launchers.web_browser_game_launcher import WebBrowser


class SerpentFooGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "web_browser"

        #kwargs["window_name"] = "HTML5 Bombergirl - Google Chrome"
        kwargs["window_name"] = "HTML5 Bombergirl"

        kwargs["url"] = "https://gd-bomberman.herokuapp.com/"
        kwargs["browser"] = WebBrowser.DEFAULT
        #kwargs["browser"] = WebBrowser.CHROME

        super().__init__(**kwargs)

        self.api_class = FooAPI
        self.api_instance = None

    @property
    def screen_regions(self):

        dic_offset = {
            "WINDOWS_CHROME": {
                "top": 81,
                "left": 5
            },
            "SAFARI":{
                "top": 0,
                "left": 0
            }
        }

        offset = dic_offset["SAFARI"]

        regions = {
            "GAME_REGION": (offset["top"], offset["left"], 416 + offset["top"], 544 + offset["left"]), #544x416
            "GAME_OVER_REGION": (118 + offset["top"], 163 + offset["left"], 151 + offset["top"], 383 + offset["left"]), #220x33 - 163,118
            "WIN_REGION": (118 + offset["top"], 171 + offset["left"], 149 + offset["top"], 372 + offset["left"]), # 201x31  - 171,118
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