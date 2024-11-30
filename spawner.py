import pygame
import random
from sprites import Asteroid, GlowWorm, Kamikaze, Pripyat
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, GLOWWORM, KAMIKAZE, PRIPYAT, ASTEROID
from test_nums.random_all_test import RandomTests
from generator_nums.linear_congruence import LinearCongruence


class Spawner:
    def __init__(self, iat_model):
        """
        Inicializa el sistema de spawn basado en un modelo de intervalos.
        :param iat_model: Lista con los intervalos de tiempo entre spawns en milisegundos.
        """
        self.iat_model = iat_model
        self.current_index = 0  # Índice actual del modelo
        self.last_spawn_time = pygame.time.get_ticks()

        # Generador de números pseudoaleatorios validados
        self.random_index = 0
        self.random_numbers = self._generate_valid_random_numbers(
            200, 1, MAP_WIDTH)

    def _generate_valid_random_numbers(self, num_iterations, min_val, max_val):
        """
        Genera una lista de números pseudoaleatorios validados.
        :param num_iterations: Número de iteraciones para generar números.
        :param min_val: Valor mínimo para los números.
        :param max_val: Valor máximo para los números.
        :return: Lista de números pseudoaleatorios validados.
        """
        tester = RandomTests()
        while True:
            generator = LinearCongruence(
                n=num_iterations, min_val=min_val, max_val=max_val)
            Ri, random_numbers = generator.generate()
            if tester.run_all_tests(Ri):
                return random_numbers
            print("Las pruebas en SPAWNER fallaron, generando nuevos números...")

    def get_random_number(self, min_val, max_val):
        """
        Obtiene un número pseudoaleatorio dentro del rango especificado,
        utilizando los números pre-generados.
        :param min_val: Valor mínimo.
        :param max_val: Valor máximo.
        :return: Número pseudoaleatorio dentro del rango.
        """
        random_value = self.random_numbers[self.random_index]
        self.random_index = (self.random_index + 1) % len(self.random_numbers)
        return min_val + (random_value % (max_val - min_val + 1))

    def _create_enemy(self, enemy_type, x, y, glowworm_group, kamikazes_group, pripyat_group, asteroid_group, all_sprites, player):
        """
        Crea y agrega un enemigo al grupo correspondiente.
        :param enemy_type: Tipo de enemigo ("glowworm", "kamikaze", "pripyat").
        :param x: Coordenada X del enemigo.
        :param y: Coordenada Y del enemigo.
        :param glowworm_group: Grupo de gusanos de luz.
        :param kamikazes_group: Grupo de kamikazes.
        :param pripyat_group: Grupo de pripyat.
        :param all_sprites: Grupo general de sprites.
        :param player: Referencia al jugador.
        """
        if enemy_type == GLOWWORM:
            glowworm = GlowWorm(pos=(x, y), length=25, color=(100, 255, 100))
            glowworm_group.add(glowworm)
            all_sprites.add(glowworm)
        elif enemy_type == KAMIKAZE:
            kamikaze = Kamikaze(
                pos=(x, y),
                kamikaze_image=pygame.image.load(
                    "assets/images/kamikaze.png").convert_alpha(),
                player=player
            )
            kamikazes_group.add(kamikaze)
            all_sprites.add(kamikaze)
        elif enemy_type == PRIPYAT:
            pripyat = Pripyat(
                pos=(x, y),
                pripyat_image=pygame.image.load(
                    "assets/images/pripyat.png").convert_alpha(),
                player=player,
                damage_sound_path="assets/sounds/raaa.wav"
            )
            pripyat_group.add(pripyat)
            all_sprites.add(pripyat)
        elif enemy_type == ASTEROID:
            # Generar un grupo de asteroides (ejemplo: entre 3 y 6)
            for _ in range(5):
                x = self.get_random_number(1, MAP_WIDTH)
                y = self.get_random_number(1, MAP_HEIGHT)
                asteroid = Asteroid(pos=(x, y))
                asteroid_group.add(asteroid)
                all_sprites.add(asteroid)

    def spawn(self, current_time, glowworm_group, kamikazes_group, pripyat_group, asteroid_group, all_sprites, player):
        """
        Genera un nuevo enemigo si se cumple el intervalo actual.
        :param current_time: Tiempo actual del juego.
        :param asteroid_group: Grupo de asteroides.
        :param glowworm_group: Grupo de gusanos de luz.
        :param kamikazes_group: Grupo de kamikazes.
        :param pripyat_group: Grupo de pripyat.
        :param all_sprites: Grupo general de sprites.
        :param player: Referencia al jugador.
        """
        if current_time - self.last_spawn_time >= self.iat_model[self.current_index]:
            # Seleccionar aleatoriamente un tipo de enemigo
            enemy_types = [ASTEROID, GLOWWORM, KAMIKAZE, PRIPYAT]
            random_index = self.get_random_number(0, len(enemy_types) - 1)
            enemy_type = enemy_types[int(random_index)]

            # Generar posición aleatoria fuera del rango visible de la cámara
            spawn_margin = 100  # Margen adicional fuera de la pantalla
            valid_spawn = False

            while not valid_spawn:
                x = self.get_random_number(1, MAP_WIDTH)
                y = self.get_random_number(1, MAP_HEIGHT)

                # Verificar si está fuera del rango de la cámara
                if (
                    x < player.rect.centerx - SCREEN_WIDTH // 2 - spawn_margin
                    or x > player.rect.centerx + SCREEN_WIDTH // 2 + spawn_margin
                    or y < player.rect.centery - SCREEN_HEIGHT // 2 - spawn_margin
                    or y > player.rect.centery + SCREEN_HEIGHT // 2 + spawn_margin
                ):
                    valid_spawn = True

            # Crear el enemigo correspondiente
            self._create_enemy(
                enemy_type, x, y, glowworm_group, kamikazes_group, pripyat_group, asteroid_group, all_sprites, player
            )

            # Actualizar el tiempo del último spawn y el índice del modelo
            self.last_spawn_time = current_time
            self.current_index = (self.current_index + 1) % len(self.iat_model)
