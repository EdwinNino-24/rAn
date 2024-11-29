import pygame
from spawner import Spawner
from sprites import PlayerShip, Asteroid, Laser, GlowWorm, Kamikaze
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
from test_nums.random_all_test import RandomTests
from generator_nums.linear_congruence import LinearCongruence
from power_manager import PowerManager


def calculate_health_reduction(value):
    """Calcula la reducción de salud según el valor aleatorio."""
    if 0 <= value < MAP_WIDTH / 3:
        return 2
    elif MAP_WIDTH / 3 <= value < (MAP_WIDTH / 3) * 2:
        return 3
    else:
        return 4


def calculate_health_reduction_mild(value):
    """Calcula la reducción de salud según el valor aleatorio."""
    if 0 <= value < MAP_WIDTH / 6:
        return 1
    elif MAP_WIDTH / 6 <= value < (MAP_WIDTH / 6) * 2:
        return 2
    else:
        return 3


def generate_random_nums():
    # Configurar el generador validado
    num_iterations = 200
    min_val, max_val = 1, MAP_WIDTH  # Rango para los números pseudoaleatorios

    # Inicializar el tester
    tester = RandomTests()

    # Generar y validar números aleatorios
    result_test = False  # Inicializar como False para entrar en el bucle
    while not result_test:
        generator = LinearCongruence(
            n=num_iterations, min_val=min_val, max_val=max_val)
        Ri, random_numbers = generator.generate()
        result_test = tester.run_all_tests(Ri)  # Ejecutar las pruebas
        if tester.run_all_tests(Ri):
            return random_numbers

        print("Las pruebas en MAIN fallaron, generando nuevos números...")


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    random_numbers = generate_random_nums()
    power_manager = PowerManager(random_numbers)

    # Cargar imágenes y sonidos
    ship_image = pygame.image.load('assets/images/ship.png').convert_alpha()
    thruster_image = pygame.image.load(
        'assets/images/thruster.png').convert_alpha()
    laser_image = pygame.image.load('assets/images/laser.png').convert_alpha()
    background_image = pygame.image.load(
        'assets/images/background1.jpg').convert()
    background_image = pygame.transform.scale(
        background_image, (MAP_WIDTH, MAP_HEIGHT))
    shoot_sound = pygame.mixer.Sound('assets/sounds/shoot.wav')

    collision_sound = pygame.mixer.Sound('assets/sounds/collision_warm.wav')

    # Crear la nave del jugador
    player = PlayerShip(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                        ship_image=ship_image,
                        thruster_image=thruster_image,
                        laser_image=laser_image,
                        shoot_sound=shoot_sound)

    # Grupos de sprites
    all_sprites = pygame.sprite.Group(player)
    laser_group = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group()
    glowworms_group = pygame.sprite.Group()
    kamikazes_group = pygame.sprite.Group()
    pripyats_group = pygame.sprite.Group()

    # Configuración del sistema de spawn
    # Intervalos de spawn en milisegundos
    iat_model = [2000, 1500, 2500, 1000, 3000]
    spawner = Spawner(iat_model)

    # Variables para la cámara y efectos
    is_teleporting = True
    flash_color = (255, 255, 255)
    flash_radius = 0
    flash_speed = 5
    flash_max_radius = 400

    # Función para manejar la cámara
    def apply_camera(sprite, camera_x, camera_y):
        return sprite.rect.move(-camera_x, -camera_y)

    font = pygame.font.Font(None, 30)
    running = True
    random_index = 0
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Obtener las teclas presionadas
        keys = pygame.key.get_pressed()

        # Actualizar sprites
        all_sprites.update(keys, laser_group)
        laser_group.update()

        # Spawnear enemigos dinámicamente
        spawner.spawn(current_time, asteroids_group, glowworms_group,
                      kamikazes_group, pripyats_group, all_sprites, player)

        # Definir la cámara (posición centrada en el jugador)
        camera_x = max(0, min(player.rect.centerx -
                       SCREEN_WIDTH // 2, MAP_WIDTH - SCREEN_WIDTH))
        camera_y = max(0, min(player.rect.centery -
                       SCREEN_HEIGHT // 2, MAP_HEIGHT - SCREEN_HEIGHT))

        # Dibujar el fondo del mapa
        screen.blit(background_image, (-camera_x, -camera_y))

        # Efecto de teletransportación
        if is_teleporting:
            pygame.draw.circle(screen, flash_color,
                               player.rect.center, flash_radius)
            flash_radius += flash_speed
            if flash_radius > flash_max_radius:
                flash_radius = 0
                is_teleporting = False
                player.pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT //
                              2)  # Posición final

        # Dibujar al jugador (solo si no se está teletransportando)
        if not is_teleporting:
            player.draw(screen, camera_x, camera_y)

        player.draw_health_bar(screen)

        # Dibujar los lasers ajustando la cámara
        for laser in laser_group:
            screen.blit(laser.image, apply_camera(laser, camera_x, camera_y))

        # Colisiones entre asteroides y lasers
        collisions = pygame.sprite.groupcollide(
            asteroids_group, laser_group, True, True)
        for asteroid, laser in collisions.items():
            # Fragmentar el asteroide al ser destruido
            asteroid.fragment(asteroids_group)

        # Dibujar los gusanos de luz
        for glowworm in glowworms_group:
            glowworm.draw(screen, camera_x, camera_y)

        # Colisiones entre el jugador y los gusanos de luz
        if pygame.sprite.spritecollide(player, glowworms_group, False):
            collision_sound.play()
            # Usar un número aleatorio de la lista
            if random_index < len(random_numbers):
                random_value = random_numbers[random_index]
                random_index += 1
            else:
                random_value = 1

            reduction = calculate_health_reduction(random_value)
            player.health -= reduction

            if player.health <= 0:
                print("¡Has muerto!")
                running = False

        # Colisiones entre gusanos de luz y láseres
        collisions = pygame.sprite.groupcollide(
            glowworms_group, laser_group, False, True)
        for glowworm, lasers in collisions.items():
            for laser in lasers:
                # Reduce la vida del gusano (asumiendo que Laser tiene un atributo damage)
                glowworm.health -= laser.damage
                if glowworm.health <= 0:
                    glowworm.kill()  # Destruir el gusano si su vida llega a cero
                    player.score += 15
                    next_power = power_manager.get_next_power()
                    print(f"Nuevo poder obtenido: {next_power}")
                    power_manager.apply_power(player)

        # Dibujar los kamikazes ajustando la cámara
        for kamikaze in kamikazes_group:
            kamikaze.draw(screen, camera_x, camera_y)

        # Colisiones entre el jugador y los gusanos de luz
        if pygame.sprite.spritecollide(player, kamikazes_group, True):
            collision_sound.play()
            # Usar un número aleatorio de la lista
            if random_index < len(random_numbers):
                random_value = random_numbers[random_index]
                random_index += 1
            else:
                random_value = 0  # Default si se agotan los números

            reduction = calculate_health_reduction_mild(random_value)
            player.health -= reduction

            if player.health <= 0:
                print("¡Has muerto!")
                running = False

        # Colisiones entre gusanos de luz y láseres
        collisions = pygame.sprite.groupcollide(
            kamikazes_group, laser_group, False, True)
        for kamikaze, lasers in collisions.items():
            for laser in lasers:
                kamikaze.kill()
                player.score += 10
                next_power = power_manager.get_next_power()
                print(f"Nuevo poder obtenido: {next_power}")
                power_manager.apply_power(player)

        # Dibujar los kamikazes ajustando la cámara
        for pripyat in pripyats_group:
            pripyat.draw(screen, camera_x, camera_y) 

        # Mostrar puntaje en la parte superior derecha 
        score_text = font.render(
            f"Puntaje: {player.score}", True, (255, 255, 255))
        # Ajustar posición según el diseño
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Calcular y mostrar FPS
        fps = str(int(clock.get_fps()))
        fps_text = font.render(f"{fps}", True, (255, 255, 255))  # Color blanco
        screen.blit(fps_text, (1885, 10))  # Posición del indicador de FPS

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
