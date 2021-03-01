#Imports
from noise import pnoise2
import numpy as np
import pygame
pygame.init()
import random

#Constantes
HEIGHT = 800
WIDTH = 600
AMARELO = (255, 255, 0)
AMARELO_CLARO = (200, 200, 100)
PRETO = (84, 84, 84)
AZUL = (0, 43, 255)
VERDE = (214, 255, 199)

RAZAO = (30, 40) #30 rows, 40 columns
#Razão a partir da qual são construidos todos os elementos do jogo (cada pixel é um retangulo de 30 por 40, ou qualquer que sejam os dois números ali em cima)

num_colunas = WIDTH // RAZAO[0]
num_linhas = HEIGHT // RAZAO[1]

FONTE = pygame.font.SysFont('Comic Sans MS', 25)

#Eventos do usuario
computa_trabalhos = pygame.USEREVENT + 0
pygame.time.set_timer(computa_trabalhos, 1000)

class Control:
    def __init__(self):
        self.lista_tropas_br = []  # uma lista com todas as tropas brasileiras
        self.lista_tropas_sp = []  # uma lista com todas as tropas paulistas
        self.tropas_selecionadas_br = []  # uma lista com todas as tropas brasileiras selecionadas
        self.tropas_selecionadas_sp = []  # uma lista com todas as tropas paulistas selecionadas
        self.lista_florestas = []  # uma lista com as florestas
        self.lista_construcoes_br = []
        self.lista_construcoes_sp = []
        self.lista_minas_br = []
        self.lista_minas_sp = []
        self.num_gold_br = 0
        self.num_gold_sp = 0

    def __eq__(self, other):
        if not isinstance(other, Control):
            return NotImplemented
        return self.lista_tropas_br == other.lista_tropas_br and self.lista_tropas_sp == other.lista_tropas_sp and self.tropas_selecionadas_br == other.tropas_selecionadas_br and self.tropas_selecionadas_sp == other.tropas_selecionadas_sp and self.lista_florestas == other.lista_florestas and self.lista_construcoes_br == other.lista_construcoes_br and self.lista_construcoes_sp == other.lista_construcoes_sp and self.lista_minas_br == other.lista_minas_br and self.lista_minas_sp == other.lista_minas_sp

    def screen_coordinates_to_grid(self, pos):
        tupla = (pos[0] // num_linhas, pos[1] // num_colunas)
        return tupla

    def grid_to_screen_coordinates(self, grid):
        tupla = (grid[0] * num_linhas, grid[1] * num_colunas)
        return tupla

    def cria_tropa_br(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        tropa = Tropa(pos, 30)
        self.lista_tropas_br.append(tropa)

    def cria_tropa_sp(self, pos):
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        tropa = Tropa(pos, 20)
        self.lista_tropas_sp.append(tropa)

    def cria_worker_br(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        worker = Worker(pos, 7)
        self.lista_tropas_br.append(worker)

    def cria_worker_sp(self, pos):  # cria uma tropa dada uma posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        worker = Worker(pos, 7)
        self.lista_tropas_sp.append(worker)

    def pinta_tropas(self, tela):  # itera através da lista de tropas e pinta | Atualizado
        for tropa in self.lista_tropas_br:
            if tropa.hidden == False:
                tropa.pinta_tropa_br(tela)
        for tropa in self.lista_tropas_sp:
            if tropa.hidden == False:
                tropa.pinta_tropa_sp(tela)

    def pinta_florestas(self, tela):  # itera através da lista de florestas e pinta | Nao precisa atualizacao
        for floresta in self.lista_florestas:
            floresta.pinta_floresta(tela)

    def pinta_contrucoes(self, tela): #Atualizado
        for construcao in self.lista_construcoes_br:
            construcao.pinta_construcao_br(tela)
        for construcao in self.lista_construcoes_sp:
            construcao.pinta_construcao_sp(tela)

    def pinta_minas(self, tela): #Atualizado
        for mina in self.lista_minas_br:
            mina.pinta_mina_br(tela)
        for mina in self.lista_minas_sp:
            mina.pinta_mina_sp(tela)

    def pinta_tela(self, tela):
        tela.fill(PRETO)
        self.pinta_tropas(tela) #Atualizado
        self.pinta_florestas(tela) #Nao precisa atualizacao
        self.pinta_contrucoes(tela) #Atualizado
        self.pinta_minas(tela) #Atualizado

        texto_gold_br = FONTE.render("Dinheiro: {}".format(self.num_gold_br), True, (128,128,128))
        texto_gold_sp = FONTE.render("Dinheiro: {}".format(self.num_gold_sp), True, (128,128,128))
        tela.blit(texto_gold_br, (0, 0))
        tela.blit(texto_gold_sp, (650, 0))

        texto_vida_base_br = FONTE.render("Vida: {}".format(self.lista_construcoes_br[0].vida), True, (128,128,128))
        texto_vida_base_sp = FONTE.render("Vida: {}".format(self.lista_construcoes_sp[0].vida), True, (128,128,128))
        tela.blit(texto_vida_base_br, (0, 50))
        tela.blit(texto_vida_base_sp, (650, 50))

        pygame.display.update()

    def processar_eventos(self, eventos, playerId):

        if self.lista_construcoes_br[0].vida <= 0:
            return 0
        if self.lista_construcoes_sp[0].vida <= 0:
            return 1

        for evento in eventos:

            if evento.type == computa_trabalhos:
                for mina in self.lista_minas_br:
                    self.num_gold_br += mina.computa_trabalho()

                for mina in self.lista_minas_sp:
                    self.num_gold_sp += mina.computa_trabalho()

            if evento.type == pygame.MOUSEBUTTONDOWN and playerId == 0: #Clique playerId=0 (BR)
                pos = pygame.mouse.get_pos()
                if evento.button == 1:  # botão esquerdo | Selecionar Tropas
                    if self.verifica_tropa_br(pos) is not None:
                        t = self.verifica_tropa_br(pos)
                        t.cor = AMARELO  # seleciona uma tropa caso uma já exista no lugar,
                        # a pinta de AMARELO e a adiciona a lista de tropas selecionadas
                        if t not in self.tropas_selecionadas_br:
                            self.tropas_selecionadas_br.append(t)
                            self.organiza_tropas_selecionadas()

                if evento.button == 1:  # botão esquerdo | Criar Tropas
                    mouse_pos = pygame.mouse.get_pos()
                    if 125 <= mouse_pos[0] <= 125+30 and 375 <= mouse_pos[1] <= 375+40 and self.verifica_tropas((125+20, 375+60)) == (None, None) and self.num_gold_br >=25:
                        self.num_gold_br -=25
                        self.cria_tropa_br((125+20, 375+60))

                if evento.button == 3:  # botão direito | Colocar Worker p Trbalahar
                    if self.tropas_selecionadas_br is not None and self.verifica_mina_br(pos) is not None:
                        for tropa in self.tropas_selecionadas_br:
                            if isinstance(tropa, Worker):
                                tropa.trabalha(self.verifica_mina_br(pos))
                                self.tropas_selecionadas_br.remove(tropa)

            if evento.type == pygame.MOUSEBUTTONDOWN and playerId == 1: #Clique playerId=1 (SP)
                pos = pygame.mouse.get_pos()
                if evento.button == 1:  # botão esquerdo | Selecionar Tropas
                    if self.verifica_tropa_sp(pos) is not None:
                        t = self.verifica_tropa_sp(pos)
                        t.cor = AMARELO  # seleciona uma tropa caso uma já exista no lugar,
                        # a pinta de AMARELO e a adiciona a lista de tropas selecionadas
                        if t not in self.tropas_selecionadas_sp:
                            self.tropas_selecionadas_sp.append(t)
                            self.organiza_tropas_selecionadas()

                if evento.button == 1:  # botão esquerdo | Criar Tropas
                    mouse_pos = pygame.mouse.get_pos()
                    if 685 <= mouse_pos[0] <= 685+30 and 200 <= mouse_pos[1] <= 200+40 and self.verifica_tropas((685+20, 205+50)) == (None, None) and self.num_gold_sp >=20:
                        self.num_gold_sp -=20
                        self.cria_tropa_sp((685+20, 205+50))

                if evento.button == 3:  # botão direito
                    if self.tropas_selecionadas_sp is not None and self.verifica_mina_sp(pos) is not None:
                        for tropa in self.tropas_selecionadas_sp:
                            if isinstance(tropa, Worker):
                                tropa.trabalha(self.verifica_mina_sp(pos))
                                self.tropas_selecionadas_sp.remove(tropa)

            if evento.type == pygame.KEYDOWN and playerId == 0: #playerId=0 (BR) pressiona botao do teclado
                pos = pygame.mouse.get_pos()

                self.organiza_tropas_selecionadas()

                if evento.key == pygame.K_e:  #Apertar "e" limpa lista de tropas selecionadas
                    for tropa in self.tropas_selecionadas_br:
                        tropa.cor = AZUL
                    self.tropas_selecionadas_br.clear()

                if evento.key == pygame.K_r: #Apertar "r" cria trabalhadores
                    if self.verifica_tropas((220, 400+30)) == (None, None) and self.num_gold_br >= 25:
                        self.num_gold_br -= 25
                        self.cria_worker_br((220, 400+30))  # cria uma tropa caso não hajam outras tropas ou florestas no lugar

                if evento.key == pygame.K_w: #W
                    for tropa in self.tropas_selecionadas_br:
                        next = (tropa.pos[0], tropa.pos[1] - num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_s: #S
                    for tropa in reversed(self.tropas_selecionadas_br):
                        next = (tropa.pos[0], tropa.pos[1] + num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_d: #D
                    for tropa in reversed(self.tropas_selecionadas_br):
                        next = (tropa.pos[0] + num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_a: #A
                    for tropa in self.tropas_selecionadas_br:
                        next = (tropa.pos[0] - num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

            if evento.type == pygame.KEYDOWN and playerId == 1: #playerId=1 (SP) pressiona botao do teclado
                pos = pygame.mouse.get_pos()

                self.organiza_tropas_selecionadas()

                if evento.key == pygame.K_e:  #Apertar "e" limpa lista de tropas selecionadas
                    for tropa in self.tropas_selecionadas_sp:
                        tropa.cor = AZUL
                    self.tropas_selecionadas_sp.clear()

                if evento.key == pygame.K_r: #Apertar "r" cria trabalhadores
                    if self.verifica_tropas((580, 200+30)) == (None, None) and self.num_gold_sp >= 20:
                        self.num_gold_sp -= 20
                        self.cria_worker_sp((580, 200+30))  # cria uma tropa caso não hajam outras tropas ou florestas no lugar

                if evento.key == pygame.K_w: #W
                    for tropa in self.tropas_selecionadas_sp:
                        next = (tropa.pos[0], tropa.pos[1] - num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_s: #S
                    for tropa in reversed(self.tropas_selecionadas_sp):
                        next = (tropa.pos[0], tropa.pos[1] + num_linhas)
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_d: #D
                    for tropa in reversed(self.tropas_selecionadas_sp):
                        next = (tropa.pos[0] + num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

                if evento.key == pygame.K_a: #A
                    for tropa in self.tropas_selecionadas_sp:
                        next = (tropa.pos[0] - num_colunas, tropa.pos[1])
                        if self.verifica_floresta(next) is None and self.verifica_tropas(next) == (None, None):
                            tropa.pos = next

        if playerId == 0:
            self.atacar_br()
        else:
            self.atacar_sp()

        self.mata_tropas()

    def verifica_tropa_br(self, pos):  # Verifica se alguma tropa brasileira já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for tropa in self.lista_tropas_br:
            if pos == tropa.pos:
                return tropa
        return None

    def verifica_tropa_sp(self, pos):  # Verifica se alguma tropa paulista já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for tropa in self.lista_tropas_sp:
            if pos == tropa.pos:
                return tropa
        return None

    def verifica_tropas(self, pos): #Retorna uma tupla com os resultados de verifica_tropa_br e verifica_tropa_sp, respectivamente

        br = self.verifica_tropa_br(pos)
        sp = self.verifica_tropa_sp(pos)
        return (br, sp)

    def atacar_br(self): #Deve ser invocado pelo Brasil

        for tropa in self.lista_tropas_br:

            if not isinstance(tropa, Worker):
                if self.screen_coordinates_to_grid(tropa.pos) == (35, 11) or self.screen_coordinates_to_grid(tropa.pos) == (34, 11) or self.screen_coordinates_to_grid(tropa.pos) == (35, 10) or self.screen_coordinates_to_grid(tropa.pos) == (34, 10):
                    self.lista_construcoes_sp[0].vida -= 1

                else:
                    direita = (tropa.pos[0] + num_colunas, tropa.pos[1])
                    esquerda = (tropa.pos[0] - num_colunas, tropa.pos[1])
                    baixo = (tropa.pos[0], tropa.pos[1] + num_linhas)
                    cima = (tropa.pos[0], tropa.pos[1] - num_linhas)

                    tiles_adjacentes = []
                    tiles_adjacentes.clear()

                    tiles_adjacentes.append(self.verifica_tropa_sp(direita))
                    tiles_adjacentes.append(self.verifica_tropa_sp(esquerda))
                    tiles_adjacentes.append(self.verifica_tropa_sp(baixo))
                    tiles_adjacentes.append(self.verifica_tropa_sp(cima))

                    tropas_adjacentes = []
                    tropas_adjacentes.clear()

                    tropas_adjacentes = [i for i in tiles_adjacentes if i != None]

                    if tropas_adjacentes:
                        tropa_atacada = random.choice(tropas_adjacentes)
                        tropa_atacada.vida -= 1

    def atacar_sp(self): #Deve ser invocado por Sao Paulo
        for tropa in self.lista_tropas_sp:
            if not isinstance(tropa, Worker):
                if self.screen_coordinates_to_grid(tropa.pos) == (7, 19) or self.screen_coordinates_to_grid(tropa.pos) == (7, 20) or self.screen_coordinates_to_grid(tropa.pos) == (6, 19) or self.screen_coordinates_to_grid(tropa.pos) == (6, 20):
                    self.lista_construcoes_br[0].vida -= 1

                else:
                    direita = (tropa.pos[0] + num_colunas, tropa.pos[1])
                    esquerda = (tropa.pos[0] - num_colunas, tropa.pos[1])
                    baixo = (tropa.pos[0], tropa.pos[1] + num_linhas)
                    cima = (tropa.pos[0], tropa.pos[1] - num_linhas)

                    tiles_adjacentes = []
                    tiles_adjacentes.clear()

                    tiles_adjacentes.append(self.verifica_tropa_br(direita))
                    tiles_adjacentes.append(self.verifica_tropa_br(esquerda))
                    tiles_adjacentes.append(self.verifica_tropa_br(baixo))
                    tiles_adjacentes.append(self.verifica_tropa_br(cima))

                    tropas_adjacentes = []
                    tropas_adjacentes.clear()

                    tropas_adjacentes = [i for i in tiles_adjacentes if i != None]

                    if tropas_adjacentes:
                        tropa_atacada = random.choice(tropas_adjacentes)
                        tropa_atacada.vida -= 1

    def mata_tropas(self):
        for tropa in self.lista_tropas_br:
            if tropa.vida <= 0:
                self.lista_tropas_br.remove(tropa)
                if tropa in self.tropas_selecionadas_br:
                    self.tropas_selecionadas_br.remove(tropa)

        for tropa in self.lista_tropas_sp:
            if tropa.vida <= 0:
                self.lista_tropas_sp.remove(tropa)
                if tropa in self.tropas_selecionadas_sp:
                    self.tropas_selecionadas_sp.remove(tropa)

    def verifica_floresta(self, pos):  # Verifica se alguma floresta já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for floresta in self.lista_florestas:
            if pos == floresta.pos:
                return floresta
        return None

    def verifica_mina_br(self, pos):  # Verifica se alguma mina brasileira já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for mina in self.lista_minas_br:
            if pos == mina.pos:
                return mina
        return None

    def verifica_mina_sp(self, pos):  # Verifica se alguma mina paulista já está nessa posição
        pos = self.grid_to_screen_coordinates(self.screen_coordinates_to_grid(pos))
        for mina in self.lista_minas_sp:
            if pos == mina.pos:
                return mina
        return None

    def verifica_minas(self, pos): #Retorna uma tupla com os resultados de verifica_mina_br e verifica_mina_sp, respectivamente

        br = self.verifica_mina_br(pos)
        sp = self.verifica_mina_sp(pos)
        return (br, sp)

    def organiza_tropas_selecionadas(self): #Organiza ambas as listas de tropas selecionadas pra facilitar movimento

        self.tropas_selecionadas_br.sort(key = lambda tropa: (tropa.pos[1], tropa.pos[0]))
        self.tropas_selecionadas_sp.sort(key = lambda tropa: (tropa.pos[1], tropa.pos[0]))

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
    def __init__(self, pos, vida):
        self.control = Control()
        self.pos = pos
        self.cor = AZUL
        #self.image = pygame.image.load('8x8.png')
        self.hidden = False
        self.vida = vida

    def __eq__(self, other):
        if not isinstance(other, Tropa):
            return NotImplemented
        return self.pos == other.pos and self.cor == other.cor and self.hidden == other.hidden

    def pinta_tropa_br(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        if self.cor == AZUL:
            image = pygame.image.load('soldadobrNORMAL.png')
        else:
            image = pygame.image.load('soldadobrESCOLHIDO.png')
        image = pygame.transform.scale(image, (20,15))
        tela.blit(image, (grid[0],grid[1]))
        #pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

    def pinta_tropa_sp(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        if self.cor == AZUL:
            image = pygame.image.load('soldadospNORMAL.png')
        else:
            image = pygame.image.load('soldadospESCOLHIDO.png')
        image = pygame.transform.scale(image, (20,15))
        tela.blit(image, (grid[0],grid[1]))
        #pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Worker(Tropa):
    def __init__(self, pos, vida):
        Tropa.__init__(self, pos, vida)
        self.trabalhando = False

    def __eq__(self, other):
        if not isinstance(other, Worker):
            return NotImplemented
        return self.trabalhando == other.trabalhando and self.pos == other.pos #and self.cor == other.cor and self.hidden == other.hidden

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

    def __eq__(self, other):
        if not isinstance(other, Floresta):
            return NotImplemented
        return self.pos == other.pos and self.cor == other.cor

    def pinta_floresta(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Construcao:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = AZUL
        self.vida = 150

    def __eq__(self, other):
        if not isinstance(other, Construcao):
            return NotImplemented
        return self.pos == other.pos and self.cor == other.cor

    def pinta_construcao_br(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        image = pygame.image.load('base-brasil.png')
        image = pygame.transform.scale(image, (40,30))
        tela.blit(image, (grid[0], grid[1]))

    def pinta_construcao_sp(self, tela):
        grid = self.control.screen_coordinates_to_grid(self.pos)
        grid = self.control.grid_to_screen_coordinates(grid)
        image = pygame.image.load('base-sao-paulo.png')
        image = pygame.transform.scale(image, (40,30))
        tela.blit(image, (grid[0], grid[1]))

class Mina:
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = AMARELO_CLARO
        self.estoque = 10000
        self.lista_trabalhadores = []

    def __eq__(self, other):
        if not isinstance(other, Mina):
            return NotImplemented
        return self.pos == other.pos and self.cor == other.cor and self.estoque == other.estoque and self.lista_trabalhadores == other.lista_trabalhadores

    def pinta_mina_br(self, tela):
        #grid = self.control.grid_to_screen_coordinates(self.pos)
        grid = self.pos
        image = pygame.image.load('mina-brasil.png')
        image = pygame.transform.scale(image, (20,20))
        tela.blit(image, (grid[0], grid[1]))

    def pinta_mina_sp(self, tela):
        #grid = self.control.grid_to_screen_coordinates(self.pos)
        grid = self.pos
        image = pygame.image.load('mina-sao-paulo.png')
        image = pygame.transform.scale(image, (20,20))
        tela.blit(image, (grid[0], grid[1]))

    def computa_trabalho(self):
        gold = 0
        for worker in self.lista_trabalhadores:
            self.estoque = self.estoque - 1
            if self.estoque == 0:
                del self
            gold = gold+1
        return gold
