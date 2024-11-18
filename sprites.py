import math
import pygame
from pygame.math import Vector2
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
import random


# Clase para los disparos de láser
class Laser(pygame.sprite.Sprite):

    def __init__(self, pos, direction, laser_image):
        super().__init__()
        self.image = laser_image
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = direction * 25  # Velocidad del láser
        self.lifetime = 3000  # El láser desaparecerá después de 3 segundos
        self.spawn_time = pygame.time.get_ticks()  # Tiempo en el que fue disparado
        self.damage = 100

    def update(self):
        self.position += self.velocity
        self.rect.center = self.position

        # Si el láser ha estado en pantalla por más de 3 segundos, eliminarlo
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

        # Si el láser sale de la pantalla, eliminarlo
        if (self.rect.right < 0 or self.rect.left > MAP_WIDTH or
            self.rect.bottom < 0 or self.rect.top > MAP_HEIGHT):
            self.kill()
        

# Clase para la nave del jugador
class PlayerShip(pygame.sprite.Sprite):

    def __init__(self, pos, ship_image, thruster_image, laser_image, shoot_sound):
        super().__init__()
        self.original_image = ship_image  # Imagen sin rotar de la nave
        self.thruster_image = thruster_image  # Imagen de la propulsión
        self.original_laser_image = laser_image  # Imagen del láser
        self.shoot_sound = shoot_sound  # Sonido de disparo
        self.image = ship_image
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.direction = Vector2(0, -1)  # Apuntando hacia arriba inicialmente
        self.angle = 0  # Ángulo de rotación
        self.rotation_speed = 5  # Velocidad de rotación
        self.speed = 10  # Velocidad de movimiento
        self.moving_forward = False  # Estado para controlar si se está moviendo
        self.last_shot_time = 0  # Temporizador para controlar los disparos
        self.shoot_mode = "normal"  # Modos: 'normal', 'doble', 'rápido'
        self.mode_duration = 0  # Duración temporal del modo especial
        self.health = 100  # Vida inicial del jugador (1-100)
        if self.shoot_mode == "doble":
            self.original_image = pygame.image.load('assets/images/ship_2.png').convert_alpha()

    def update(self, keys, laser_group):
        # Rotar la nave
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed  # Gira a la derecha
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed  # Gira a la izquierda
        
        # Aplicar la rotación a la dirección de movimiento
        self.direction = Vector2(0, -1).rotate(self.angle)
        
        # Mover la nave hacia adelante
        if keys[pygame.K_UP]:
            self.velocity = self.direction * self.speed
            self.moving_forward = True  # Está en movimiento
        else:
            self.velocity *= 0.9  # Frenar lentamente cuando no se mueve
            self.moving_forward = False  # No se está moviendo

        # Actualizar la posición
        self.position += self.velocity
        self.rect.center = self.position

        # Actualizar la rotación de la imagen
        self.image = pygame.transform.rotate(self.original_image, -self.angle)  # Rotación inversa para la imagen
        self.rect = self.image.get_rect(center=self.rect.center)

        # Efecto wraparound: reaparecer en el lado opuesto
        if self.rect.right < 0:  # Sale por la izquierda
            self.position.x = MAP_WIDTH
        elif self.rect.left > MAP_WIDTH:  # Sale por la derecha
            self.position.x = 0
        if self.rect.bottom < 0:  # Sale por arriba
            self.position.y = MAP_HEIGHT
        elif self.rect.top > MAP_HEIGHT:  # Sale por abajo
            self.position.y = 0

        # Asegurarse de actualizar la posición después de wraparound
        self.rect.center = self.position

        # Disparar láser con tecla ESPACIO
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            fire_rate = 500  # Intervalo entre disparos para modo normal (0.5 segundos)

            if self.shoot_mode == "rápido":
                fire_rate = 200  # Disparos rápidos (0.2 segundos)
            if current_time - self.last_shot_time > fire_rate:
                self.shoot(laser_group)
                self.last_shot_time = current_time

    def shoot(self, laser_group):
        if self.shoot_mode == "doble":
            # Crear dos láseres: uno a la izquierda y otro a la derecha
            offset = Vector2(25, 0).rotate(-self.angle)  # Distancia entre los disparos
            laser_left = Laser(self.rect.center - offset, self.direction, pygame.transform.rotate(self.original_laser_image, -self.angle))
            laser_right = Laser(self.rect.center + offset, self.direction, pygame.transform.rotate(self.original_laser_image, -self.angle))
            laser_group.add(laser_left, laser_right)
        else:
            # Modo normal o rápido: un solo láser
            laser = Laser(self.rect.center, self.direction, pygame.transform.rotate(self.original_laser_image, -self.angle))
            laser_group.add(laser)

        self.shoot_sound.play()  # Reproducir el sonido del disparo

    def draw(self, screen, camera_x, camera_y):
        # Dibujar el thruster (propulsión) si la nave está avanzando
        if self.moving_forward:
            thruster = pygame.transform.rotate(self.thruster_image, -self.angle)  # Rotar propulsión según ángulo
            thruster_rect = thruster.get_rect(center=self.rect.center)
            thruster_offset = self.direction * -35  # Distancia detrás de la nave
            thruster_rect.center += thruster_offset
            # Ajustar el thruster a la cámara
            thruster_rect.x -= camera_x
            thruster_rect.y -= camera_y
            screen.blit(thruster, thruster_rect)

        # Ajustar la posición de la nave a la cámara
        adjusted_rect = self.rect.move(-camera_x, -camera_y)
        screen.blit(self.image, adjusted_rect)
        
    def draw_health_bar(self, screen):
        # Posición y tamaño de la barra de vida
        bar_width = SCREEN_WIDTH
        bar_height = 10
        bar_x = 0
        bar_y = 0

        # Proporción de la vida restante
        health_percentage = self.health / 100
        current_bar_width = int(bar_width * health_percentage)

        # Color dependiendo del porcentaje de vida
        if health_percentage > 0.7:
            bar_color = (0, 255, 0)  # Verde
        elif health_percentage > 0.3:
            bar_color = (255, 255, 0)  # Amarillo
        else:
            bar_color = (255, 0, 0)  # Rojo

        # Dibujar la barra de vida
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, current_bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)  # Borde blanco


