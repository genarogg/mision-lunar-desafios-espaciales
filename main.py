import pygame
from pygame.locals import *

pygame.init()

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')

#definir variables del juego
tamaño_casilla = 50

#cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')

class Jugador():
    def __init__(self, x, y):
        img = pygame.image.load('img/guy1.png')
        self.imagen = pygame.transform.scale(img, (40, 80))
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.saltado = False

    def actualizar(self):
        dx = 0
        dy = 0

        #obtener teclas presionadas
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_SPACE] and self.saltado == False:
            self.vel_y = -15
            self.saltado = True
        if tecla[pygame.K_SPACE] == False:
            self.saltado = False
        if tecla[pygame.K_LEFT]:
            dx -= 5
        if tecla[pygame.K_RIGHT]:
            dx += 5

        #añadir gravedad
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #verificar colisión

        #actualizar coordenadas del jugador
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > alto_pantalla:
            self.rect.bottom = alto_pantalla
            dy = 0

        #dibujar jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)

class Mundo():
    def __init__(self, datos):
        self.lista_de_baldosas = []

        #cargar imágenes
        img_tierra = pygame.image.load('img/dirt.png')
        img_cesped = pygame.image.load('img/grass.png')

        contador_filas = 0
        for fila in datos:
            contador_columnas = 0
            for baldosa in fila:
                if baldosa == 1:
                    img = pygame.transform.scale(img_tierra, (tamaño_casilla, tamaño_casilla))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_casilla
                    rect_img.y = contador_filas * tamaño_casilla
                    baldosa = (img, rect_img)
                    self.lista_de_baldosas.append(baldosa)
                if baldosa == 2:
                    img = pygame.transform.scale(img_cesped, (tamaño_casilla, tamaño_casilla))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_casilla
                    rect_img.y = contador_filas * tamaño_casilla
                    baldosa = (img, rect_img)
                    self.lista_de_baldosas.append(baldosa)
                contador_columnas += 1
            contador_filas += 1

    def dibujar(self):
        for baldosa in self.lista_de_baldosas:
            pantalla.blit(baldosa[0], baldosa[1])

#... datos del mundo ...
datos_mundo = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

jugador = Jugador(100, alto_pantalla - 130)
mundo = Mundo(datos_mundo)

ejecutar = True
while ejecutar:

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    mundo.dibujar()

    jugador.actualizar()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutar = False

    pygame.display.update()

pygame.quit()