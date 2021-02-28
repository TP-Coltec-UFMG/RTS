#Imports
from noise import pnoise2
import numpy as np
import pygame

#Constantes
HEIGHT = 800
WIDTH = 600
AMARELO = (255, 255, 0)
AMARELO_CLARO = (200, 200, 100)
PRETO = (0, 0, 0)
AZUL = (0, 43, 255)
VERDE = (0, 146, 10)

RAZAO = (30, 40)
#Razão a partir da qual são construidos todos os elementos do jogo (cada pixel é um retangulo de 30 por 40, ou qualquer que sejam os dois números ali em cima)

num_colunas = WIDTH // RAZAO[0]
num_linhas = HEIGHT // RAZAO[1]

#Inicialização
pygame.init()
pygame.display.set_caption("minimal program")
SCREEN = pygame.display.set_mode((HEIGHT, WIDTH), 0)
SCREEN.blit(SCREEN, (0, 0))

#User events
computa_trabalhos = pygame.USEREVENT + 0

class Control:
    def __init__(self):
        self.lista_tropas = []  # uma lista com todas as tropas
        self.tropas_selecionadas = []  # uma lista com todas as tropas selecionadas
        self.lista_florestas = []  # uma lista com as florestas
        self.lista_construcoes = []
        self.lista_minas = []
        self.num_gold = 0

    def screen_coordinates_to_grid(self, pos):
        tupla = (pos[0] // num_linhas, pos[1] // num_colunas)
        return tupla

    def grid_to_screen_coordinates(self, grid):
        tupla = (grid[0] * num_linhas, grid[1] * num_colunas)
        return tupla

    def cria_tropa(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        tropa = Tropa(pos)
        self.lista_tropas.append(tropa)

    def cria_worker(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        worker = Worker(pos)
        self.lista_tropas.append(worker)

    def pinta_tropas(self):  # itera através da lista de tropas e pinta
        for tropa in self.lista_tropas:
            if tropa.hidden == False:
                tropa.pinta_tropa(SCREEN)

    def pinta_florestas(self):  # itera através da lista de florestas e pinta
        for floresta in self.lista_florestas:
            floresta.pinta_floresta(SCREEN)

    def pinta_contrucoes(self):
        for construcao in self.lista_construcoes:
            construcao.pinta_construcao(SCREEN)

    def pinta_minas(self):
        for mina in self.lista_minas:
            mina.pinta_mina(SCREEN)


    def processar_eventos(self, eventos):
        for evento in eventos:

            if evento.type == computa_trabalhos:
                for mina in self.lista_minas:
                    self.num_gold += mina.computa_trabalho()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if evento.button == 1:  # botão esquerdo
                    if self.verifica_tropa(pos) is not None:
                        t = self.verifica_tropa(pos)
                        t.cor = AMARELO  # seleciona uma tropa caso uma já exista no lugar,
                        # a pinta de AMARELO e a adiciona a lista de tropas selecionadas
                        if t not in self.tropas_selecionadas:
                            self.tropas_selecionadas.append(t)
                            self.organiza_tropas_selecionadas()
                if evento.button == 1:  # botão esquerdo
                    if self.verifica_tropa(pos) is None and self.verifica_floresta(pos) is None:
                        self.cria_tropa(pos)  # cria uma tropa caso não hajam outras tropas ou florestas no lugar

                if evento.button == 3:  # botão direito
                    if self.tropas_selecionadas is not None and self.verifica_mina(pos) is not None:
                        for tropa in self.tropas_selecionadas:
                            if isinstance(tropa, Worker):
                                tropa.trabalha(self.verifica_mina(pos))
                                self.tropas_selecionadas.remove(tropa)

            if evento.type == pygame.KEYDOWN:
                pos = pygame.mouse.get_pos()
                if evento.key == pygame.K_e:  # limpa lista de tropas selecionadas
                    for tropa in self.tropas_selecionadas:
                        tropa.cor = AZUL
                    self.tropas_selecionadas.clear()

                if evento.key == pygame.K_r: #cria trabalhadores
                    if self.verifica_tropa(pos) is None and self.verifica_floresta(pos) is None:
                        self.cria_worker(pos)  # cria uma tropa caso não hajam outras tropas ou florestas no lugar

                if evento.key == pygame.K_UP:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0], tropa.pos[1] - num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropa(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_DOWN:
                    for tropa in reversed(self.tropas_selecionadas):
                        next = (tropa.pos[0], tropa.pos[1] + num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropa(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_RIGHT:
                    for tropa in reversed(self.tropas_selecionadas):
                        next = (tropa.pos[0] + num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropa(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_LEFT:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0] - num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropa(next) is None:
                            tropa.pos = next

    def verifica_tropa(self, pos):  # Verifica se alguma tropa já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for tropa in self.lista_tropas:
            if pos == tropa.pos:
                return tropa
        return None

    def organiza_tropas_selecionadas(self): #organiza a lista de tropas selecionadas pra facilitar movimento
        self.tropas_selecionadas.sort(key = lambda tropa: (tropa.pos[1], tropa.pos[0]))

    def verifica_floresta(self, pos):  # Verifica se alguma floresta já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for floresta in self.lista_florestas:
            if pos == floresta.pos:
                return floresta
        return None

    def verifica_mina(self, pos):  # Verifica se alguma mina já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for mina in self.lista_minas:
            if pos == mina.pos:
                return mina
        return None

    def gera_mapa(self, shape=(RAZAO[1], RAZAO[0]),  # gera um array de ruido 2d
                  scale=100, octaves=6,
                  persistence=0.5,
                  lacunarity=2.0,
                  seed=None):

        if not seed:
            seed = np.random.randint(0, 100)

        arr = np.zeros(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                arr[i][j] = pnoise2(i / scale,
                                    j / scale,
                                    octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=1024,
                                    repeaty=1024,
                                    base=seed)
        max_arr = np.max(arr)
        min_arr = np.min(arr)
        norm_me = lambda x: (x - min_arr) / (max_arr - min_arr)
        norm_me = np.vectorize(norm_me)
        arr = norm_me(arr)
        return arr

    def pinta_mapa(self, array):
        for x in range(RAZAO[1]):
            for y in range(RAZAO[0]):
                if array[x][y] > 0.5:
                    pos = (x * num_linhas, y * num_colunas)
                    floresta = Floresta(pos)
                    self.lista_florestas.append(floresta)


class Tropa:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = AZUL
        self.hidden = False

    def pinta_tropa(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Worker(Tropa):
    def __init__(self, pos):
        Tropa.__init__(self, pos)
        self.trabalhando = False

    def trabalha(self, target):
        self.trabalhando = True
        self.pos = target.pos
        self.hidden = True
        target.lista_trabalhadores.append(self)
    def sair_trabalho(self, target): #essa função só deve ser chamada pelo target
        self.trabalhando = False
        self.hidden = False

class Floresta:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = VERDE

    def pinta_floresta(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Construcao:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = AZUL
    def pinta_construcao(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas*2, num_linhas*2), 0)

class Mina:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = AMARELO_CLARO
        self.estoque = 10000
        self.lista_trabalhadores = []

    def pinta_mina(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

    def computa_trabalho(self):
        gold = 0
        for worker in self.lista_trabalhadores:
            self.estoque = self.estoque - 1
            if self.estoque == 0:
                del self
            gold = gold+1
        return gold

def main():
    RUN = True
    control = Control()
    control.pinta_mapa(control.gera_mapa(seed=20))

    base1 = Construcao((100, 400))
    control.lista_construcoes.append(base1)

    mina1 = Mina((220, 400))
    worker1 = Worker((220, 400))
    mina1.lista_trabalhadores.append(worker1)
    control.lista_minas.append(mina1)


    pygame.time.set_timer(computa_trabalhos, 1000)

    while RUN:

        SCREEN.fill(PRETO)
        control.pinta_tropas()
        control.pinta_florestas()
        control.pinta_contrucoes()
        control.pinta_minas()
        pygame.display.update()
        EVENTS = pygame.event.get()

        for event in EVENTS:
            if event.type == pygame.QUIT:
                RUN = False

        control.processar_eventos(EVENTS)
    pygame.quit()


if __name__ == "__main__":
    main()
