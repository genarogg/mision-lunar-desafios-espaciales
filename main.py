import pygame
from pygame.locals import *
import pickle
from os import path

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformero')

# Definir fuente
fuente = pygame.font.SysFont('Bauhaus 93', 70)
fuente_puntuacion = pygame.font.SysFont('Bauhaus 93', 30)

# Definir variables del juego
tamanio_casilla = 50
fin_del_juego = 0
menu_principal = True
nivel = 0
max_niveles = 7
puntuacion = 0

# Definir colores
blanco = (255, 255, 255)
azul = (0, 0, 255)

# Cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')
img_reinicio = pygame.image.load('img/restart_btn.png')
img_inicio = pygame.image.load('img/start_btn.png')
img_salida = pygame.image.load('img/exit_btn.png')

def dibujar_texto(texto, fuente, color_texto, x, y):
    img = fuente.render(texto, True, color_texto)
    pantalla.blit(img, (x, y))

def reiniciar_nivel(nivel):
    jugador.reiniciar(100, alto_pantalla - 130)
    grupo_enemigos.empty()
    grupo_lava.empty()
    grupo_salida.empty()

    if path.exists(f'level{nivel}_data'):
        pickle_in = open(f'level{nivel}_data', 'rb')
        datos_mundo = pickle.load(pickle_in)
    mundo = Mundo(datos_mundo)

    return mundo

class Boton():
    def __init__(self, x, y, imagen):
        self.imagen = imagen
        self.rect = self.imagen.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clickeado = False

    def dibujar(self):
        accion = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clickeado:
                accion = True
                self.clickeado = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clickeado = False

        pantalla.blit(self.imagen, self.rect)

        return accion

