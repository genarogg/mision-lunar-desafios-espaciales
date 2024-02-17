import pygame
import pickle
from os import path


pygame.init()

reloj = pygame.time.Clock()
fps = 60

#ventana del juego
tamano_celda = 50
columnas = 20
margen = 100
ancho_pantalla = tamano_celda * columnas
alto_pantalla = (tamano_celda * columnas) + margen

pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Editor de Niveles')


#cargar imágenes
img_sol = pygame.image.load('img/sun.png')
img_sol = pygame.transform.scale(img_sol, (tamano_celda, tamano_celda))
img_fondo = pygame.image.load('img/sky.png')
img_fondo = pygame.transform.scale(img_fondo, (ancho_pantalla, alto_pantalla - margen))
img_tierra = pygame.image.load('img/dirt.png')
img_hierba = pygame.image.load('img/grass.png')
img_blob = pygame.image.load('img/blob.png')
img_plataforma_x = pygame.image.load('img/platform_x.png')
img_plataforma_y = pygame.image.load('img/platform_y.png')
img_lava = pygame.image.load('img/lava.png')
img_moneda = pygame.image.load('img/coin.png')
img_salida = pygame.image.load('img/exit.png')
img_guardar = pygame.image.load('img/save_btn.png')
img_cargar = pygame.image.load('img/load_btn.png')


#definir variables del juego
clickeado = False
nivel = 1

#definir colores
blanco = (255, 255, 255)
verde = (144, 201, 120)

fuente = pygame.font.SysFont('Futura', 24)

#crear lista de celdas vacía
datos_mundo = []
for fila in range(20):
    r = [0] * 20
    datos_mundo.append(r)

#crear límites
for celda in range(0, 20):
    datos_mundo[19][celda] = 2
    datos_mundo[0][celda] = 1
    datos_mundo[celda][0] = 1
    datos_mundo[celda][19] = 1

#función para mostrar texto en la pantalla
def dibujar_texto(texto, fuente, color_texto, x, y):
    img = fuente.render(texto, True, color_texto)
    pantalla.blit(img, (x, y))

def dibujar_cuadricula():
    for c in range(21):
        #líneas verticales
        pygame.draw.line(pantalla, blanco, (c * tamano_celda, 0), (c * tamano_celda, alto_pantalla - margen))
        #líneas horizontales
        pygame.draw.line(pantalla, blanco, (0, c * tamano_celda), (ancho_pantalla, c * tamano_celda))

def dibujar_mundo():
    for fila in range(20):
        for columna in range(20):
            if datos_mundo[fila][columna] > 0:
                if datos_mundo[fila][columna] == 1:
                    #bloques de tierra
                    img = pygame.transform.scale(img_tierra, (tamano_celda, tamano_celda))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda))
                if datos_mundo[fila][columna] == 2:
                    #bloques de hierba
                    img = pygame.transform.scale(img_hierba, (tamano_celda, tamano_celda))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda))
                if datos_mundo[fila][columna] == 3:
                    #bloques de enemigos
                    img = pygame.transform.scale(img_blob, (tamano_celda, int(tamano_celda * 0.75)))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda + (tamano_celda * 0.25)))
                if datos_mundo[fila][columna] == 4:
                    #plataforma móvil horizontal
                    img = pygame.transform.scale(img_plataforma_x, (tamano_celda, tamano_celda // 2))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda))
                if datos_mundo[fila][columna] == 5:
                    #plataforma móvil vertical
                    img = pygame.transform.scale(img_plataforma_y, (tamano_celda, tamano_celda // 2))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda))
                if datos_mundo[fila][columna] == 6:
                    #lava
                    img = pygame.transform.scale(img_lava, (tamano_celda, tamano_celda // 2))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda + (tamano_celda // 2)))
                if datos_mundo[fila][columna] == 7:
                    #moneda
                    img = pygame.transform.scale(img_moneda, (tamano_celda // 2, tamano_celda // 2))
                    pantalla.blit(img, (columna * tamano_celda + (tamano_celda // 4), fila * tamano_celda + (tamano_celda // 4)))
                if datos_mundo[fila][columna] == 8:
                    #salida
                    img = pygame.transform.scale(img_salida, (tamano_celda, int(tamano_celda * 1.5)))
                    pantalla.blit(img, (columna * tamano_celda, fila * tamano_celda - (tamano_celda // 2)))


class Boton():
    def __init__(self, x, y, imagen):
        self.imagen = imagen
        self.rect = self.imagen.get_rect()
        self.rect.topleft = (x, y)
        self.clickeado = False

    def dibujar(self):
        accion = False

        #obtener posición del ratón
        pos = pygame.mouse.get_pos()

        #verificar condiciones de mouseover y clickeado
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clickeado == False:
                accion = True
                self.clickeado = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clickeado = False

        #dibujar botón
        pantalla.blit(self.imagen, (self.rect.x, self.rect.y))

        return accion

#crear botones de guardar y cargar
boton_guardar = Boton(ancho_pantalla // 2 - 150, alto_pantalla - 80, img_guardar)
boton_cargar = Boton(ancho_pantalla // 2 + 50, alto_pantalla - 80, img_cargar)

#bucle principal del juego
ejecutar = True
while ejecutar:

    reloj.tick(fps)

    #dibujar fondo
    pantalla.fill(verde)
    pantalla.blit(img_fondo, (0, 0))
    pantalla.blit(img_sol, (tamano_celda * 2, tamano_celda * 2))

    #cargar y guardar nivel
    if boton_guardar.dibujar():
        #guardar datos del nivel
        pickle_out = open(f'nivel{nivel}_datos', 'wb')
        pickle.dump(datos_mundo, pickle_out)
        pickle_out.close()
    if boton_cargar.dibujar():
        #cargar datos del nivel
        if path.exists(f'nivel{nivel}_datos'):
            pickle_in = open(f'nivel{nivel}_datos', 'rb')
            datos_mundo = pickle.load(pickle_in)


    #mostrar la cuadrícula y dibujar los bloques del nivel
    dibujar_cuadricula()
    dibujar_mundo()


    #texto mostrando el nivel actual
    dibujar_texto(f'Nivel: {nivel}', fuente, blanco, tamano_celda, alto_pantalla - 60)
    dibujar_texto('Presiona ARRIBA o ABAJO para cambiar de nivel', fuente, blanco, tamano_celda, alto_pantalla - 40)

    #manejador de eventos
    for evento in pygame.event.get():
        #salir del juego
        if evento.type == pygame.QUIT:
            ejecutar = False
        #clics del ratón para cambiar bloques
        if evento.type == pygame.MOUSEBUTTONDOWN and clickeado == False:
            clickeado = True
            pos = pygame.mouse.get_pos()
            x = pos[0] // tamano_celda
            y = pos[1] // tamano_celda
            #verificar que las coordenadas estén dentro del área de bloques
            if x < 20 and y < 20:
                #actualizar valor del bloque
                if pygame.mouse.get_pressed()[0] == 1:
                    datos_mundo[y][x] += 1
                    if datos_mundo[y][x] > 8:
                        datos_mundo[y][x] = 0
                elif pygame.mouse.get_pressed()[2] == 1:
                    datos_mundo[y][x] -= 1
                    if datos_mundo[y][x] < 0:
                        datos_mundo[y][x] = 8
        if evento.type == pygame.MOUSEBUTTONUP:
            clickeado = False
        #presiones de teclas arriba y abajo para cambiar el número de nivel
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                nivel += 1
            elif evento.key == pygame.K_DOWN and nivel > 1:
                nivel -= 1

    #actualizar ventana de visualización del juego
    pygame.display.update()

pygame.quit()