class Asteroid(pygame.sprite.Sprite):
    
    def __init__(self, pos=None, image=None):
        super().__init__()
        
        # Generar posición aleatoria en cualquier borde del mapa si no se proporciona
        if pos is None:
            pos = self.generate_random_position_on_edge()
        self.position = Vector2(pos)

        # Cargar imagen de asteroide si no se proporciona
        if image is None:
            self.image = pygame.image.load('assets/images/asteroid.png').convert_alpha()
        else:
            self.image = image

        # Escalar el asteroide a un tamaño aleatorio
        self.scale = random.uniform(0.8, 1.0)  # Tamaño aleatorio
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
        self.original_image = self.image  # Guardar imagen original para rotación
        self.rect = self.image.get_rect(center=self.position)

        # Velocidad y dirección aleatoria
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

        # Rotación del asteroide
        self.angle = 0
        self.rotation_speed = random.uniform(-2, 2)  # Velocidad de rotación aleatoria
        self.fragmentation_level = 3

    def generate_random_position_on_edge(self):
        """Genera una posición aleatoria en los bordes del mapa."""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.randint(0, MAP_WIDTH), 0
        elif side == 'bottom':
            return random.randint(0, MAP_WIDTH), MAP_HEIGHT
        elif side == 'left':
            return 0, random.randint(0, MAP_HEIGHT)
        elif side == 'right':
            return MAP_WIDTH, random.randint(0, MAP_HEIGHT)

    def update(self, asteroid_group):
        # Mover el asteroide
        self.position += self.velocity
        self.rect.center = self.position

        # Rotar el asteroide
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Detectar colisiones con otros asteroides
        #self.handle_collisions(asteroid_group)
        
        # Teletransportarse a través de los bordes del mapa
        self.wrap_around_map()

    def wrap_around_map(self):
        """Permite que el asteroide aparezca en el lado opuesto cuando cruza los bordes."""
        if self.position.x < 0:
            self.position.x = MAP_WIDTH
        elif self.position.x > MAP_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = MAP_HEIGHT
        elif self.position.y > MAP_HEIGHT:
            self.position.y = 0

    def fragment(self, asteroid_group):
        """Crea fragmentos más pequeños del asteroide si es posible."""
        if self.fragmentation_level > 0:
            for _ in range(3):
                # Calcular una posición ligeramente desplazada para los nuevos asteroides
                new_pos = (self.position.x + random.randint(-20, 20),
                           self.position.y + random.randint(-20, 20))

                # Reducir la escala del asteroide
                new_scale = self.scale * 0.7  # Reducir el tamaño de los fragmentos
                if new_scale < 0.3:
                    continue  # Evitar asteroides demasiado pequeños

                # Reducir el tamaño de la imagen
                new_image = pygame.transform.scale(self.original_image,
                                                   (int(self.original_image.get_width() * new_scale),
                                                    int(self.original_image.get_height() * new_scale)))

                # Crear un nuevo asteroide con una velocidad aleatoria
                new_asteroid = Asteroid(pos=new_pos, image=new_image)
                new_asteroid.scale = new_scale
                new_asteroid.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))  # Velocidades diferentes
                new_asteroid.fragmentation_level = self.fragmentation_level - 1
                asteroid_group.add(new_asteroid)

            self.kill()  # Eliminar el asteroide original

    def handle_collisions(self, asteroid_group):
        """Gestiona las colisiones entre asteroides, invirtiendo su dirección."""
        for asteroid in asteroid_group:
            if asteroid != self and pygame.sprite.collide_rect(self, asteroid):
                # Invertir direcciones al colisionar
                self.velocity *= -1
                asteroid.velocity *= -1

