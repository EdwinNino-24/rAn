import numpy as np
import matplotlib.pyplot as plt

class KamikazeModel:
    def __init__(self, initial_position, player_position, speed):
        self.position = np.array(initial_position, dtype=float)
        self.player_position = np.array(player_position, dtype=float)
        self.speed = speed

    def update(self):
        # Calcular dirección hacia el jugador
        direction = self.player_position - self.position
        if np.linalg.norm(direction) > 0:
            direction /= np.linalg.norm(direction)  # Normalizar dirección
        # Actualizar posición del kamikaze
        self.position += direction * self.speed

    def get_position(self):
        return self.position

# Configuración inicial
kamikaze = KamikazeModel(initial_position=(0, 0), player_position=(50, 50), speed=1)
positions = [kamikaze.get_position().copy()]

# Simulación del movimiento
for _ in range(100):
    kamikaze.update()
    positions.append(kamikaze.get_position().copy())

# Graficar resultados
positions = np.array(positions)
plt.plot(positions[:, 0], positions[:, 1], label="Trayectoria del Kamikaze")
plt.scatter([50], [50], color='red', label="Jugador")
plt.title("Simulación del Movimiento del Kamikaze")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid()
plt.show()



