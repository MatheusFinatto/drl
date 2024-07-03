
import json
import random
import numpy as np
import pygame


class Ambiente:
    def __init__(self, size=10, qtdPolicia=8, qtdDerby=5, numeroDeAmbulantes=3):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.estadoInicial = self.randomPlacing(1).pop()
        self.estadoObjetivo = self.randomPlacing(1).pop()
        self.estadoPolicia = self.randomPlacing(qtdPolicia,)
        self.estadosDerby = self.randomPlacing(qtdDerby, exclude=self.estadoPolicia)
        self.estadosAmbulantes = self.randomPlacing(numeroDeAmbulantes, exclude=self.estadoPolicia | self.estadosDerby)
        self.qtdDerbyColetados = set()
        self.update()
        self.carregarImagens()

    def carregarImagens(self):
        self.agente = pygame.image.load('./assets/f1000.png')
        self.cigarro = pygame.image.load('./assets/derby.png')
        self.fronteira = pygame.image.load('./assets/fronteira.png')
        self.vendedorAmbulante = pygame.image.load('./assets/ambulante.png')
        self.policia = pygame.image.load('./assets/policia.jpg')
        self.fundo = pygame.image.load('./assets/rua.jpg')

    def randomPlacing(self, num_items, exclude=set()):
        all_positions = {(i, j) for i in range(self.size) for j in range(self.size)}
        valid_positions = list(all_positions - exclude)
        if num_items > len(valid_positions):
            raise ValueError("Number of items exceeds available valid positions.")
        return set(random.sample(valid_positions, num_items))

    def update(self):
        self.grid.fill(0)
        for i, j in self.estadoPolicia:
            self.grid[i][j] = 1
        for i, j in self.estadosDerby:
            self.grid[i][j] = 2
        for i, j in self.estadosAmbulantes:
            self.grid[i][j] = 3

    def verificaReward(self):
        if self.estadoAtual == self.estadoObjetivo:
            if len(self.qtdDerbyColetados) == len(self.estadosDerby):
                return 10, True
            else:
                return -1, False
        elif self.estadoAtual in self.estadoPolicia:
            return -5, True
        elif self.estadoAtual in self.estadosDerby and self.estadoAtual not in self.qtdDerbyColetados:
            self.qtdDerbyColetados.add(self.estadoAtual)
            return 2, False
        else:
            return -0.1, False

    def validaMov(self, proxEstado):
        if proxEstado in self.estadosAmbulantes:
            return self.estadoAtual
        return proxEstado

    def step(self, action):
        i, j = self.estadoAtual
        proxEstado = self._move(i, j, action)
        self.estadoAtual = self.validaMov(proxEstado)
        reward, done = self.verificaReward()
        return self.estadoAtual, tuple(self.qtdDerbyColetados), reward, done

    def _move(self, i, j, action):
        if action == 0: 
            i = max(i-1, 0)
        elif action == 1:
            i = min(i+1, self.size-1)
        elif action == 2:
            j = max(j-1, 0)
        elif action == 3:
            j = min(j+1, self.size-1)
        return (i, j)

    def reset(self):
        self.estadoAtual = self.estadoInicial
        self.qtdDerbyColetados = set()
        return self.estadoAtual, tuple(self.qtdDerbyColetados)

    def render(self, screen, cell_size=60):
        screen.fill((200, 200, 200))
        for i in range(self.size):
            for j in range(self.size):
                self._draw_item(screen, i, j, cell_size)
        pygame.display.flip()

    def _draw_item(self, screen, i, j, cell_size):
        screen.blit(pygame.transform.scale(self.fundo, (cell_size, cell_size)), (j * cell_size, i * cell_size))
        if (i, j) == self.estadoAtual:
            img = self.agente
        elif (i, j) == self.estadoObjetivo:
            img = self.fronteira
        elif self.grid[i][j] == 1:
            img = self.policia
        elif self.grid[i][j] == 2 and (i, j) not in self.qtdDerbyColetados:
            img = self.cigarro
        elif self.grid[i][j] == 3:
            img = self.vendedorAmbulante
        else:
            img = None

        if img:
            screen.blit(pygame.transform.scale(img, (cell_size, cell_size)), (j * cell_size, i * cell_size))

    def save_q_table(self, q_table, filename='q_table_and_environment.json'):
        data = {
            'q_table': q_table.tolist(),
            'environment_info': {
                'size': self.size,
                'qtdPolicia': list(self.estadoPolicia),
                'qtdDerby': list(self.estadosDerby),
                'numeroDeAmbulantes': list(self.estadosAmbulantes),
                'estadoInicial': self.estadoInicial,
                'estadoObjetivo': self.estadoObjetivo
            }
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Tabela Q e informações do ambiente salvas em {filename}")

    def load_q_table(self, filename='q_table_and_environment.json'):
        with open(filename, 'r') as f:
            data = json.load(f)
            q_table = np.array(data['q_table'])
            environment_info = data['environment_info']
            self.size = environment_info['size']
            self.estadoInicial = tuple(environment_info['estadoInicial'])
            self.estadoObjetivo = tuple(environment_info['estadoObjetivo'])
            self.estadoPolicia = set(tuple(pos) for pos in environment_info['qtdPolicia'])
            self.estadosDerby = set(tuple(pos) for pos in environment_info['qtdDerby'])
            self.estadosAmbulantes = set(tuple(pos) for pos in environment_info['numeroDeAmbulantes'])
            self.qtdDerbyColetados = set()
            self.update()
            self.carregarImagens()
            print(f"Tabela Q carregada de {filename}")
            return q_table