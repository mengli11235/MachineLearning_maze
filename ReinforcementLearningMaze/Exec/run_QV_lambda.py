from MazeEnv.maze_layouts_qv import MazeSmallQV, MazeLargeQV, MazeMediumQV
from LearningAlgos.QV_lambda_RL import QTable, VTable
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
# import matplotlib.pyplot as plt
import time
import math
import pandas as pd


def learning(total_steps, max_steps, time_in_ms, _is_render, QL, VL, env):
    # store the data of learning process for the plotting later
    episode = 0
    step_counter = 0
    rewards = []
    time_array = []
    epo = []
    step_array = []
    per_5 = math.floor(total_steps / 20)
    training_time = time.time()

    while True:
        force_exit = False

        # initialize the agent
        agent = env.reset()
        reward_in_each_epi = 0
        init_time = time.time()

        for step in range(max_steps):
            step_counter = step_counter + 1
            if step_counter % per_5 == 0:
                print("{} %".format((step_counter / per_5) * 5))
                print()

            # refresh rendering
            env.render(time_in_ms)

            # choose action based on current state
            current_state = str(agent)
            action = QL.choose_action(current_state)

            # take action and get next state and reward
            new_state, reward, is_done = env.taking_action(action)
            reward_in_each_epi += reward

            if step == max_steps - 1:
                force_exit = True

            # learning
            QL.learn(VL, agent, action, reward, new_state, is_done, force_exit)
            VL.update(current_state, reward, str(new_state), is_done)

            # assign to update variables
            agent = new_state

            # break the loop
            if is_done or step_counter >= total_steps:
                break

        episode = episode + 1
        rewards.append(reward_in_each_epi)
        time_array.append(format(time.time() - init_time, '.2f'))
        epo.append(episode + 1)
        step_array.append(step)

        if step_counter >= total_steps:
            break

    # end of game
    print('game over')
    # print training time
    training_time = time.time() - training_time
    m, s = divmod(training_time, 60)
    h, m = divmod(m, 60)
    print("Total training time: %d hr %02d min %02d sec" % (h, m, s))

    # store the table as csv
    QL.q_table.to_csv("temp_qv_qtable.csv", sep=',', encoding='utf-8')

    # plot the learning progress
    axes = plt.gca()
    axes.set_ylim([-1000, 1000])
    plt.figure(1)
    plt.plot(epo[:-1], rewards[:-1])
    plt.ylabel("rewards")
    plt.xlabel("epoches")
    plt.title("small maze rewards: QV_lambda(lambda=0.8)")

    plt.figure(2)
    plt.plot(epo[:-1], step_array[:-1])
    plt.ylabel("steps")
    plt.xlabel("epoches")
    plt.title("small maze steps: QV_lambda(lambda=0.8)")
    plt.show()

    if _is_render:
        time.sleep(1)
        env.destroy()


def running(epi, time_in_ms, _is_render, QL, VL, env):
    try:
        qdf = pd.DataFrame.from_csv("temp_qv_qtable.csv", sep=',', encoding='utf8')
        # vdf = pd.DataFrame.from_csv("temp_qv_vtable.csv", sep=',', encoding='utf8')
        QL.set_prior_qtable(qdf)
        # VL.set_prior_vtable(vdf)
        print("set prior q")
    except Exception:
        pass

    for episode in range(epi):
        # initiate the agent
        agent = env.reset()
        reward_in_each_epi = 0

        while True:
            # fresh env
            env.render(time_in_ms)

            # RL choose action based on observation
            current_state = str(agent)
            action = QL.choose_action(current_state)

            # RL take action and get next observation and reward
            new_state, reward, is_done = env.taking_action(action)
            reward_in_each_epi += reward

            # swap observation
            agent = new_state

            # break while loop when end of this episode
            if is_done:
                # print(epo)
                break

        if _is_render:
            print(reward_in_each_epi)

    # end of game)
    print('game over')
    if _is_render:
        time.sleep(500)
        env.destroy()


if __name__ == "__main__":
    # set if render the GUI of learning
    is_render = False

    # when is_demo set as True, no learning but running GUI to show the learning outcome
    is_demo = False

    # set number of total steps
    total_steps = 5000  # 60000 for medium, 5000(0.5,0.8), 6000(0) for simple
    # animation interval
    interval = 0.005
    # maximal number of states
    max_steps = 150  # 1000 for medium, 150(0.5,0.8), 200(0) for simple

    # initial position of the agent
    # all position count from 0
    init_pos = [0, 0]

    # initiate maze simulator for learning and running
    if is_demo:
        is_render = True

    maze = MazeSmallQV(init_pos).init_maze(is_render)
    # maze = MazeMediumQV(init_pos).init_maze(is_render)

    # initialize QLearner
    actions = list(range(maze.n_actions))
    learning_rate_v = 0.1
    learning_rate_q = 0.1
    reward_gamma = 0.95
    greedy = 0.9
    lambda_v = 0.8
    max_reward_coefficient = 0.75
    QLearner = QTable(actions, learning_rate_q, reward_gamma, greedy, max_reward_coefficient)
    Vlearner = VTable(learning_rate_v, reward_gamma, lambda_v)

    # run the training
    if not is_demo:
        if is_render:
            maze.after(1, learning(total_steps, max_steps, interval, is_render, QLearner, Vlearner, maze))
            maze.mainloop()
        else:
            learning(total_steps, max_steps, interval, is_render, QLearner, Vlearner, maze)
    # run the simulation of result
    else:
        # Q decision with 99% greedy strategy
        demo_greedy = 0.99
        demo_interval = 0.05
        QLearner = QTable(actions, learning_rate_q, reward_gamma, demo_greedy, max_reward_coefficient)
        Vlearner = VTable(learning_rate_v, reward_gamma, lambda_v)
        running(30, demo_interval, True, QLearner, Vlearner, maze)

