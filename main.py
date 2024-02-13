import pygame
from pygame.locals import *

pygame.init()

# Definir el ancho y la altura de la pantalla
ancho_pantalla = 1000
altura_pantalla = 1000

# Crear la pantalla del juego
pantalla = pygame.display.set_mode((ancho_pantalla, altura_pantalla))
pygame.display.set_caption('Juego de Plataformas')

# Definir variables del juego
tamaño_bloque = 50

# Cargar imágenes
imagen_sol = pygame.image.load('img/sun.png')
imagen_fondo = pygame.image.load('img/sky.png')

# Función para dibujar una cuadrícula en la pantalla
def dibujar_cuadricula():
    for linea in range(0, 20):
        pygame.draw.line(pantalla, (255, 255, 255), (0, linea * tamaño_bloque), (ancho_pantalla, linea * tamaño_bloque))
        pygame.draw.line(pantalla, (255, 255, 255), (linea * tamaño_bloque, 0), (linea * tamaño_bloque, altura_pantalla))

# Clase para el mundo del juego
class Mundo():
    def __init__(self, datos):
        self.lista_bloques = []

        # Cargar imágenes
        imagen_tierra = pygame.image.load('img/dirt.png')
        imagen_hierba = pygame.image.load('img/grass.png')

        # Crear los bloques del mundo basándose en los datos proporcionados
        numero_fila = 0
        for fila in datos:
            numero_columna = 0
            for bloque in fila:
                if bloque == 1:
                    img = pygame.transform.scale(imagen_tierra, (tamaño_bloque, tamaño_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = numero_columna * tamaño_bloque
                    rect_img.y = numero_fila * tamaño_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                if bloque == 2:
                    img = pygame.transform.scale(imagen_hierba, (tamaño_bloque, tamaño_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = numero_columna * tamaño_bloque
                    rect_img.y = numero_fila * tamaño_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                numero_columna += 1
            numero_fila += 1

    # Función para dibujar el mundo en la pantalla
    def dibujar(self):
        for bloque in self.lista_bloques:
            pantalla.blit(bloque[0], bloque[1])

# Datos del mundo del juego
datos_mundo = [
# Aquí van los datos del mundo
]

# Crear el mundo del juego
mundo = Mundo(datos_mundo)

# Bucle principal del juego
ejecutando = True
while ejecutando:

    # Dibujar el fondo y el sol
    pantalla.blit(imagen_fondo, (0, 0))
    pantalla.blit(imagen_sol, (100, 100))

    # Dibujar el mundo
    mundo.dibujar()

    # Dibujar la cuadrícula
    dibujar_cuadricula()

    # Procesar eventos del juego
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Actualizar la pantalla del juego
    pygame.display.update()

# Salir de Pygame
pygame.quit()