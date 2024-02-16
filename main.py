import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')

# Definir fuente
fuente = pygame.font.SysFont('Bauhaus 93', 70)
fuente_puntuacion = pygame.font.SysFont('Bauhaus 93', 30)

# Definir variables del juego
tamaño_celda = 50
fin_juego = 0
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

# Cargar sonidos
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
fx_moneda = pygame.mixer.Sound('img/coin.wav')
fx_moneda.set_volume(0.5)
fx_salto = pygame.mixer.Sound('img/jump.wav')
fx_salto.set_volume(0.5)
fx_fin_juego = pygame.mixer.Sound('img/game_over.wav')
fx_fin_juego.set_volume(0.5)


def dibujar_texto(texto, fuente, color_texto, x, y):
    img = fuente.render(texto, True, color_texto)
    pantalla.blit(img, (x, y))


# Función para reiniciar nivel
def reiniciar_nivel(nivel):
    jugador.resetear(100, alto_pantalla - 130)
    grupo_blob.empty()
    grupo_lava.empty()
    grupo_salida.empty()

    # Cargar datos del nivel y crear mundo
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

        # Obtener posición del ratón
        pos = pygame.mouse.get_pos()

        # Verificar condiciones de ratón sobre el botón y clickeado
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
        self.reiniciar(x, y)

    def actualizar(self, fin_juego):
        dx = 0
        dy = 0
        cooldown_caminar = 5

        if fin_juego == 0:
            # Obtener teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
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

            # Manejar la animación
            if self.contador > cooldown_caminar:
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

            # Verificar colisiones
            self.in_air = True
            for tile in mundo.lista_tiles:
                # Verificar colisión en dirección x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Verificar colisión en dirección y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Verificar si está debajo del suelo, es decir, saltando
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Verificar si está sobre el suelo, es decir, cayendo
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # Verificar colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blob, False):
                fin_juego = -1
                game_over_fx.play()

            # Verificar colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_juego = -1
                game_over_fx.play()

            # Verificar colisión con la salida
            if pygame.sprite.spritecollide(self, grupo_salida, False):
                fin_juego = 1

            # Actualizar coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_juego == -1:
            self.imagen = self.imagen_muerto
            dibujar_texto('¡JUEGO TERMINADO!', fuente, azul, (ancho_pantalla // 2) - 200, alto_pantalla // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # Dibujar jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)

        return fin_juego

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
        self.jumped = False
        self.direccion = 0
        self.in_air = True

class Mundo():
    def __init__(self, datos):
        self.lista_de_tiles = []

        # Cargar imágenes
        img_tierra = pygame.image.load('img/tierra.png')
        img_pasto = pygame.image.load('img/pasto.png')

        contador_filas = 0
        for fila in datos:
            contador_columnas = 0
            for tile in fila:
                if tile == 1:
                    img = pygame.transform.scale(img_tierra, (tamaño_celda, tamaño_celda))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_celda
                    rect_img.y = contador_filas * tamaño_celda
                    tile = (img, rect_img)
                    self.lista_de_tiles.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(img_pasto, (tamaño_celda, tamaño_celda))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columnas * tamaño_celda
                    rect_img.y = contador_filas * tamaño_celda
                    tile = (img, rect_img)
                    self.lista_de_tiles.append(tile)
                if tile == 3:
                    blob = Enemigo(contador_columnas * tamaño_celda, contador_filas * tamaño_celda + 15)
                    grupo_blob.add(blob)
                if tile == 6:
                    lava = Lava(contador_columnas * tamaño_celda, contador_filas * tamaño_celda + (tamaño_celda // 2))
                    grupo_lava.add(lava)
                if tile == 7:
                    moneda = Moneda(contador_columnas * tamaño_celda + (tamaño_celda // 2), contador_filas * tamaño_celda + (tamaño_celda // 2))
                    grupo_moneda.add(moneda)
                if tile == 8:
                    salida = Salida(contador_columnas * tamaño_celda, contador_filas * tamaño_celda - (tamaño_celda // 2))
                    grupo_salida.add(salida)
                contador_columnas += 1
            contador_filas += 1

    def dibujar(self):
        for tile in self.lista_de_tiles:
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
        self.image = pygame.transform.scale(img, (tamaño_celda, tamaño_celda // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/moneda.png')
        self.image = pygame.transform.scale(img, (tamaño_celda // 2, tamaño_celda // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Salida(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/salida.png')
        self.image = pygame.transform.scale(img, (tamaño_celda, int(tamaño_celda * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

jugador = Jugador(100, alto_pantalla - 130)

grupo_blobs = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()
grupo_monedas = pygame.sprite.Group()
grupo_salidas = pygame.sprite.Group()

# Crear una moneda ficticia para mostrar la puntuación
moneda_puntuacion = Moneda(tamaño_celda // 2, tamaño_celda // 2)
grupo_monedas.add(moneda_puntuacion)

# Cargar los datos del nivel y crear el mundo
if path.exists(f'datos_nivel{nivel}_data'):
    pickle_in = open(f'datos_nivel{nivel}_data', 'rb')
    datos_mundo = pickle.load(pickle_in)
mundo = Mundo(datos_mundo)

# Crear botones
boton_reiniciar = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, imagen_reinicio)
boton_inicio = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, imagen_inicio)
boton_salida = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, imagen_salida)

correr = True
while correr:

    reloj.tick(fps)

    pantalla.blit(imagen_fondo, (0, 0))
    pantalla.blit(imagen_sol, (100, 100))

    if menu_principal == True:
        if boton_salida.draw():
            correr = False
        if boton_inicio.draw():
            menu_principal = False
    else:
        mundo.dibujar()

        if fin_juego == 0:
            grupo_blobs.update()
            # Actualizar puntuación
            # Verificar si se ha recolectado una moneda
            if pygame.sprite.spritecollide(jugador, grupo_monedas, True):
                puntuacion += 1
                efecto_moneda.play()
            dibujar_texto('X ' + str(puntuacion), fuente_puntuacion, blanco, tamaño_celda - 10, 10)
        
        grupo_blobs.draw(pantalla)
        grupo_lava.draw(pantalla)
        grupo_monedas.draw(pantalla)
        grupo_salidas.draw(pantalla)

        fin_juego = jugador.actualizar(fin_juego)

        # Si el jugador ha muerto
        if fin_juego == -1:
            if boton_reiniciar.draw():
                datos_mundo = []
                mundo = resetear_nivel(nivel)
                fin_juego = 0
                puntuacion = 0

        # Si el jugador ha completado el nivel
        if fin_juego == 1:
            # Reiniciar juego e ir al siguiente nivel
            nivel += 1
            if nivel <= max_niveles:
                # Reiniciar nivel
                datos_mundo = []
                mundo = resetear_nivel(nivel)
                fin_juego = 0
            else:
                dibujar_texto('¡GANASTE!', fuente, azul, (ancho_pantalla // 2) - 140, alto_pantalla // 2)
                if boton_reiniciar.draw():
                    nivel = 1
                    # Reiniciar nivel
                    datos_mundo = []
                    mundo = resetear_nivel(nivel)
                    fin_juego = 0
                    puntuacion = 0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            correr = False

    pygame.display.update()

pygame.quit()
