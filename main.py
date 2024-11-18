import pygame
from spawner import Spawner
from sprites import PlayerShip, Asteroid, Laser, GlowWorm, Kamikaze
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT
import random


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Cargar imágenes y sonidos
    ship_image = pygame.image.load('assets/images/ship.png').convert_alpha()
    thruster_image = pygame.image.load('assets/images/thruster.png').convert_alpha()
    laser_image = pygame.image.load('assets/images/laser.png').convert_alpha()
    background_image = pygame.image.load('assets/images/background1.jpg').convert()
    background_image = pygame.transform.scale(background_image, (MAP_WIDTH, MAP_HEIGHT))
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
    iat_model = [2000, 1500, 2500, 1000, 3000]  # Intervalos de spawn en milisegundos
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
        spawner.spawn(current_time, asteroids_group, glowworms_group, kamikazes_group, pripyats_group, all_sprites, player)

        # Definir la cámara (posición centrada en el jugador)
        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, MAP_WIDTH - SCREEN_WIDTH))
        camera_y = max(0, min(player.rect.centery - SCREEN_HEIGHT // 2, MAP_HEIGHT - SCREEN_HEIGHT))

        # Dibujar el fondo del mapa
        screen.blit(background_image, (-camera_x, -camera_y))

        # Efecto de teletransportación
        if is_teleporting:
            pygame.draw.circle(screen, flash_color, player.rect.center, flash_radius)
            flash_radius += flash_speed
            if flash_radius > flash_max_radius:
                flash_radius = 0
                is_teleporting = False
                player.pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Posición final

        # Dibujar al jugador (solo si no se está teletransportando)
        if not is_teleporting:
            player.draw(screen, camera_x, camera_y)

        player.draw_health_bar(screen)

        # Dibujar los lasers ajustando la cámara
        for laser in laser_group:
            screen.blit(laser.image, apply_camera(laser, camera_x, camera_y))

        # Colisiones entre asteroides y lasers
        collisions = pygame.sprite.groupcollide(asteroids_group, laser_group, True, True)
        for asteroid, laser in collisions.items():
            asteroid.fragment(asteroids_group)  # Fragmentar el asteroide al ser destruido

        # Dibujar los gusanos de luz
        for glowworm in glowworms_group:
            glowworm.draw(screen, camera_x, camera_y)
            
        # Colisiones entre el jugador y los gusanos de luz
        if pygame.sprite.spritecollide(player, glowworms_group, False):
            collision_sound.play()  
            player.health -= random.randint(1, 3)  
            if player.health <= 0:
                # El jugador ha muerto
                print("¡Has muerto!")
                running = False
                
        # Colisiones entre gusanos de luz y láseres
        collisions = pygame.sprite.groupcollide(glowworms_group, laser_group, False, True)
        for glowworm, lasers in collisions.items():
            for laser in lasers:
                glowworm.health -= laser.damage  # Reduce la vida del gusano (asumiendo que Laser tiene un atributo damage)
                if glowworm.health <= 0:
                    glowworm.kill()  # Destruir el gusano si su vida llega a cero
        
        
        # Dibujar los kamikazes ajustando la cámara
        for kamikaze in kamikazes_group:
            kamikaze.draw(screen, camera_x, camera_y)  
            
        # Colisiones entre el jugador y los gusanos de luz
        if pygame.sprite.spritecollide(player, kamikazes_group, True):
            collision_sound.play()  
            player.health -= 20
            if player.health <= 0:
                # El jugador ha muerto
                print("¡Has muerto!")
                running = False
                
        # Colisiones entre gusanos de luz y láseres
        collisions = pygame.sprite.groupcollide(kamikazes_group, laser_group, False, True)
        for kamikaze, lasers in collisions.items():
            for laser in lasers:
                kamikaze.kill()  


        # Dibujar los kamikazes ajustando la cámara
        for pripyat in pripyats_group:
            pripyat.draw(screen, camera_x, camera_y)  
            
       


        # Calcular y mostrar FPS
        fps = str(int(clock.get_fps()))
        fps_text = font.render(f"{fps}", True, (255, 255, 255))  # Color blanco
        screen.blit(fps_text, (1885, 10))  # Posición del indicador de FPS

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