class LinearCongruence:
    def __init__(self, xo, n, k, c, g, min_val, max_val):
        self.xo = xo
        self.n = n
        self.k = k
        self.c = c
        self.g = g
        self.min_val = min_val
        self.max_val = max_val

    def generate(self):
        """Genera una secuencia de números pseudoaleatorios."""
        xn = self.xo
        for _ in range(self.n):
            xn = ((self.k * xn) + self.c) % 2**self.g
            rn = xn / (2**self.g - 1)  # Normalizar a [0, 1)
            scaled_rn = self.min_val + (self.max_val - self.min_val) * rn
            yield xn, rn, scaled_rn

class GlowWorm(pygame.sprite.Sprite):
    def __init__(self, pos, length=25, speed=25, color=(100, 255, 100)):
        super().__init__()
        self.segments = [pos]
        self.length = length
        self.speed = speed
        self.color = color
        self.favored_direction = random.choice(['up', 'down', 'left', 'right'])
        self.health = 100
        
        # Inicializar el generador de congruencia lineal con parámetros aleatorios
        self.generator = LinearCongruence(
            xo=random.randint(1, 1000),  # Semilla aleatoria
            n=1000, 
            k=random.randint(1, 10),    # k aleatorio
            c=random.randint(1, 10),    # c aleatorio
            g=random.randint(5, 10),    # g aleatorio
            min_val=0, 
            max_val=4
        )
        self.steps = [result[2] for result in self.generator.generate()]  # Obtener los números aleatorios generados
        self.step_counter = 0

        self.image = pygame.Surface((25, 25)).convert_alpha()
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=pos)
    
    def update_favored_direction(self):
        self.favored_direction = random.choice(['up', 'down', 'left', 'right'])

    def update(self, keys, laser_group):
        # Obtener la dirección del movimiento de la caminata aleatoria
        step = self.steps[self.step_counter]
        self.step_counter = (self.step_counter + 1) % len(self.steps)  # Reiniciar si se llega al final de la lista

        if self.step_counter % 30 == 0:
            self.update_favored_direction()

        # Mover la cabeza en la dirección actual
        head_x, head_y = self.segments[0]
        if self.favored_direction == 'up':
            if 0 < step <= 2:  # Arriba (mayor probabilidad)
                head_y -= self.speed
            elif 2 < step <= 3:  # Abajo
                head_y += self.speed
            elif 3 < step <= 3.5:  # Derecha
                head_x += self.speed
            elif 3.5 < step <= 4:  # Izquierda
                head_x -= self.speed
        elif self.favored_direction == 'down':
            if 0 < step <= 2:  # Abajo (mayor probabilidad)
                head_y += self.speed
            elif 2 < step <= 3:  # Arriba
                head_y -= self.speed
            elif 3 < step <= 3.5:  # Derecha
                head_x += self.speed
            elif 3.5 < step <= 4:  # Izquierda
                head_x -= self.speed
        elif self.favored_direction == 'left':
            if 0 < step <= 2:  # Izquierda (mayor probabilidad)
                head_x -= self.speed
            elif 2 < step <= 3:  # Derecha
                head_x += self.speed
            elif 3 < step <= 3.5:  # Arriba
                head_y -= self.speed
            elif 3.5 < step <= 4:  # Abajo
                head_y += self.speed
        elif self.favored_direction == 'right':
            if 0 < step <= 2:  # Derecha (mayor probabilidad)
                head_x += self.speed
            elif 2 < step <= 3:  # Izquierda
                head_x -= self.speed
            elif 3 < step <= 3.5:  # Arriba
                head_y -= self.speed
            elif 3.5 < step <= 4:  # Abajo
                head_y += self.speed

        # Aplicar el efecto wraparound
        head_x %= MAP_WIDTH
        head_y %= MAP_HEIGHT

        self.segments.insert(0, (head_x, head_y))

        # Ajustar la longitud del gusano
        if len(self.segments) > self.length:
            self.segments.pop()

        # Actualizar la posición del rectángulo
        self.rect.center = self.segments[0]

    def draw(self, screen, camera_x, camera_y):
        for i, segment in enumerate(self.segments):
            x, y = segment
            # Calcular el radio del brillo en función de la posición del segmento
            radius = 5 + (len(self.segments) - i) * 2
            # Dibujar un círculo con brillo
            pygame.draw.circle(screen, self.color, (x - camera_x, y - camera_y), radius)
            
            
