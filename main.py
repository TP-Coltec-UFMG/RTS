from noise import pnoise2
import numpy as np
import pygame

pygame.init()
pygame.display.set_caption("minimal program")

screen_altura = 800
screen_largura = 600

screen = pygame.display.set_mode((screen_altura, screen_largura), 0)
screen.blit(screen, (0, 0))

amarelo = (255, 255, 0)
amarelo_claro = (200, 200, 100)
preto = (0, 0, 0)
azul = (0, 43, 255)
verde = (0, 146, 10)

razao_unidade_tela = (30, 40)

num_colunas = screen_largura // razao_unidade_tela[0]
num_linhas = screen_altura // razao_unidade_tela[1]


class Control:
    def __init__(self):
        self.lista_tropas = []  # uma lista com todas as tropas
        self.tropas_selecionadas = []  # uma lista com todas as tropas selecionadas
        self.lista_florestas = []  # uma lista com as florestas
        self.lista_construcoes = []
        self.lista_minas = []
        self.num_gold = 0

    def mouse_position_to_grid(self, pos):
        tupla = (pos[0] // num_linhas, pos[1] // num_colunas)
        return tupla

    def grid_to_mouse_position(self, grid):
        tupla = (grid[0] * num_linhas, grid[1] * num_colunas)
        return tupla

    def cria_tropa(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        tropa = Tropa(pos)
        self.lista_tropas.append(tropa)

    def pinta_tropas(self):  # itera através da lista de tropas e pinta
        for tropa in self.lista_tropas:
            if tropa.hidden == False:
                tropa.pinta_tropa(screen)

    def pinta_florestas(self):  # itera através da lista de florestas e pinta
        for floresta in self.lista_florestas:
            floresta.pinta_floresta(screen)

    def pinta_contrucoes(self):
        for construcao in self.lista_construcoes:
            construcao.pinta_construcao(screen)

    def pinta_minas(self):
        for mina in self.lista_minas:
            mina.pinta_mina(screen)


    def processar_eventos(self, eventos):
        for evento in eventos:

            if evento.type == computa_trabalhos:
                for mina in self.lista_minas:
                    self.num_gold += mina.computa_trabalho()
                    print(self.num_gold)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if evento.button == 1:  # botão esquerdo
                    if self.verifica_tropa(pos) is not None:
                        t = self.verifica_tropa(pos)
                        t.cor = amarelo  # seleciona uma tropa caso uma já exista no lugar,
                        # a pinta de amarelo e a adiciona a lista de tropas selecionadas
                        if t not in self.tropas_selecionadas:
                            self.tropas_selecionadas.append(t)
                if evento.button == 1:  # botão esquerdo
                    if self.verifica_tropa(pos) is None and self.verifica_floresta(pos) is None:
                        self.cria_tropa(pos)  # cria uma tropa caso não hajam outras tropas ou florestas no lugar

                if evento.button == 2:  # botão direito
                    if self.tropas_selecionadas is not None and self.verifica_mina(pos) is not None:
                        for tropa in self.tropas_selecionadas:
                            if tropa is Worker:
                                tropa.trabalha(self.verifica_mina(pos))

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:  # limpa lista de tropas selecionadas
                    for tropa in self.tropas_selecionadas:
                        tropa.cor = azul
                    self.tropas_selecionadas.clear()

                if evento.key == pygame.K_UP:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0], tropa.pos[1] - num_linhas)
                        if self.verifica_floresta(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_DOWN:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0], tropa.pos[1] + num_linhas)
                        if self.verifica_floresta(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_RIGHT:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0] + num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None:
                            tropa.pos = next
                if evento.key == pygame.K_LEFT:
                    for tropa in self.tropas_selecionadas:
                        next = (tropa.pos[0] - num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None:
                            tropa.pos = next

    def verifica_tropa(self, pos):  # Verifica se alguma tropa já está nessa posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        for tropa in self.lista_tropas:
            if pos == tropa.pos:
                return tropa
        return None

    def verifica_floresta(self, pos):  # Verifica se alguma floresta já está nessa posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        for floresta in self.lista_florestas:
            if pos == floresta.pos:
                return floresta
        return None

    def verifica_mina(self, pos):  # Verifica se alguma mina já está nessa posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        for mina in self.lista_minas:
            if pos == mina.pos:
                return mina
        return None

    def gera_mapa(self, shape=(razao_unidade_tela[1], razao_unidade_tela[0]),  # gera um array de ruido 2d
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
        for x in range(razao_unidade_tela[1]):
            for y in range(razao_unidade_tela[0]):
                if array[x][y] > 0.5:
                    pos = (x * num_linhas, y * num_colunas)
                    floresta = Floresta(pos)
                    self.lista_florestas.append(floresta)


class Tropa:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = azul
        self.hidden = False

    def pinta_tropa(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Worker(Tropa):
    def __init__(self):
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
        self.cor = verde

    def pinta_floresta(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Construcao:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = azul
    def pinta_construcao(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas*2, num_linhas*2), 0)

class Mina:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = amarelo_claro
        self.estoque = 10000
        self.lista_trabalhadores = []

    def pinta_mina(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

    def computa_trabalho(self):
        gold = 0
        for worker in self.lista_trabalhadores:
            self.estoque = self.estoque - 1
            if self.estoque == 0:
                del self
            gold = gold+1
        return gold


if __name__ == "__main__":

    control = Control()
    control.pinta_mapa(control.gera_mapa(seed=20))

    base1 = Construcao((100, 400))
    control.lista_construcoes.append(base1)

    mina1 = Mina((220, 400))
    worker1 = Worker()
    mina1.lista_trabalhadores.append(worker1)
    control.lista_minas.append(mina1)


    computa_trabalhos = pygame.USEREVENT + 0
    pygame.time.set_timer(computa_trabalhos, 1000)

    while True:

        screen.fill(preto)
        control.pinta_tropas()
        control.pinta_florestas()
        control.pinta_contrucoes()
        control.pinta_minas()
        pygame.display.update()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                exit(2)

        control.processar_eventos(events)
