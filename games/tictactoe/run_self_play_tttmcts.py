import datetime
import os
from os import listdir
from os.path import isfile, join

import torch
from games.algos.mcts import MCTreeSearch, ConvNetTicTacToe
from games.algos.q import EpsilonGreedy, QConvTicTacToe
from games.algos.self_play import SelfPlay
from games.tictactoe.tictactoe_env import TicTacToeEnv

save_dir = "saves"


def run_training():
    env = TicTacToeEnv()
    # policy = EpsilonGreedy(QConvTicTacToe(env, buffer_size=5000, batch_size=64), 0.1)
    policy = MCTreeSearch(ConvNetTicTacToe(3, 3, 9), TicTacToeEnv, temperature_cutoff=1, iterations=200, min_memory=64,)
    opposing_policy = EpsilonGreedy(
        QConvTicTacToe(env), 1
    )  # Make it not act greedily for the moment- exploration Acts greedily
    self_play = SelfPlay(policy, opposing_policy, env=env, swap_sides=True)
    self_play.train_model(20000, resume=False)
    print("Training Done")

    saved_name = os.path.join(save_dir, datetime.datetime.now().isoformat())
    torch.save(self_play.policy.q.policy_net.state_dict(), saved_name)


def resume_self_play():
    env = TicTacToeEnv()
    saves = [f for f in listdir(save_dir) if isfile(join(save_dir, f))]
    recent_file = max(saves)
    policy = EpsilonGreedy(QConvTicTacToe(env), 0)
    opposing_policy = EpsilonGreedy(QConvTicTacToe(env), 1)
    self_play = SelfPlay(policy, opposing_policy)
    policy.q.policy_net.load_state_dict(torch.load(join(save_dir, recent_file)))
    self_play.evaluate_policy(100)


def interactive_play():
    pass


if __name__ == "__main__":
    run_training()
    resume_self_play()

    # self_play.evaluate_policy(1000)
    # # self_play.policy.epsilon = 0
    # self_play.opposing_policy = EpsilonGreedy(QLinear(env), 0.1)
    # self_play.evaluate_policy(1000)