class Kamikaze(pygame.sprite.Sprite):
    def __init__(self, pos, kamikaze_image, player):  # Agrega la imagen del kamikaze
        super().__init__()
        self.image = kamikaze_image  # Asigna la imagen
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.speed = 5  # Ajusta la velocidad según sea necesario
        self.player = player  # Referencia al jugador para la persecución

    def update(self, keys, laser_group):
        # Calcula la dirección hacia el jugador
        direction = self.player.position - self.position
        direction.normalize_ip()  # Normaliza el vector de dirección

        # Mueve al kamikaze hacia el jugador
        self.velocity = direction * self.speed
        self.position += self.velocity
        self.rect.center = self.position

        # Aplicar el efecto wraparound
        if self.rect.right < 0:
            self.position.x = MAP_WIDTH
        elif self.rect.left > MAP_WIDTH:
            self.position.x = 0
        if self.rect.bottom < 0:
            self.position.y = MAP_HEIGHT
        elif self.rect.top > MAP_HEIGHT:
            self.position.y = 0

        self.rect.center = self.position  # Actualizar la posición del rectángulo
            
    def draw(self, screen, camera_x, camera_y):
        # Ajustar la posición del kamikaze a la cámara
        adjusted_rect = self.rect.move(-camera_x, -camera_y)
        screen.blit(self.image, adjusted_rect)
        
        
class Pripyat(pygame.sprite.Sprite):
    def __init__(self, pos, pripyat_image, player):
        super().__init__()
        self.image = pripyat_image
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.speed = 3
        self.player = player
        self.orbit_radius = 100
        self.orbit_angle = 0

    def update(self, keys, laser_group):
        distance_to_player = self.position.distance_to(self.player.position)

        if distance_to_player > self.orbit_radius:
            direction = self.player.position - self.position
            direction.normalize_ip()
            self.velocity = direction * self.speed
            self.position += self.velocity
        else:
            self.orbit_angle += self.speed / self.orbit_radius
            self.position.x = self.player.position.x + self.orbit_radius * math.cos(self.orbit_angle)
            self.position.y = self.player.position.y + self.orbit_radius * math.sin(self.orbit_angle)

        self.wraparound()
        self.rect.center = self.position

    def wraparound(self):
        if self.position.x < 0:
            self.position.x = MAP_WIDTH
        elif self.position.x > MAP_WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = MAP_HEIGHT
        elif self.position.y > MAP_HEIGHT:
            self.position.y = 0

    def draw(self, screen, camera_x, camera_y):
        adjusted_rect = self.rect.move(-camera_x, -camera_y)
        screen.blit(self.image, adjusted_rect)