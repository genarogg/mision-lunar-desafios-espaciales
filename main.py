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

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Juego de Plataformas')

# Definir fuente
fuente = pygame.font.SysFont('Bauhaus 93', 70)
fuente_puntuacion = pygame.font.SysFont('Bauhaus 93', 30)

# Definir variables del juego
tamano_bloque = 50
fin_juego = 0
menu_principal = True
nivel = 3
max_niveles = 7
puntuacion = 0

# Definir colores
blanco = (255, 255, 255)
azul = (0, 0, 255)

# Cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')
img_reiniciar = pygame.image.load('img/restart_btn.png')
img_inicio = pygame.image.load('img/start_btn.png')
img_salida = pygame.image.load('img/exit_btn.png')

# Cargar sonidos
fx_moneda = pygame.mixer.Sound('img/coin.wav')
fx_moneda.set_volume(0.5)
fx_salto = pygame.mixer.Sound('img/jump.wav')
fx_salto.set_volume(0.5)
fx_fin_juego = pygame.mixer.Sound('img/game_over.wav')
fx_fin_juego.set_volume(0.5)

# Definir función para dibujar texto
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
        self.resetear(x, y)

    def actualizar(self, fin_juego):
        dx = 0
        dy = 0
        tiempo_entre_pasos = 5

        if fin_juego == 0:
            # Obtener teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and not self.saltado and not self.en_aire:
                fx_salto.play()
                self.vel_y = -15
                self.saltado = True
            if not tecla[pygame.K_SPACE]:
                self.saltado = False
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
            if self.contador > tiempo_entre_pasos:
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

            # Verificar colisión
            self.en_aire = True
            for bloque in mundo.lista_bloques:
                # Verificar colisión en dirección x
                if bloque[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                # Verificar colisión en dirección y
                if bloque[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    # Verificar si está debajo del suelo (saltando)
                    if self.vel_y < 0:
                        dy = bloque[1].bottom - self.rect.top
                        self.vel_y = 0
                    # Verificar si está encima del suelo (cayendo)
                    elif self.vel_y >= 0:
                        dy = bloque[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.en_aire = False

            # Verificar colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blob, False):
                fin_juego = -1
                fx_fin_juego.play()

            # Verificar colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_juego = -1
                fx_fin_juego.play()

            # Verificar colisión con salida
            if pygame.sprite.spritecollide(self, grupo_salida, False):
                fin_juego = 1

            # Actualizar coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_juego == -1:
            self.imagen = self.imagen_muerto
            dibujar_texto('¡FIN DEL JUEGO!', fuente, azul, (ancho_pantalla // 2) - 200, alto_pantalla // 2)
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
        self.saltado = False
        self.direccion = 0
        self.en_aire = True

class Mundo():
    def __init__(self, datos):
        self.lista_bloques = []

        # Cargar imágenes
        img_tierra = pygame.image.load('img/dirt.png')
        img_pasto = pygame.image.load('img/grass.png')

        fila = 0
        for fila_datos in datos:
            columna = 0
            for bloque_datos in fila_datos:
                if bloque_datos == 1:
                    img = pygame.transform.scale(img_tierra, (tamano_bloque, tamano_bloque))
                    rect = img.get_rect()
                    rect.x = columna * tamano_bloque
                    rect.y = fila * tamano_bloque
                    bloque = (img, rect)
                    self.lista_bloques.append(bloque)
                if bloque_datos == 2:
                    img = pygame.transform.scale(img_pasto, (tamano_bloque, tamano_bloque))
                    rect = img.get_rect()
                    rect.x = columna * tamano_bloque
                    rect.y = fila * tamano_bloque
                    bloque = (img, rect)
                    self.lista_bloques.append(bloque)
                if bloque_datos == 3:
                    blob = Enemigo(columna * tamano_bloque, fila * tamano_bloque + 15)
                    grupo_blob.add(blob)
                if bloque_datos == 4:
                    plataforma = Plataforma(columna * tamano_bloque, fila * tamano_bloque, 1, 0)
                    grupo_plataforma.add(plataforma)
                if bloque_datos == 5:
                    plataforma = Plataforma(columna * tamano_bloque, fila * tamano_bloque, 0, 1)
                    grupo_plataforma.add(plataforma)
                if bloque_datos == 6:
                    lava = Lava(columna * tamano_bloque, fila * tamano_bloque + (tamano_bloque // 2))
                    grupo_lava.add(lava)
                if bloque_datos == 7:
                    moneda = Coin(columna * tamano_bloque + (tamano_bloque // 2), fila * tamano_bloque + (tamano_bloque // 2))
                    grupo_moneda.add(moneda)
                if bloque_datos == 8:
                    salida = Exit(columna * tamano_bloque, fila * tamano_bloque - (tamano_bloque // 2))
                    grupo_salida.add(salida)
                columna += 1
            fila += 1

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

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tamano_bloque, tamano_bloque // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tamano_bloque // 2, tamano_bloque // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tamano_bloque, int(tamano_bloque * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


jugador = Jugador(100, alto_pantalla - 130)

grupo_blob = pygame.sprite.Group()
grupo_plataforma = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()
grupo_moneda = pygame.sprite.Group()
grupo_salida = pygame.sprite.Group()

# crear moneda ficticia para mostrar la puntuación
moneda_puntuacion = Coin(tamano_bloque // 2, tamano_bloque // 2)
grupo_moneda.add(moneda_puntuacion)

# cargar datos de nivel y crear mundo
if path.exists(f'level{nivel}_data'):
	pickle_in = open(f'level{nivel}_data', 'rb')
	datos_mundo = pickle.load(pickle_in)
mundo = Mundo(datos_mundo)

# crear botones
boton_reiniciar = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, img_reiniciar)
boton_inicio = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, img_inicio)
boton_salida = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, img_salida)

corriendo = True
while corriendo:

	reloj.tick(fps)

	pantalla.blit(img_fondo, (0, 0))
	pantalla.blit(img_sol, (100, 100))

	if menu_principal == True:
		if boton_salida.draw():
			corriendo = False
		if boton_inicio.draw():
			menu_principal = False
	else:
		mundo.draw()

		if fin_juego == 0:
			grupo_blob.update()
			grupo_plataforma.update()
			# actualizar puntuación
			# verificar si se ha recogido una moneda
			if pygame.sprite.spritecollide(jugador, grupo_moneda, True):
				puntuación += 1
				fx_moneda.play()
			dibujar_texto('X ' + str(puntuación), fuente_puntuacion, blanco, tamano_bloque - 10, 10)
		
		grupo_blob.draw(pantalla)
		grupo_plataforma.draw(pantalla)
		grupo_lava.draw(pantalla)
		grupo_moneda.draw(pantalla)
		grupo_salida.draw(pantalla)

		fin_juego = jugador.update(fin_juego)

		# si el jugador ha muerto
		if fin_juego == -1:
			if boton_reiniciar.draw():
				datos_mundo = []
				mundo = reiniciar_nivel(nivel)
				fin_juego = 0
				puntuación = 0

		# si el jugador ha completado el nivel
		if fin_juego == 1:
			# reiniciar juego e ir al siguiente nivel
			nivel += 1
			if nivel <= max_niveles:
				# reiniciar nivel
				datos_mundo = []
				mundo = reiniciar_nivel(nivel)
				fin_juego = 0
			else:
				dibujar_texto('¡GANASTE!', fuente, azul, (ancho_pantalla // 2) - 140, alto_pantalla // 2)
				if boton_reiniciar.draw():
					nivel = 1
					# reiniciar nivel
					datos_mundo = []
					mundo = reiniciar_nivel(nivel)
					fin_juego = 0
					puntuación = 0

	for evento in pygame.event.get():
		if evento.type == pygame.QUIT:
			corriendo = False

	pygame.display.update()

pygame.quit()