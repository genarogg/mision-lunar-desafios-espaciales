import pygame
from pygame.locals import *

pygame.init()

reloj = pygame.time.Clock()
fps = 60

ancho_pantalla = 1000
alto_pantalla = 1000

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Plataformero')

# Definir variables del juego
tamaño_bloque = 50
fin_del_juego = 0

# Cargar imágenes
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
		self.imagen_muerto = pygame.image.load('img/ghost.png')
		self.imagen = self.imagenes_derecha[self.indice]
		self.rectangulo = self.imagen.get_rect()
		self.rectangulo.x = x
		self.rectangulo.y = y
		self.ancho = self.imagen.get_width()
		self.alto = self.imagen.get_height()
		self.vel_y = 0
		self.salto = False
		self.direccion = 0

	def actualizar(self, fin_del_juego):
		dx = 0
		dy = 0
		enfriamiento_caminata = 5

		if fin_del_juego == 0:
			# Obtener teclas presionadas
			tecla = pygame.key.get_pressed()
			if tecla[pygame.K_SPACE] and not self.salto:
				self.vel_y = -15
				self.salto = True
			if not tecla[pygame.K_SPACE]:
				self.salto = False
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
			if self.contador > enfriamiento_caminata:
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
			for bloque in lista_de_bloques:
				# Verificar colisión en dirección x
				if bloque[1].colliderect(self.rectangulo.x + dx, self.rectangulo.y, self.ancho, self.alto):
					dx = 0
				# Verificar colisión en dirección y
				if bloque[1].colliderect(self.rectangulo.x, self.rectangulo.y + dy, self.ancho, self.alto):
					# Verificar si está debajo del suelo, es decir, saltando
					if self.vel_y < 0:
						dy = bloque[1].bottom - self.rectangulo.top
						self.vel_y = 0
					# Verificar si está sobre el suelo, es decir, cayendo
					elif self.vel_y >= 0:
						dy = bloque[1].top - self.rectangulo.bottom
						self.vel_y = 0

			# Verificar colisión con enemigos
			if pygame.sprite.spritecollide(self, grupo_de_enemigos, False):
				fin_del_juego = -1

			# Verificar colisión con lava
			if pygame.sprite.spritecollide(self, grupo_de_lava, False):
				fin_del_juego = -1

			# Actualizar coordenadas del jugador
			self.rectangulo.x += dx
			self.rectangulo.y += dy

		elif fin_del_juego == -1:
			self.imagen = self.imagen_muerto
			if self.rectangulo.y > 200:
				self.rectangulo.y -= 5

		# Dibujar jugador en la pantalla
		pantalla.blit(self.imagen, self.rectangulo)
		pygame.draw.rect(pantalla, (255, 255, 255), self.rectangulo, 2)

		return fin_del_juego
	
class Mundo():
	def __init__(self, datos):
		self.lista_tiles = []

		#cargar imágenes
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')

		fila_contador = 0
		for fila in datos:
			columna_contador = 0
			for tile in fila:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tamaño_tile, tamaño_tile))
					img_rect = img.get_rect()
					img_rect.x = columna_contador * tamaño_tile
					img_rect.y = fila_contador * tamaño_tile
					tile = (img, img_rect)
					self.lista_tiles.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tamaño_tile, tamaño_tile))
					img_rect = img.get_rect()
					img_rect.x = columna_contador * tamaño_tile
					img_rect.y = fila_contador * tamaño_tile
					tile = (img, img_rect)
					self.lista_tiles.append(tile)
				if tile == 3:
					blob = Enemigo(columna_contador * tamaño_tile, fila_contador * tamaño_tile + 15)
					grupo_blob.add(blob)
				if tile == 6:
					lava = Lava(columna_contador * tamaño_tile, fila_contador * tamaño_tile + (tamaño_tile // 2))
					grupo_lava.add(lava)

				columna_contador += 1
			fila_contador += 1

	def dibujar(self):
		for tile in self.lista_tiles:
			pantalla.blit(tile[0], tile[1])
			pygame.draw.rect(pantalla, (255, 255, 255), tile[1], 2)


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
		self.imagen = pygame.transform.scale(img, (tamaño_tile, tamaño_tile // 2))
		self.rect = self.imagen.get_rect()
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

grupo_blob = pygame.sprite.Group()
grupo_lava = pygame.sprite.Group()

mundo = Mundo(datos_mundo)

corriendo = True
while corriendo:

	reloj.tick(fps)

	pantalla.blit(img_fondo, (0, 0))
	pantalla.blit(img_sol, (100, 100))

	mundo.dibujar()

	if fin_juego == 0:
		grupo_blob.update()
	
	grupo_blob.draw(pantalla)
	grupo_lava.draw(pantalla)

	fin_juego = jugador.update(fin_juego)

	for evento in pygame.event.get():
		if evento.type == pygame.QUIT:
			corriendo = False

	pygame.display.update()

pygame.quit()
