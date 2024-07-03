import random
import numpy as np
import pygame


def initialize_q_table(environment):
    return np.zeros((environment.size, environment.size, 2 ** len(environment.estadosDerby), 4))

def epsilon_greedy_policy(state, collected_supplies, q_table, environment, epsilon):
    supply_index = get_supply_index(collected_supplies, environment)
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, 3)
    else:
        return np.argmax(q_table[state[0]][state[1]][supply_index])

def get_supply_index(collected_supplies, environment):
    return int(''.join(['1' if (i, j) in collected_supplies else '0' for (i, j) in environment.estadosDerby]), 2)

def train_agent(environment, q_table, screen, cell_size, num_episodes=10000, max_steps_per_episode=100, learning_rate=0.1, discount_factor=0.99, epsilon=1.0, min_epsilon=0.01, epsilon_decay_rate=0.001):
    for episode in range(num_episodes):
        state, collected_supplies = environment.reset()
        done = False
        t = 0
        while not done and t < max_steps_per_episode:
            action = epsilon_greedy_policy(state, collected_supplies, q_table, environment, epsilon)
            proxEstado, next_collected_supplies, reward, done = environment.step(action)
            update_q_table(q_table, state, collected_supplies, action, reward, proxEstado, next_collected_supplies, environment, learning_rate, discount_factor)
            state, collected_supplies = proxEstado, next_collected_supplies
            t += 1
        epsilon = max(min_epsilon, epsilon * (1 - epsilon_decay_rate))
        if episode % 1000 == 0:
            print(f'Episode: {episode}')
            environment.render(screen, cell_size)
    environment.save_q_table(q_table)

def update_q_table(q_table, state, collected_supplies, action, reward, proxEstado, next_collected_supplies, environment, learning_rate, discount_factor):
    supply_index = get_supply_index(collected_supplies, environment)
    next_supply_index = get_supply_index(next_collected_supplies, environment)
    q_table[state[0]][state[1]][supply_index][action] += learning_rate * \
        (reward + discount_factor * np.max(q_table[proxEstado[0]][proxEstado[1]][next_supply_index]) - q_table[state[0]][state[1]][supply_index][action])

def test_agent(environment, q_table, screen, cell_size=60):
    state, collected_supplies = environment.reset()
    done = False
    environment.render(screen, cell_size)
    pygame.time.wait(500)
    while not done:
        supply_index = get_supply_index(collected_supplies, environment)
        action = np.argmax(q_table[state[0]][state[1]][supply_index])
        proxEstado, next_collected_supplies, reward, done = environment.step(action)
        environment.render(screen, cell_size)
        pygame.time.wait(500)
        state, collected_supplies = proxEstado, next_collected_supplies