import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')

# definir variables del juego
tamaño_bloque = 50


# cargar imágenes
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
        self.ancho = self.imagen.get_width()
        self.alto = self.imagen.get_height()
        self.vel_y = 0
        self.salto = False
        self.direccion = 0

    def update(self):
        dx = 0
        dy = 0
        tiempo_entre_pasos = 5

        # obtener pulsaciones de teclas
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE] and self.salto == False:
            self.vel_y = -15
            self.salto = True
        if teclas[pygame.K_SPACE] == False:
            self.salto = False
        if teclas[pygame.K_LEFT]:
            dx -= 5
            self.contador += 1
            self.direccion = -1
        if teclas[pygame.K_RIGHT]:
            dx += 5
            self.contador += 1
            self.direccion = 1
        if teclas[pygame.K_LEFT] == False and teclas[pygame.K_RIGHT] == False:
            self.contador = 0
            self.indice = 0
            if self.direccion == 1:
                self.imagen = self.imagenes_derecha[self.indice]
            if self.direccion == -1:
                self.imagen = self.imagenes_izquierda[self.indice]

        # manejar la animación
        if self.contador > tiempo_entre_pasos:
            self.contador = 0
            self.indice += 1
            if self.indice >= len(self.imagenes_derecha):
                self.indice = 0
            if self.direccion == 1:
                self.imagen = self.imagenes_derecha[self.indice]
            if self.direccion == -1:
                self.imagen = self.imagenes_izquierda[self.indice]

        # agregar gravedad
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # comprobar colisión
        for bloque in mundo.lista_bloques:
            # comprobar colisión en dirección x
            if bloque[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                dx = 0
            # comprobar colisión en dirección y
            if bloque[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                # comprobar si está debajo del suelo, es decir, saltando
                if self.vel_y < 0:
                    dy = bloque[1].bottom - self.rect.top
                    self.vel_y = 0
                # comprobar si está sobre el suelo, es decir, cayendo
                elif self.vel_y >= 0:
                    dy = bloque[1].top - self.rect.bottom
                    self.vel_y = 0

        # actualizar coordenadas del jugador
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > alto_pantalla:
            self.rect.bottom = alto_pantalla
            dy = 0

        # dibujar jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)


class Mundo():
    def __init__(self, data):
        self.lista_bloques = []

        # cargar imágenes
        img_suelo = pygame.image.load('img/dirt.png')
        img_hierba = pygame.image.load('img/grass.png')

        contador_fila = 0
        for fila in data:
            contador_columna = 0
            for bloque in fila:
                if bloque == 1:
                    img = pygame.transform.scale(img_suelo, (tamaño_bloque, tamaño_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columna * tamaño_bloque
                    rect_img.y = contador_fila * tamaño_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                if bloque == 2:
                    img = pygame.transform.scale(img_hierba, (tamaño_bloque, tamaño_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columna * tamaño_bloque
                    rect_img.y = contador_fila * tamaño_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                if bloque == 3:
                    enemigo = Enemigo(contador_columna * tamaño_bloque, contador_fila * tamaño_bloque + 15)
                    grupo_enemigos.add(enemigo)
                contador_columna += 1
            contador_fila += 1

    def dibujar(self):
        for bloque in self.lista_bloques:
            pantalla.blit(bloque[0], bloque[1])
            pygame.draw.rect(pantalla, (255, 255, 255), bloque[1], 2)


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.imagen = pygame.image.load('img/blob.png')
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direccion_movimiento = 1
        self.contador_movimiento = 0

    def update(self):
        self.rect.x += self.direccion_movimiento
        self.contador_movimiento += 1
        if abs(self.contador_movimiento) > 50:
            self.direccion_movimiento *= -1
            self.contador_movimiento *= -1


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

grupo_enemigos = pygame.sprite.Group()

mundo = Mundo(datos_mundo)

corriendo = True
while corriendo:

    reloj.tick(fps)

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    mundo.dibujar()

    grupo_enemigos.update()
    grupo_enemigos.draw(pantalla)

    jugador.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            corriendo = False

    pygame.display.update()

pygame.quit()
