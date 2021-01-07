from noise import pnoise2
import numpy as np
import pygame

pygame.init()
pygame.display.set_caption("minimal program")

screen_altura = 800
screen_largura = 600

screen = pygame.display.set_mode((screen_altura, screen_largura), 0)

amarelo = (255, 255, 0)
preto = (0, 0, 0)
azul = (0, 43, 255)
verde = (0, 146, 10)

razao_unidade_tela = (30, 40)

num_colunas = screen_largura // razao_unidade_tela[0]
num_linhas = screen_altura // razao_unidade_tela[1]

class Control():
    def __init__(self):
        self.lista_tropas = [] #uma lista com todas as tropas
        self.tropas_selecionadas = [] #uma lista com todas as tropas selecionadas
        self.lista_florestas = []#uma lista com as florestas

    def mouse_position_to_grid(self, pos):
        tuple = (pos[0]//num_linhas, pos[1]//num_colunas)
        return tuple

    def grid_to_mouse_position(self, grid):
        tuple = (grid[0]*num_linhas, grid[1]*num_colunas)
        return tuple

    def cria_tropa(self, pos): # cria uma tropa dada uma posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        tropa = Tropa(pos)
        self.lista_tropas.append(tropa)

    def pinta_tropas(self): #itera através da lista de tropas e pinta
        for tropa in self.lista_tropas:
            tropa.pinta_tropa(screen)

    def pinta_florestas(self):  # itera através da lista de florestas e pinta
        for floresta in self.lista_florestas:
            floresta.pinta_floresta(screen)

    def processar_eventos(self, eventos):
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if evento.button == 1: #botão esquerdo
                    if self.verifica_tropa(pos) == None:
                        self.cria_tropa(pos) #cria uma tropa caso não hajam outras tropas no lugar
                elif evento.button == 3: #botão direito
                    if self.verifica_tropa(pos) != None:
                        t = self.verifica_tropa(pos)
                        t.cor = amarelo #seleciona uma tropa caso uma já exista no lugar, a pinta de amarelo e a adiciona a lista de tropas selecionadas
                        if t not in self.tropas_selecionadas:
                            self.tropas_selecionadas.append(t)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e: #limpa lista de tropas selecionadas
                    for tropa in self.tropas_selecionadas:
                        tropa.cor = azul
                    self.tropas_selecionadas.clear

    def verifica_tropa(self, pos): #Verifica se alguma tropa já está nessa posição
        pos = self.grid_to_mouse_position(self.mouse_position_to_grid(pos))
        for tropa in self.lista_tropas:
            if pos == tropa.pos:
                return tropa
        return None

    def gera_mapa(self, shape=(razao_unidade_tela[1], razao_unidade_tela[0]), #gera um array de ruido 2d
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

    def pinta_mapa(self, tela, array):
        for x in range(razao_unidade_tela[1]):
            for y in range(razao_unidade_tela[0]):
                if array[x][y] > 0.4:
                    pos = (x * num_linhas, y*num_colunas)
                    floresta = Floresta(pos)
                    self.lista_florestas.append(floresta)


class Tropa():
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = azul
    def pinta_tropa(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (grid[0], grid[1], num_colunas, num_linhas), 0)

class Floresta():
    def __init__(self, pos):
        self.control = Control()
        self.pos = pos
        self.cor = verde

    def pinta_floresta(self, tela):
        grid = control.mouse_position_to_grid(self.pos)
        grid = control.grid_to_mouse_position(grid)
        pygame.draw.rect(tela, self.cor, (self.pos[0], self.pos[1], num_colunas, num_linhas), 0)

if __name__=="__main__":

    control = Control()
    control.pinta_mapa(screen, control.gera_mapa(seed=20))

    while True:
        #screen.fill(preto)
        control.pinta_tropas()
        control.pinta_florestas()
        pygame.display.update()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit(2)

        control.processar_eventos(events)