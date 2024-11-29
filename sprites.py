import math
import pygame
from pygame.math import Vector2
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
import random
from test_nums.random_all_test import RandomTests
from generator_nums.linear_congruence import LinearCongruence


# Clase para los disparos de láser
class Laser(pygame.sprite.Sprite):

    def __init__(self, pos, direction, laser_image):
        super().__init__()
        self.image = laser_image
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = direction * 20  # Velocidad del láser
        self.lifetime = 750  # El láser desaparecerá después de 0.75 segundos
        self.spawn_time = pygame.time.get_ticks()  # Tiempo en el que fue disparado
        self.damage = 100

    def update(self):
        self.position += self.velocity
        self.rect.center = self.position

        # Si el láser ha estado en pantalla por más de 0.75 segundos, eliminarlo
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
        self.score = 0
        if self.shoot_mode == "doble":
            self.original_image = pygame.image.load(
                'assets/images/ship_2.png').convert_alpha()

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
        self.image = pygame.transform.rotate(
            self.original_image, -self.angle)  # Rotación inversa para la imagen
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
            # Intervalo entre disparos para modo normal (0.5 segundos)
            fire_rate = 500

            if self.shoot_mode == "rapido":
                fire_rate = 200  # Disparos rápidos (0.2 segundos)
            if current_time - self.last_shot_time > fire_rate:
                self.shoot(laser_group)
                self.last_shot_time = current_time

    def shoot(self, laser_group):
        if self.shoot_mode == "doble":
            # Crear dos láseres: uno a la izquierda y otro a la derecha
            # Distancia entre los disparos
            offset = Vector2(25, 0).rotate(-self.angle)
            laser_left = Laser(self.rect.center - offset, self.direction,
                               pygame.transform.rotate(self.original_laser_image, -self.angle))
            laser_right = Laser(self.rect.center + offset, self.direction,
                                pygame.transform.rotate(self.original_laser_image, -self.angle))
            laser_group.add(laser_left, laser_right)
        else:
            # Modo normal o rápido: un solo láser
            laser = Laser(self.rect.center, self.direction, pygame.transform.rotate(
                self.original_laser_image, -self.angle))
            laser_group.add(laser)

        self.shoot_sound.play()  # Reproducir el sonido del disparo

    def draw(self, screen, camera_x, camera_y):
        # Dibujar el thruster (propulsión) si la nave está avanzando
        if self.moving_forward:
            thruster = pygame.transform.rotate(
                self.thruster_image, -self.angle)  # Rotar propulsión según ángulo
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
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y,
                         current_bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y,
                         bar_width, bar_height), 2)  # Borde blanco


class Asteroid(pygame.sprite.Sprite):
    """
    Clase para representar un asteroide en el juego.

    Atributos:
        position (Vector2): Posición del asteroide.
        velocity (Vector2): Velocidad y dirección del movimiento.
        random_numbers (list): Lista de números aleatorios validados.
        ready_to_spawn (bool): Indica si el asteroide está listo para aparecer.
        image (Surface): Imagen del asteroide.
        rect (Rect): Rectángulo de colisión del asteroide.
    """

    def __init__(self, pos=None, image=None):
        super().__init__()
        self.ready_to_spawn = False
        self.random_numbers = self.generate_valid_random_numbers()
        self.position = Vector2(pos or self.generate_random_position_on_edge())
        self.image = self.load_asteroid_image(image)
        self.velocity = self.generate_random_velocity()
        self.angle = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.rect = self.image.get_rect(center=self.position)

    # Generación y validación de números aleatorios
    def generate_valid_random_numbers(self):
        """Genera y valida una lista de números aleatorios."""
        tester = RandomTests()
        while True:
            generator = LinearCongruence(
                n=MAP_WIDTH, min_val=1, max_val=MAP_WIDTH)
            Ri, random_numbers = generator.generate()
            if tester.run_all_tests(Ri):
                return random_numbers
            print("Las pruebas fallaron, generando nuevos números...")

    def get_random_number(self, min_val, max_val):
        """Obtiene un número aleatorio validado dentro de un rango."""
        number = self.random_numbers[self.random_index]
        self.random_index = (self.random_index + 1) % len(self.random_numbers)
        return number % (max_val - min_val + 1) + min_val

    # Inicialización del asteroide
    def generate_random_position_on_edge(self):
        """Genera una posición aleatoria en los bordes del mapa."""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return self.get_random_number(0, MAP_WIDTH), 0
        elif side == 'bottom':
            return self.get_random_number(0, MAP_WIDTH), MAP_HEIGHT
        elif side == 'left':
            return 0, self.get_random_number(0, MAP_HEIGHT)
        elif side == 'right':
            return MAP_WIDTH, self.get_random_number(0, MAP_HEIGHT)

    def load_asteroid_image(self, image):
        """Carga y escala la imagen del asteroide."""
        image = image or pygame.image.load(
            'assets/images/asteroid.png').convert_alpha()
        scale = random.uniform(0.8, 1.0)
        return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

    def generate_random_velocity(self):
        """Genera una velocidad aleatoria para el asteroide."""
        return Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

    # Métodos de actualización
    def update(self, asteroid_group):
        """Actualiza la posición, rotación y verifica colisiones del asteroide."""
        if not self.ready_to_spawn:
            return

        # Movimiento y rotación
        self.position += self.velocity
        self.rect.center = self.position
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Teletransportarse a través de los bordes
        self.wrap_around_map()

    def wrap_around_map(self):
        """Permite que el asteroide reaparezca en el lado opuesto al salir del mapa."""
        if self.position.x < 0:
            self.position.x = MAP_WIDTH
        elif self.position.x > MAP_WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = MAP_HEIGHT
        elif self.position.y > MAP_HEIGHT:
            self.position.y = 0

    # Gestión de colisiones y fragmentación
    def handle_collisions(self, asteroid_group):
        """Gestiona las colisiones entre asteroides."""
        for asteroid in asteroid_group:
            if asteroid != self and pygame.sprite.collide_rect(self, asteroid):
                self.velocity *= -1
                asteroid.velocity *= -1

    def fragment(self, asteroid_group):
        """Fragmenta el asteroide en partes más pequeñas."""
        self.kill()  # Elimina el asteroide actual


