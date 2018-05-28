from tensorforce.agents import PPOAgent

from serpent.utilities import SerpentError

import numpy as np

# This file is borrowed from SerpentAIsaacGameAgentPlugin:
# https://github.com/SerpentAI/SerpentAIsaacGameAgentPlugin/blob/master/files/helpers/ppo.py
class SerpentPPO:

	def __init__(self, frame_shape=None, game_inputs=None):

		if frame_shape is None:
			raise SerpentError("A 'frame_shape' tuple kwarg is required...")

		states_spec = {"type": "float", "shape": frame_shape}

		if game_inputs is None:
			raise SerpentError("A 'game_inputs' dict kwarg is required...")

		self.game_inputs = game_inputs
		self.game_inputs_mapping = self._generate_game_inputs_mapping()

		actions_spec = {"type": "int", "num_actions": len(self.game_inputs)}

		summary_spec = {
			"directory": "./board/",
			"steps": 50,
			"labels": [
				"configuration",
				"gradients_scalar",
				"regularization",
				"inputs",
				"losses",
				"variables"
			]
		}

		network_spec = [
			{"type": "conv2d", "size": 32, "window": 8, "stride": 4},
			{"type": "conv2d", "size": 64, "window": 4, "stride": 2},
			{"type": "conv2d", "size": 64, "window": 3, "stride": 1},
			{"type": "flatten"},
			{"type": "dense", "size": 1024}
		]

		self.agent = PPOAgent(
			states=states_spec,
			actions=actions_spec,
			network=network_spec,
			batched_observe=2560,
			batching_capacity=1000,
			# BatchAgent
			#keep_last_timestep=True,
			# PPOAgent
			step_optimizer=dict(
				type='adam',
				learning_rate=1e-3
			),
			optimization_steps=10,
			# Model
			scope='ppo',
			discount=0.97,
			# DistributionModel
			distributions=None,
			entropy_regularization=0.01,
			# PGModel
			baseline_mode=None,
			baseline=None,
			baseline_optimizer=None,
			gae_lambda=None,
			# PGLRModel
			likelihood_ratio_clipping=None,
			#summary_spec=summary_spec,
			#distributed_spec=None,
			# More info
			device=None,
			#session_config=None,
			saver=None,
			variable_noise=None,
			#states_preprocessing_spec=None,
			#explorations_spec=None,
			#reward_preprocessing_spec=None,

			summarizer=None,
			execution=None,
			actions_exploration=None,
			update_mode=None,
			memory=None,
			subsampling_fraction=0.1
		)

	def generate_action(self, game_frame_buffer):
		states = np.stack(
			[game_frame.frame for game_frame in game_frame_buffer.frames],
			axis=2
		)

		# Get prediction from agent, execute
		action = self.agent.act(states)
		label = self.game_inputs_mapping[action]

		return action, label, self.game_inputs[label]

	def observe(self, reward=0, terminal=False):
		self.agent.observe(reward=reward, terminal=terminal)

	def _generate_game_inputs_mapping(self):
		mapping = dict()

		for index, key in enumerate(self.game_inputs):
			mapping[index] = key

		return mapping