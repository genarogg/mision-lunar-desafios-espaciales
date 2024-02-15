import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Platformer')

# Definir variables del juego
tamaño_tile = 50
fin_juego = 0

# Cargar imágenes
sol_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')


class Boton():
    def __init__(self, x, y, imagen):
        self.imagen = imagen
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clickeado = False

    def dibujar(self):
        accion = False

        # Obtener posición del ratón
        pos = pygame.mouse.get_pos()

        # Comprobar condiciones de ratón sobre y clickeado
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clickeado:
                accion = True
                self.clickeado = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clickeado = False

        # Dibujar botón
        pantalla.blit(self.imagen, self.rect)

        return accion


class Jugador():
    def __init__(self, x, y):
        self.resetear(x, y)

    def actualizar(self, fin_juego):
        dx = 0
        dy = 0
        cooldown_andar = 5

        if fin_juego == 0:
            # Obtener teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
            if not tecla[pygame.K_SPACE]:
                self.jumped = False
            if tecla[pygame.K_LEFT]:
                dx -= 5
                self.contador += 1
                self.direccion = -1
            if tecla[pygame.K_RIGHT]:
                dx += 5
                self.contador += 1
                self.direccion = 1
            if not tecla[pygame.K_LEFT] and not tecla[pygame.K_RIGHT]:
                self.contador = 0
                self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            # Manejar animación
            if self.contador > cooldown_andar:
                self.contador = 0
                self.indice += 1
                if self.indice >= len(self.imagenes_derecha):
                    self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            # Agregar gravedad
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Comprobar colisión
            self.in_air = True
            for tile in mundo.lista_tiles:
                # Comprobar colisión en dirección x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Comprobar colisión en dirección y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Comprobar si está debajo del suelo, es decir, saltando
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Comprobar si está encima del suelo, es decir, cayendo
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Comprobar colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blobs, False):
                fin_juego = -1

            # Comprobar colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_juego = -1

            # Actualizar coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_juego == -1:
            self.imagen = self.imagen_muerto
            if self.rect.y > 200:
                self.rect.y -= 5

        # Dibujar jugador en pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)

        return fin_juego

    def resetear(self, x, y):
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
        self.imagen_muerto = pygame.image.load('img/ghost.png')
        self.imagen = self.imagenes_derecha[self.indice]
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ancho = self.imagen.get_width()
        self.alto = self.imagen.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direccion = 0
        self.in_air = True

class Mundo():
    def __init__(self, datos):
        self.lista_tiles = []

        # Cargar imágenes
        img_tierra = pygame.image.load('img/dirt.png')
        img_pasto = pygame.image.load('img/grass.png')

        fila_contador = 0
        for fila in datos:
            col_contador = 0
            for tile in fila:
                if tile == 1:
                    img = pygame.transform.scale(img_tierra, (tamaño_tile, tamaño_tile))
                    img_rect = img.get_rect()
                    img_rect.x = col_contador * tamaño_tile
                    img_rect.y = fila_contador * tamaño_tile
                    tile = (img, img_rect)
                    self.lista_tiles.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(img_pasto, (tamaño_tile, tamaño_tile))
                    img_rect = img.get_rect()
                    img_rect.x = col_contador * tamaño_tile
                    img_rect.y = fila_contador * tamaño_tile
                    tile = (img, img_rect)
                    self.lista_tiles.append(tile)
                if tile == 3:
                    blob = Enemigo(col_contador * tamaño_tile, fila_contador * tamaño_tile + 15)
                    grupo_blobs.add(blob)
                if tile == 6:
                    lava = Lava(col_contador * tamaño_tile, fila_contador * tamaño_tile + (tamaño_tile // 2))
                    grupo_lava.add(lava)

                col_contador += 1
            fila_contador += 1

    def dibujar(self):
        for tile in self.lista_tiles:
            pantalla.blit(tile[0], tile[1])
            pygame.draw.rect(pantalla, (255, 255, 255), tile[1], 2)


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
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


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tamaño_tile, tamaño_tile // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


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

grupo_blobs = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()

mundo = Mundo(datos_mundo)

# Crear botones
boton_reinicio = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, restart_img)

corriendo = True
while corriendo:

    reloj.tick(fps)

    pantalla.blit(bg_img, (0, 0))
    pantalla.blit(sol_img, (100, 100))

    mundo.dibujar()

    if fin_juego == 0:
        grupo_blobs.update()

    grupo_blobs.draw(pantalla)
    grupo_lava.draw(pantalla)

    fin_juego = jugador.actualizar(fin_juego)

    # Si el jugador ha muerto
    if fin_juego == -1:
        if boton_reinicio.dibujar():
            jugador.resetear(100, alto_pantalla - 130)
            fin_juego = 0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    pygame.display.update()

pygame.quit()