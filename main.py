import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

reloj = pygame.time.Clock()
fps = 60

# Ventana del juego
pantalla_size = 1000
ancho_pantalla = pantalla_size
alto_pantalla = pantalla_size

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformas')


# Define la fuente
fuente = pygame.font.SysFont('Bauhaus 93', 70)
fuente_puntaje = pygame.font.SysFont('Bauhaus 93', 30)


# Define las variables del juego
tamano_bloque = 50
fin_juego = 0
menu_principal = True
nivel = 3
max_niveles = 7
puntaje = 0


# Define los colores
blanco = (255, 255, 255)
azul = 	(255, 255, 255)


# Carga las imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')
img_reiniciar = pygame.image.load('img/restart_btn.png')
img_inicio = pygame.image.load('img/start_btn.png')
img_salir = pygame.image.load('img/exit_btn.png')

# Carga los sonidos
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


# Función para reiniciar el nivel
def reiniciar_nivel(nivel):
    jugador.reiniciar(100, alto_pantalla - 130)
    grupo_blobs.empty()
    grupo_plataformas.empty()
    grupo_monedas.empty()
    grupo_lava.empty()
    grupo_salida.empty()

    # Carga los datos del nivel y crea el mundo
    if path.exists(f'./niveles/level{nivel}_data'):
        pickle_in = open(f'./niveles/level{nivel}_data', 'rb')
        datos_mundo = pickle.load(pickle_in)
    mundo = Mundo(datos_mundo)
    # Crea una moneda ficticia para mostrar el puntaje
    moneda_puntaje = Moneda(tamano_bloque // 2, tamano_bloque // 2)
    grupo_monedas.add(moneda_puntaje)
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

        # Obtiene la posición del ratón
        pos = pygame.mouse.get_pos()

        # Verifica las condiciones de paso del ratón y clickeo
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clickeado:
                accion = True
                self.clickeado = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clickeado = False

        # Dibuja el botón
        pantalla.blit(self.imagen, self.rect)

        return accion


class Jugador():
    def __init__(self, x, y):
        self.reiniciar(x, y)

    def actualizar(self, fin_juego):
        dx = 0
        dy = 0
        enfriamiento_caminar = 5
        umbral_colision = 20

        if fin_juego == 0:
            # Obtiene las teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and not self.saltando and not self.en_aire:
                fx_salto.play()
                self.vel_y = -15
                self.saltando = True
            if not tecla[pygame.K_SPACE]:
                self.saltando = False
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

            # Maneja la animación
            if self.contador > enfriamiento_caminar:
                self.contador = 0
                self.indice += 1
                if self.indice >= len(self.imagenes_derecha):
                    self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            # Agrega gravedad
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Verifica colisiones
            self.en_aire = True
            for bloque in mundo.lista_bloques:
                # Verifica colisión en dirección x
                if bloque[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Verifica colisión en dirección y
                if bloque[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Verifica si está debajo del suelo, es decir, saltando
                    if self.vel_y < 0:
                        dy = bloque[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Verifica si está encima del suelo, es decir, cayendo
                    elif self.vel_y >= 0:
                        dy = bloque[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.en_aire = False

            # Verifica colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blobs, False):
                fin_juego = -1
                fx_fin_juego.play()

            # Verifica colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_juego = -1
                fx_fin_juego.play()

            # Verifica colisión con la salida
            if pygame.sprite.spritecollide(self, grupo_salida, False):
                fin_juego = 1

            # Verifica colisión con plataformas
            for plataforma in grupo_plataformas:
                # Colisión en dirección x
                if plataforma.rect.colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Colisión en dirección y
                if plataforma.rect.colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Verifica si está debajo de la plataforma
                    if abs((self.rect.top + dy) - plataforma.rect.bottom) < umbral_colision:
                        self.vel_y = 0
                        dy = plataforma.rect.bottom - self.rect.top
                    # Verifica si está encima de la plataforma
                    elif abs((self.rect.bottom + dy) - plataforma.rect.top) < umbral_colision:
                        self.rect.bottom = plataforma.rect.top - 1
                        self.en_aire = False
                        dy = 0
                    # Se mueve lateralmente con la plataforma
                    if plataforma.mover_x != 0:
                        self.rect.x += plataforma.direccion_movimiento

            # Actualiza las coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_juego == -1:
            self.imagen = self.imagen_muerto
            dibujar_texto('¡FIN DEL JUEGO!', fuente, azul, (ancho_pantalla // 2) - 200, alto_pantalla // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # Dibuja al jugador en la pantalla
        pantalla.blit(self.imagen, self.rect)

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
        self.saltando = False
        self.direccion = 0
        self.en_aire = True


class Mundo():
    def __init__(self, data):
        self.lista_bloques = []

        # Carga las imágenes
        img_suelo = pygame.image.load('img/dirt.png')
        img_pasto = pygame.image.load('img/grass.png')

        contador_fila = 0
        for fila in data:
            contador_columna = 0
            for bloque in fila:
                if bloque == 1:
                    img = pygame.transform.scale(img_suelo, (tamano_bloque, tamano_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columna * tamano_bloque
                    rect_img.y = contador_fila * tamano_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                if bloque == 2:
                    img = pygame.transform.scale(img_pasto, (tamano_bloque, tamano_bloque))
                    rect_img = img.get_rect()
                    rect_img.x = contador_columna * tamano_bloque
                    rect_img.y = contador_fila * tamano_bloque
                    bloque = (img, rect_img)
                    self.lista_bloques.append(bloque)
                if bloque == 3:
                    blob = Enemigo(contador_columna * tamano_bloque, contador_fila * tamano_bloque + 15)
                    grupo_blobs.add(blob)
                if bloque == 4:
                    plataforma = Plataforma(contador_columna * tamano_bloque, contador_fila * tamano_bloque, 1, 0)
                    grupo_plataformas.add(plataforma)
                if bloque == 5:
                    plataforma = Plataforma(contador_columna * tamano_bloque, contador_fila * tamano_bloque, 0, 1)
                    grupo_plataformas.add(plataforma)
                if bloque == 6:
                    lava = Lava(contador_columna * tamano_bloque, contador_fila * tamano_bloque + (tamano_bloque // 2))
                    grupo_lava.add(lava)
                if bloque == 7:
                    moneda = Moneda(contador_columna * tamano_bloque + (tamano_bloque // 2), contador_fila * tamano_bloque + (tamano_bloque // 2))
                    grupo_monedas.add(moneda)
                if bloque == 8:
                    salida = Salida(contador_columna * tamano_bloque, contador_fila * tamano_bloque - (tamano_bloque // 2))
                    grupo_salida.add(salida)
                contador_columna += 1
            contador_fila += 1

    def dibujar(self):
        for bloque in self.lista_bloques:
            pantalla.blit(bloque[0], bloque[1])


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


class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, mover_x, mover_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tamano_bloque, tamano_bloque // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.contador_movimiento = 0
        self.direccion_movimiento = 1
        self.mover_x = mover_x
        self.mover_y = mover_y

    def update(self):
        self.rect.x += self.direccion_movimiento * self.mover_x
        self.rect.y += self.direccion_movimiento * self.mover_y
        self.contador_movimiento += 1
        if abs(self.contador_movimiento) > 50:
            self.direccion_movimiento *= -1
            self.contador_movimiento *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tamano_bloque, tamano_bloque // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (tamano_bloque // 2, tamano_bloque // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Salida(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tamano_bloque, int(tamano_bloque * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


jugador = Jugador(100, alto_pantalla - 130)

grupo_blobs = pygame.sprite.Group()
grupo_plataformas = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()
grupo_monedas = pygame.sprite.Group()
grupo_salida = pygame.sprite.Group()

# Crea una moneda ficticia para mostrar el puntaje
moneda_puntaje = Moneda(tamano_bloque // 2, tamano_bloque // 2)
grupo_monedas.add(moneda_puntaje)

# Carga los datos del nivel y crea el mundo
if path.exists(f'./niveles/level{nivel}_data'):
    pickle_in = open(f'./niveles/level{nivel}_data', 'rb')
    datos_mundo = pickle.load(pickle_in)
mundo = Mundo(datos_mundo)


# Crea los botones
boton_reiniciar = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, img_reiniciar)
boton_inicio = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, img_inicio)
boton_salir = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, img_salir)


corriendo = True
while corriendo:

    reloj.tick(fps)

    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (100, 100))

    if menu_principal:
        if boton_salir.dibujar():
            corriendo = False
        if boton_inicio.dibujar():
            menu_principal = False
    else:
        mundo.dibujar()

        if fin_juego == 0:
            grupo_blobs.update()
            grupo_plataformas.update()
            # Actualiza el puntaje
            # Verifica si se ha recogido una moneda
            if pygame.sprite.spritecollide(jugador, grupo_monedas, True):
                puntaje += 1
                fx_moneda.play()
            dibujar_texto('X ' + str(puntaje), fuente_puntaje, blanco, tamano_bloque - 10, 10)
        
        grupo_blobs.draw(pantalla)
        grupo_plataformas.draw(pantalla)
        grupo_lava.draw(pantalla)
        grupo_monedas.draw(pantalla)
        grupo_salida.draw(pantalla)

        fin_juego = jugador.actualizar(fin_juego)

        # Si el jugador ha muerto
        if fin_juego == -1:
            if boton_reiniciar.dibujar():
                datos_mundo = []
                mundo = reiniciar_nivel(nivel)
                fin_juego = 0
                puntaje = 0

        # Si el jugador ha completado el nivel
        if fin_juego == 1:
            # Reinicia el juego y pasa al siguiente nivel
            nivel += 1
            if nivel <= max_niveles:
                # Reinicia el nivel
                datos_mundo = []
                mundo = reiniciar_nivel(nivel)
                fin_juego = 0
            else:
                dibujar_texto('¡GANASTE!', fuente, azul, (ancho_pantalla // 2) - 140, alto_pantalla // 2)
                if boton_reiniciar.dibujar():
                    nivel = 1
                    # Reinicia el nivel
                    datos_mundo = []
                    mundo = reiniciar_nivel(nivel)
                    fin_juego = 0
                    puntaje = 0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    pygame.display.update()

pygame.quit()
