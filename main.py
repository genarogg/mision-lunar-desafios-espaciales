import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')

#define las variables del juego
tamaño_baldosa = 50

#carga las imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')


class Jugador():
    def __init__(self, x, y):
        self.imagenes_derecha = []
        self.imagenes_izquierda = []
        self.indice = 0
        self.contador = 0
        for num in range(1, 5):
            img_derecha = pygame.image.load(f'img/guy{num}.png')
            img_derecha = pygame.transform.scale(img_derecha, (40, 80))
            img_izquierda = pygame.transform.flip(img_derecha, True, False)
            self.imagenes_derecha.append(img_derecha)
            self.imagenes_izquierda.append(img_izquierda)
        self.imagen = self.imagenes_derecha[self.indice]
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.saltado = False
        self.direccion = 0

    def actualizar(self):
        dx = 0
        dy = 0
        tiempo_animacion = 5

        #obtener las teclas presionadas
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_SPACE] and self.saltado == False:
            self.vel_y = -15
            self.saltado = True
        if tecla[pygame.K_SPACE] == False:
            self.saltado = False
        if tecla[pygame.K_LEFT]:
            dx -= 5
            self.contador += 1
            self.direccion = -1
        if tecla[pygame.K_RIGHT]:
            dx += 5
            self.contador += 1
            self.direccion = 1
        if tecla[pygame.K_LEFT] == False and tecla[pygame.K_RIGHT] == False:
            self.contador = 0
            self.indice = 0
            if self.direccion == 1:
                self.imagen = self.imagenes_derecha[self.indice]
            if self.direccion == -1:
                self.imagen = self.imagenes_izquierda[self.indice]

        #manejar la animación
        if self.contador > tiempo_animacion:
            self.contador = 0	
            self.indice += 1
            if self.indice >= len(self.imagenes_derecha):
                self.indice = 0
            if self.direccion == 1:
                self.imagen = self.imagenes_derecha[self.indice]
            if self.direccion == -1:
                self.imagen = self.imagenes_izquierda[self.indice]

        #añadir gravedad
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        #verificar colisiones

        #actualizar las coordenadas del jugador
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > alto_pantalla:
            self.rect.bottom = alto_pantalla
            dy = 0

        #dibujar al jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)


class Mundo():
    def __init__(self, datos):
        self.lista_baldosas = []

        #cargar imágenes
        img_tierra = pygame.image.load('img/dirt.png')
        img_cesped = pygame.image.load('img/grass.png')

        contador_filas = 0
        for fila in datos:
            contador_columnas = 0
            for baldosa in fila:
                if baldosa == 1:
                    img = pygame.transform.scale(img_tierra, (tamaño_baldosa, tamaño_baldosa))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_baldosa
                    rect_img.y = contador_filas * tamaño_baldosa
                    baldosa = (img, rect_img)
                    self.lista_baldosas.append(baldosa)
                if baldosa == 2:
                    img = pygame.transform.scale(img_cesped, (tamaño_baldosa, tamaño_baldosa))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_baldosa
                    rect_img.y = contador_filas * tamaño_baldosa
                    baldosa = (img, rect_img)
                    self.lista_baldosas.append(baldosa)
                contador_columnas += 1
            contador_filas += 1

    def dibujar(self):
        for baldosa in self.lista_baldosas:
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

    reloj.tick(fps)

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    mundo.dibujar()

    jugador.actualizar()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutar = False

    pygame.display.update()

pygame.quit()