class Jugador():
    def __init__(self, x, y):
        self.reiniciar(x, y)

    def actualizar(self, fin_del_juego):
        dx = 0
        dy = 0
        tiempo_entre_pasos = 5

        if fin_del_juego == 0:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_SPACE] and not self.saltando and not self.en_aire:
                self.vel_y = -15
                self.saltando = True
            if not teclas[pygame.K_SPACE]:
                self.saltando = False
            if teclas[pygame.K_LEFT]:
                dx -= 5
                self.contador += 1
                self.direccion = -1
            if teclas[pygame.K_RIGHT]:
                dx += 5
                self.contador += 1
                self.direccion = 1
            if not teclas[pygame.K_LEFT] and not teclas[pygame.K_RIGHT]:
                self.contador = 0
                self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            if self.contador > tiempo_entre_pasos:
                self.contador = 0
                self.indice += 1
                if self.indice >= len(self.imagenes_derecha):
                    self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.en_aire = True
            for casilla in mundo.lista_casillas:
                if casilla[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                if casilla[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    if self.vel_y < 0:
                        dy = casilla[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = casilla[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.en_aire = False

            if pygame.sprite.spritecollide(self, grupo_enemigos, False):
                fin_del_juego = -1

            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_del_juego = -1

            if pygame.sprite.spritecollide(self, grupo_salida, False):
                fin_del_juego = 1

            self.rect.x += dx
            self.rect.y += dy

        elif fin_del_juego == -1:
            self.imagen = self.imagen_muerto
            dibujar_texto('¡GAME OVER!', fuente, azul, (ancho_pantalla // 2) - 200, alto_pantalla // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)

        return fin_del_juego

    def reiniciar(self, x, y):
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
        self.saltando = False
        self.direccion = 0
        self.en_aire = True

class Mundo():
    def __init__(self, datos):
        self.lista_casillas = []
        img_tierra = pygame.image.load('img/dirt.png')
        img_pasto = pygame.image.load('img/grass.png')
        fila_actual = 0
        for fila in datos:
            columna_actual = 0
            for casilla in fila:
                if casilla == 1:
                    img = pygame.transform.scale(img_tierra, (tamanio_casilla, tamanio_casilla))
                    rect = img.get_rect()
                    rect.x = columna_actual * tamanio_casilla
                    rect.y = fila_actual * tamanio_casilla
                    casilla = (img, rect)
                    self.lista_casillas.append(casilla)
                if casilla == 2:
                    img = pygame.transform.scale(img_pasto, (tamanio_casilla, tamanio_casilla))
                    rect = img.get_rect()
                    rect.x = columna_actual * tamanio_casilla
                    rect.y = fila_actual * tamanio_casilla
                    casilla = (img, rect)
                    self.lista_casillas.append(casilla)
                if casilla == 3:
                    enemigo = Enemigo(columna_actual * tamanio_casilla, fila_actual * tamanio_casilla + 15)
                    grupo_enemigos.add(enemigo)
                if casilla == 6:
                    lava = Lava(columna_actual * tamanio_casilla, fila_actual * tamanio_casilla + (tamanio_casilla // 2))
                    grupo_lava.add(lava)
                if casilla == 7:
                    moneda = Moneda(columna_actual * tamanio_casilla + (tamanio_casilla // 2), fila_actual * tamanio_casilla + (tamanio_casilla // 2))
                    grupo_monedas.add(moneda)
                if casilla == 8:
                    salida = Salida(columna_actual * tamanio_casilla, fila_actual * tamanio_casilla - (tamanio_casilla // 2))
                    grupo_salida.add(salida)
                columna_actual += 1
            fila_actual += 1

    def dibujar(self):
        for casilla in self.lista_casillas:
            pantalla.blit(casilla[0], casilla[1])
            pygame.draw.rect(pantalla, (255, 255, 255), casilla[1], 2)

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

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tamanio_casilla, tamanio_casilla // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tamanio_casilla // 2, tamanio_casilla // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Salida(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tamanio_casilla, int(tamanio_casilla * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

jugador = Jugador(100, alto_pantalla - 130)

grupo_enemigos = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()
grupo_monedas = pygame.sprite.Group()
grupo_salida = pygame.sprite.Group()

moneda_puntuacion = Moneda(tamanio_casilla // 2, tamanio_casilla // 2)
grupo_monedas.add(moneda_puntuacion)

if path.exists(f'level{nivel}_data'):
    pickle_in = open(f'level{nivel}_data', 'rb')
    datos_mundo = pickle.load(pickle_in)
mundo = Mundo(datos_mundo)

boton_reinicio = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, img_reinicio)
boton_inicio = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, img_inicio)
boton_salida = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, img_salida)

correr = True
while correr:

    reloj.tick(fps)

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    if menu_principal:
        if boton_salida.dibujar():
            correr = False
        if boton_inicio.dibujar():
            menu_principal = False
    else:
        mundo.dibujar()

        if fin_del_juego == 0:
            grupo_enemigos.update()
            if pygame.sprite.spritecollide(jugador, grupo_monedas, True):
                puntuacion += 1
            dibujar_texto('X ' + str(puntuacion), fuente_puntuacion, blanco, tamanio_casilla - 10, 10)

        grupo_enemigos.draw(pantalla)
        grupo_lava.draw(pantalla)
        grupo_monedas.draw(pantalla)
        grupo_salida.draw(pantalla)

        fin_del_juego = jugador.actualizar(fin_del_juego)

        if fin_del_juego == -1:
            if boton_reinicio.dibujar():
                datos_mundo = []
                mundo = reiniciar_nivel(nivel)
                fin_del_juego = 0
                puntuacion = 0

        if fin_del_juego == 1:
            nivel += 1
            if nivel <= max_niveles:
                datos_mundo = []
                mundo = reiniciar_nivel(nivel)
                fin_del_juego = 0
            else:
                dibujar_texto('¡GANASTE!', fuente, azul, (ancho_pantalla // 2) - 140, alto_pantalla // 2)
                if boton_reinicio.dibujar():
                    nivel = 1
                    datos_mundo = []
                    mundo = reiniciar_nivel(nivel)
                    fin_del_juego = 0
                    puntuacion = 0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            correr = False

    pygame.display.update()

pygame.quit()