class GlowWorm(pygame.sprite.Sprite):
    def __init__(self, pos, length=20, speed=1, color=(100, 255, 100)):
        super().__init__()
        self.segments = [pos]
        self.length = length
        self.speed = speed
        self.color = color
        self.health = 100

        # Generador de números pseudoaleatorios
        self.random_index = 0
        self.random_numbers = None  # Inicialmente no hay números generados
        self.steps = []
        self.step_counter = 0
        self.ready = False  # Indica si el objeto está listo

        # Dirección favorecida
        self.favored_direction = None

        # Generar números aleatorios de forma diferida
        self.generate_random_numbers()

        # Inicialización de la imagen y rectángulo
        self.image = pygame.Surface((25, 25)).convert_alpha()
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=pos)

    def generate_random_numbers(self):
        """Genera una lista de números aleatorios validados mediante pruebas."""
        num_iterations = 100
        min_val, max_val = 1, 4

        # Intentar hasta pasar las pruebas
        while not self.ready:
            generator = LinearCongruence(
                n=num_iterations, min_val=min_val, max_val=max_val)
            Ri, random_numbers = generator.generate()
            if RandomTests().run_all_tests(Ri):
                self.random_numbers = random_numbers
                self.steps = self.random_numbers
                self.ready = True
                self.favored_direction = self.get_direction_from_random()

    def get_random_number(self):
        """Obtiene un número aleatorio de la lista generada."""
        if not self.ready:
            return None
        random_num = self.random_numbers[self.random_index]
        self.random_index = (self.random_index + 1) % len(self.random_numbers)
        return random_num

    def get_direction_from_random(self):
        """Obtiene una dirección basada en los números aleatorios."""
        directions = ['up', 'down', 'left', 'right']
        random_index = self.get_random_number() % len(directions)
        return directions[int(random_index)]

    def update_favored_direction(self):
        """Actualiza la dirección favorecida usando números aleatorios."""
        if self.ready:
            self.favored_direction = self.get_direction_from_random()

    def update(self, keys, laser_group):
        """Actualiza la posición del GlowWorm."""
        if not self.ready:
            return

        step = self.steps[self.step_counter]
        self.step_counter = (self.step_counter + 1) % len(self.steps)

        if self.step_counter % 30 == 0:
            self.update_favored_direction()

        # Mover la cabeza
        head_x, head_y = self.segments[0]
        movement = {
            'up': lambda x, y: (x, y - self.speed),
            'down': lambda x, y: (x, y + self.speed),
            'left': lambda x, y: (x - self.speed, y),
            'right': lambda x, y: (x + self.speed, y),
        }
        head_x, head_y = movement[self.favored_direction](head_x, head_y)

        # Wraparound
        head_x %= MAP_WIDTH
        head_y %= MAP_HEIGHT

        self.segments.insert(0, (head_x, head_y))

        if len(self.segments) > self.length:
            self.segments.pop()

        self.rect.center = self.segments[0]

    def draw(self, screen, camera_x, camera_y):
        """Dibuja el GlowWorm en la pantalla."""
        if not self.ready:
            return
        for i, segment in enumerate(self.segments):
            x, y = segment
            radius = 5 + (len(self.segments) - i) * 2
            pygame.draw.circle(screen, self.color,
                               (x - camera_x, y - camera_y), radius)


class Kamikaze(pygame.sprite.Sprite):
    def __init__(self, pos, kamikaze_image, player):
        super().__init__()
        self.image = kamikaze_image
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)
        self.velocity = Vector2(0, 0)
        self.speed = 5
        self.player = player

    def update(self, keys, laser_group):
        """Actualiza la posición del Kamikaze."""
        direction = self.player.position - self.position
        direction.normalize_ip()
        self.velocity = direction * self.speed
        self.position += self.velocity

        # Wraparound
        if self.rect.right < 0:
            self.position.x = MAP_WIDTH
        elif self.rect.left > MAP_WIDTH:
            self.position.x = 0
        if self.rect.bottom < 0:
            self.position.y = MAP_HEIGHT
        elif self.rect.top > MAP_HEIGHT:
            self.position.y = 0

        self.rect.center = self.position

    def draw(self, screen, camera_x, camera_y):
        """Dibuja el Kamikaze en la pantalla."""
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
            self.position.x = self.player.position.x + \
                self.orbit_radius * math.cos(self.orbit_angle)
            self.position.y = self.player.position.y + \
                self.orbit_radius * math.sin(self.orbit_angle)

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
