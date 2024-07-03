import sys
import pygame
from ambiente import Ambiente
from helpers import initialize_q_table, train_agent, test_agent

# Parâmetros de treinamento
episodes = 20000
max_steps = 200
epsilon = 1.0
min_epsilon = 0.01
epsilon_decay_rate = 0.001
discount_factor = 0.99
learning_rate = 0.1

isTrained = True


if __name__ == "__main__":
    environment = Ambiente(size=7, qtdPolicia=4, qtdDerby=3, numeroDeAmbulantes=6)
    pygame.init()
    cell_size = 60
    screen = pygame.display.set_mode((environment.size * cell_size, environment.size * cell_size))
    pygame.display.set_caption('Cigaro contrabando simulator')

    if isTrained:
        q_table = environment.load_q_table()
        test_agent(environment, q_table, screen, cell_size)
    else:
        q_table = initialize_q_table(environment)
        print("Inicializando nova tabela Q.")
        train_agent(environment, q_table, screen, cell_size, episodes, max_steps, learning_rate, discount_factor, epsilon, min_epsilon, epsilon_decay_rate)
        test_agent(environment, q_table, screen, cell_size)

    pygame.quit()
    sys.exit()
