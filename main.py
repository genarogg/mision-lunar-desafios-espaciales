import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')

#definir variables del juego
tamaño_casilla = 50

#cargar imágenes
imagen_sol = pygame.image.load('img/sun.png')
imagen_fondo = pygame.image.load('img/sky.png')


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
        self.ancho = self.imagen.get_width()
        self.alto = self.imagen.get_height()
        self.vel_y = 0
        self.saltado = False
        self.direccion = 0

    def actualizar(self):
        dx = 0
        dy = 0
        enfriamiento_caminar = 5

        #obtener teclas presionadas
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


        #manejar animación
        if self.contador > enfriamiento_caminar:
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

        #verificar colisión
        for casilla in mundo.lista_casillas:
            #verificar colisión en dirección x
            if casilla[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                dx = 0
            #verificar colisión en dirección y
            if casilla[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                #verificar si está debajo del suelo, es decir, saltando
                if self.vel_y < 0:
                    dy = casilla[1].bottom - self.rect.top
                    self.vel_y = 0
                #verificar si está sobre el suelo, es decir, cayendo
                elif self.vel_y >= 0:
                    dy = casilla[1].top - self.rect.bottom
                    self.vel_y = 0




        #actualizar coordenadas del jugador
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > alto_pantalla:
            self.rect.bottom = alto_pantalla
            dy = 0

        #dibujar jugador en pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)
class Mundo():
    def __init__(self, datos):
        self.lista_casillas = []

        #cargar imágenes
        img_suciedad = pygame.image.load('img/dirt.png')
        img_hierba = pygame.image.load('img/grass.png')

        contador_filas = 0
        for fila in datos:
            contador_columnas = 0
            for casilla in fila:
                if casilla == 1:
                    img = pygame.transform.scale(img_suciedad, (tamaño_casilla, tamaño_casilla))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_casilla
                    rect_img.y = contador_filas * tamaño_casilla
                    casilla = (img, rect_img)
                    self.lista_casillas.append(casilla)
                if casilla == 2:
                    img = pygame.transform.scale(img_hierba, (tamaño_casilla, tamaño_casilla))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_casilla
                    rect_img.y = contador_filas * tamaño_casilla
                    casilla = (img, rect_img)
                    self.lista_casillas.append(casilla)
                contador_columnas += 1
            contador_filas += 1

    def dibujar(self):
        for casilla in self.lista_casillas:
            pantalla.blit(casilla[0], casilla[1])
            pygame.draw.rect(pantalla, (255, 255, 255), casilla[1], 2)


jugador = Jugador(100, altura_pantalla - 130)
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