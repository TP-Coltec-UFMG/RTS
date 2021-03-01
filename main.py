#Imports
from noise import pnoise2
import numpy as np
import pygame
from network import Network
pygame.init()
import classes
import pickle
import copy
import time

#Constantes
HEIGHT = 800
WIDTH = 600
BRANCO = (255, 255, 255)
AMARELO = (255, 255, 0)
AMARELO_CLARO = (200, 200, 100)
PRETO = (84, 84, 84)
AZUL = (0, 43, 255)
VERDE = (214, 255, 199)

RAZAO = (30, 40) #30 rows, 40 columns
#Razão a partir da qual são construidos todos os elementos do jogo (cada pixel é um retangulo de 30 por 40, ou qualquer que sejam os dois números ali em cima)

num_colunas = WIDTH // RAZAO[0]
num_linhas = HEIGHT // RAZAO[1]

#Inicialização

pygame.display.set_caption("minimal program")
SCREEN = pygame.display.set_mode((HEIGHT, WIDTH), 0)
SCREEN.blit(SCREEN, (0, 0))
FONTE = pygame.font.SysFont('Comic Sans MS', 40)

def main():

    RUN = True

    #Multiplayer bullshit
    n = Network() #This class's purpose is to connect the client to the especified server

    clock = pygame.time.Clock()

    playerControls = []
    playerControls = n.getPlayerControl()

    control = playerControls[0]
    playerId = playerControls[1]

    data = []#Data that will be sent to the server and back

    print("playerId from client: ", playerId)

    control.pinta_mapa(control.gera_mapa(seed=9))

    BASE1POS = (120, 390)
    base1 = classes.Construcao(BASE1POS)
    control.lista_construcoes_br.append(base1)

    BASE2POS = (680, 210)
    base2 = classes.Construcao(BASE2POS)
    control.lista_construcoes_sp.append(base2)

    MINA1POS = (220, 400)
    mina1 = classes.Mina(MINA1POS)
    worker1 = classes.Worker(MINA1POS, 25)
    mina1.lista_trabalhadores.append(worker1)
    control.lista_minas_br.append(mina1)

    MINA2POS = (580, 200)
    mina2 = classes.Mina(MINA2POS)
    worker2 = classes.Worker(MINA2POS, 25)
    mina2.lista_trabalhadores.append(worker2)
    control.lista_minas_sp.append(mina2)

    end = None

    while RUN:
        clock.tick(60)

        EVENTS = pygame.event.get()
        for event in EVENTS:
            if event.type == pygame.QUIT:
                RUN = False

        controlCopia = copy.deepcopy(control)

        end = control.processar_eventos(EVENTS, playerId)

        control.pinta_tela(SCREEN)

        data.clear()
        data = [copy.deepcopy(control), copy.deepcopy(controlCopia)]

        try:
            data = n.send(data)

            if data[1]:
                control = data[0]
        except:
            break

        if end == 1:
            RUN = False
        if end == 0:
            RUN = False

    if end == 0:
        texto_game_over = FONTE.render("As Tropas Estaduais Vencem!", True, BRANCO)
    elif end == 1:
        texto_game_over = FONTE.render("Os Revolucionários Vencem!", True, BRANCO)
    else:
        texto_game_over = FONTE.render("Game Over! Você Perdeu..", True, BRANCO)

    SCREEN.blit(texto_game_over, (100, 200))
    pygame.display.update()
    time.sleep(10)

    pygame.quit()

if __name__ == "__main__":
    main()
