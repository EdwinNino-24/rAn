import pygame
import random
from sprites import Asteroid, GlowWorm, Kamikaze, Pripyat

class Spawner:
    def __init__(self, iat_model):
        """
        Inicializa el sistema de spawn basado en un modelo de intervalos.
        :param iat_model: Lista con los intervalos de tiempo entre spawns en milisegundos.
        """
        self.iat_model = iat_model
        self.current_index = 0  # Índice actual del modelo
        self.last_spawn_time = pygame.time.get_ticks()

    def spawn(self, current_time, asteroid_group, glowworm_group, kamikazes_group, pripyat_group, all_sprites, player):
        """
        Genera un nuevo enemigo si se cumple el intervalo actual.
        :param current_time: Tiempo actual del juego.
        :param asteroid_group: Grupo de asteroides.
        :param glowworm_group: Grupo de gusanos de luz.
        :param all_sprites: Grupo general de sprites.
        """
        # Si se cumple el intervalo definido por el modelo
        if current_time - self.last_spawn_time >= self.iat_model[self.current_index]:
            # Escoger aleatoriamente un tipo de enemigo
            enemy_type = random.choice(["pripyat"])
            if enemy_type == "glowworm":
                x = random.randint(0, 4096)
                y = random.randint(0, 4096)
                glowworm = GlowWorm(pos=(x, y), length=25, speed=25, color=(100, 255, 100))
                glowworm_group.add(glowworm)
                all_sprites.add(glowworm)
            elif enemy_type == "kamikaze":
                x = random.randint(0, 4096)
                y = random.randint(0, 4096)
                kamikaze = Kamikaze(
                    pos=(x, y), 
                    kamikaze_image=pygame.image.load('assets/images/kamikaze.png').convert_alpha(),  # Usa la imagen guardada
                    player=player  # Pasa la referencia al jugador
                )
                kamikazes_group.add(kamikaze)
                all_sprites.add(kamikaze)
            elif enemy_type == "pripyat":
                x = random.randint(0, 4096)
                y = random.randint(0, 4096)
                pripyat = Pripyat(pos=(x, y), pripyat_image=pygame.image.load('assets/images/pripyat.png').convert_alpha(), player=player)
                pripyat_group.add(pripyat)
                all_sprites.add(pripyat)

            # Actualizar el tiempo del último spawn
            self.last_spawn_time = current_time

            # Avanzar al siguiente intervalo en el modelo
            self.current_index = (self.current_index + 1) % len(self.iat_model)
