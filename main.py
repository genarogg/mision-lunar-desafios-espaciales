import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformero')

# definir variables del juego
tamaño_bloque = 50
fin_del_juego = 0
menu_principal = True

# cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')
img_reinicio = pygame.image.load('img/restart_btn.png')
img_inicio = pygame.image.load('img/start_btn.png')
img_salida = pygame.image.load('img/exit_btn.png')


class Boton():
    def __init__(self, x, y, imagen):
        self.imagen = imagen
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clickeado = False

    def dibujar(self):
        accion = False

        # obtener posición del mouse
        pos = pygame.mouse.get_pos()

        # verificar condiciones de paso del mouse y clic
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clickeado == False:
                accion = True
                self.clickeado = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clickeado = False

        # dibujar botón
        pantalla.blit(self.imagen, self.rect)

        return accion


class Jugador():
    def __init__(self, x, y):
        self.resetear(x, y)

    def actualizar(self, fin_del_juego):
        dx = 0
        dy = 0
        enfriamiento_caminar = 5

        if fin_del_juego == 0:
            # obtener teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and self.saltado == False and self.en_aire == False:
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

            # manejar animación
            if self.contador > enfriamiento_caminar:
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

            # verificar colisiones
            self.en_aire = True
            for bloque in mundo.lista_bloques:
                # verificar colisión en dirección x
                if bloque[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # verificar colisión en dirección y
                if bloque[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # verificar si está debajo del suelo, es decir, saltando
                    if self.vel_y < 0:
                        dy = bloque[1].bottom - self.rect.top
                        self.vel_y = 0
                    # verificar si está encima del suelo, es decir, cayendo
                    elif self.vel_y >= 0:
                        dy = bloque[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.en_aire = False

            # verificar colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blob, False):
                fin_del_juego = -1

            # verificar colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_del_juego = -1

            # actualizar coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_del_juego == -1:
            self.imagen = self.imagen_muerto
            if self.rect.y > 200:
                self.rect.y -= 5

        # dibujar jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)

        return fin_del_juego

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
        self.saltado = False
        self.direccion = 0
        self.en_aire = True

class Mundo():
    def __init__(self, datos):
        self.lista_bloques = []

        # cargar imágenes
        img_tierra = pygame.image.load('img/tierra.png')
        img_pasto = pygame.image.load('img/pasto.png')

        fila_cont = 0
        for fila in datos:
            col_cont = 0
            for bloque in fila:
                if bloque == 1:
                    img = pygame.transform.scale(img_tierra, (tamaño_bloque, tamaño_bloque))
                    img_rect = img.get_rect()
                    img_rect.x = col_cont * tamaño_bloque
                    img_rect.y = fila_cont * tamaño_bloque
                    bloque = (img, img_rect)
                    self.lista_bloques.append(bloque)
                if bloque == 2:
                    img = pygame.transform.scale(img_pasto, (tamaño_bloque, tamaño_bloque))
                    img_rect = img.get_rect()
                    img_rect.x = col_cont * tamaño_bloque
                    img_rect.y = fila_cont * tamaño_bloque
                    bloque = (img, img_rect)
                    self.lista_bloques.append(bloque)
                if bloque == 3:
                    enemigo = Enemigo(col_cont * tamaño_bloque, fila_cont * tamaño_bloque + 15)
                    grupo_blob.add(enemigo)
                if bloque == 6:
                    lava = Lava(col_cont * tamaño_bloque, fila_cont * tamaño_bloque + (tamaño_bloque // 2))
                    grupo_lava.add(lava)

                col_cont += 1
            fila_cont += 1

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

    def actualizar(self):
        self.rect.x += self.direccion_movimiento
        self.contador_movimiento += 1
        if abs(self.contador_movimiento) > 50:
            self.direccion_movimiento *= -1
            self.contador_movimiento *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.imagen = pygame.transform.scale(img, (tamaño_bloque, tamaño_bloque // 2))
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y


datos_mundo = [
]

jugador = Jugador(100, alto_pantalla - 130)

grupo_blob = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()

mundo = Mundo(datos_mundo)

# crear botones
boton_reinicio = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, img_reinicio)
boton_inicio = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, img_inicio)
boton_salida = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, img_salida)

ejecutar = True
while ejecutar:

    reloj.tick(fps)

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    if menu_principal == True:
        if boton_salida.dibujar():
            ejecutar = False
        if boton_inicio.dibujar():
            menu_principal = False
    else:
        mundo.dibujar()

        if fin_del_juego == 0:
            grupo_blob.update()

        grupo_blob.draw(pantalla)
        grupo_lava.draw(pantalla)

        fin_del_juego = jugador.actualizar(fin_del_juego)

        # si el jugador ha muerto
        if fin_del_juego == -1:
            if boton_reinicio.dibujar():
                jugador.resetear(100, alto_pantalla - 130)
                fin_del_juego = 0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutar = False

    pygame.display.update()

pygame.quit()
