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
pygame.display.set_caption('Plataformas')

# Definir variables del juego
tamaño_bloque = 50
fin_del_juego = 0
menu_principal = True
nivel = 0
max_niveles = 7

# Cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_fondo = pygame.image.load('img/sky.png')
img_reinicio = pygame.image.load('img/restart_btn.png')
img_inicio = pygame.image.load('img/start_btn.png')
img_salida = pygame.image.load('img/exit_btn.png')

# Función para reiniciar nivel
def reiniciar_nivel(nivel):
    jugador.reset(100, alto_pantalla - 130)
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

        # Verificar condiciones de pasar el ratón por encima y hacer clic
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
        self.reset(x, y)

    def actualizar(self, fin_del_juego):
        dx = 0
        dy = 0
        tiempo_entre_pasos = 5

        if fin_del_juego == 0:
            # Obtener teclas presionadas
            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_SPACE] and not self.jugando and not self.en_aire:
                self.vel_y = -15
                self.jugando = True
            if not tecla[pygame.K_SPACE]:
                self.jugando = False
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

            # Animación
            if self.contador > tiempo_entre_pasos:
                self.contador = 0
                self.indice += 1
                if self.indice >= len(self.imagenes_derecha):
                    self.indice = 0
                if self.direccion == 1:
                    self.imagen = self.imagenes_derecha[self.indice]
                if self.direccion == -1:
                    self.imagen = self.imagenes_izquierda[self.indice]

            # Gravedad
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Colisiones
            self.en_aire = True
            for bloque in mundo.lista_bloques:
                if bloque[1].colliderect(self.rect.x + dx, self.rect.y, self.ancho, self.alto):
                    dx = 0
                if bloque[1].colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                    if self.vel_y < 0:
                        dy = bloque[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = bloque[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.en_aire = False

            # Colisión con enemigos
            if pygame.sprite.spritecollide(self, grupo_blob, False):
                fin_del_juego = -1

            # Colisión con lava
            if pygame.sprite.spritecollide(self, grupo_lava, False):
                fin_del_juego = -1

            # Colisión con salida
            if pygame.sprite.spritecollide(self, grupo_salida, False):
                fin_del_juego = 1

            # Actualizar coordenadas del jugador
            self.rect.x += dx
            self.rect.y += dy

        elif fin_del_juego == -1:
            self.imagen = self.imagen_muerto
            if self.rect.y > 200:
                self.rect.y -= 5

        # Dibujar jugador en pantalla
        pantalla.blit(self.imagen, self.rect)
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect, 2)

        return fin_del_juego

    def reset(self, x, y):
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
        self.jugando = False
        self

class Mundo():
	def __init__(self, datos):
		self.lista_de_tiles = []

		#cargar imágenes
		img_tierra = pygame.image.load('img/tierra.png')
		img_pasto = pygame.image.load('img/pasto.png')

		num_fila = 0
		for fila in datos:
			num_columna = 0
			for tile in fila:
				if tile == 1:
					img = pygame.transform.scale(img_tierra, (tamaño_de_tile, tamaño_de_tile))
					img_rect = img.get_rect()
					img_rect.x = num_columna * tamaño_de_tile
					img_rect.y = num_fila * tamaño_de_tile
					tile = (img, img_rect)
					self.lista_de_tiles.append(tile)
				if tile == 2:
					img = pygame.transform.scale(img_pasto, (tamaño_de_tile, tamaño_de_tile))
					img_rect = img.get_rect()
					img_rect.x = num_columna * tamaño_de_tile
					img_rect.y = num_fila * tamaño_de_tile
					tile = (img, img_rect)
					self.lista_de_tiles.append(tile)
				if tile == 3:
					bloque = Enemigo(num_columna * tamaño_de_tile, num_fila * tamaño_de_tile + 15)
					grupo_de_enemigos.add(bloque)
				if tile == 6:
					lava = Lava(num_columna * tamaño_de_tile, num_fila * tamaño_de_tile + (tamaño_de_tile // 2))
					grupo_de_lavas.add(lava)
				if tile == 8:
					salida = Salida(num_columna * tamaño_de_tile, num_fila * tamaño_de_tile - (tamaño_de_tile // 2))
					grupo_de_salidas.add(salida)
				num_columna += 1
			num_fila += 1


	def dibujar(self):
		for tile in self.lista_de_tiles:
			pantalla.blit(tile[0], tile[1])
			pygame.draw.rect(pantalla, (255, 255, 255), tile[1], 2)



class Enemigo(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.imagen = pygame.image.load('img/bloque.png')
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
		self.imagen = pygame.transform.scale(img, (tamaño_de_tile, tamaño_de_tile // 2))
		self.rect = self.imagen.get_rect()
		self.rect.x = x
		self.rect.y = y

class Salida(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/salida.png')
		self.imagen = pygame.transform.scale(img, (tamaño_de_tile, int(tamaño_de_tile * 1.5)))
		self.rect = self.imagen.get_rect()
		self.rect.x = x
		self.rect.y = y



jugador = Jugador(100, alto_pantalla - 130)

grupo_de_enemigos = pygame.sprite.Group()
grupo_de_lavas = pygame.sprite.Group()
grupo_de_salidas = pygame.sprite.Group()


#cargar datos del nivel y crear el mundo
if path.exists(f'datos_nivel{nivel}'):
	pickle_in = open(f'datos_nivel{nivel}', 'rb')
	datos_mundo = pickle.load(pickle_in)
mundo = Mundo(datos_mundo)


#crear botones
boton_reiniciar = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, img_reiniciar)
boton_iniciar = Boton(ancho_pantalla // 2 - 350, alto_pantalla // 2, img_iniciar)
boton_salir = Boton(ancho_pantalla // 2 + 150, alto_pantalla // 2, img_salir)


ejecutar = True
while ejecutar:

	reloj.tick(fps)

	pantalla.blit(img_fondo, (0, 0))
	pantalla.blit(img_sol, (100, 100))

	if menu_principal == True:
		if boton_salir.dibujar():
			ejecutar = False
		if boton_iniciar.dibujar():
			menu_principal = False
	else:
		mundo.dibujar()

		if fin_del_juego == 0:
			grupo_de_enemigos.update()
		
		grupo_de_enemigos.draw(pantalla)
		grupo_de_lavas.draw(pantalla)
		grupo_de_salidas.draw(pantalla)

		fin_del_juego = jugador.update(fin_del_juego)

		#si el jugador ha muerto
		if fin_del_juego == -1:
			if boton_reiniciar.dibujar():
				datos_mundo = []
				mundo = resetear_nivel(nivel)
				fin_del_juego = 0

		#si el jugador ha completado el nivel
		if fin_del_juego == 1:
			#reiniciar juego e ir al siguiente nivel
			nivel += 1
			if nivel <= max_niveles:
				#reiniciar nivel
				datos_mundo = []
				mundo = resetear_nivel(nivel)
				fin_del_juego = 0
			else:
				if boton_reiniciar.dibujar():
					nivel = 1
					#reiniciar nivel
					datos_mundo = []
					mundo = resetear_nivel(nivel)
					fin_del_juego = 0


	for evento in pygame.event.get():
		if evento.type == pygame.QUIT:
			ejecutar = False

	pygame.display.update()

pygame.quit()
