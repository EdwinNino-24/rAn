import random
import matplotlib.pyplot as plt

# Generador de congruencia lineal
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
        xn = self.xo
        for _ in range(self.n):
            xn = ((self.k * xn) + self.c) % 2**self.g
            rn = xn / (2**self.g - 1)  # Normalizar a [0, 1)
            scaled_rn = self.min_val + (self.max_val - self.min_val) * rn
            yield scaled_rn

# Caminata aleatoria del gusano de luz
class GlowWormModel:
    def __init__(self, pos, length=25, speed=25, map_width=200, map_height=200):
        self.segments = [pos]
        self.length = length
        self.speed = speed
        self.map_width = map_width
        self.map_height = map_height
        self.favored_direction = random.choice(['up', 'down', 'left', 'right'])
        self.generator = LinearCongruence(
            xo=random.randint(1, 100), n=1000, k=7, c=3, g=10, min_val=0, max_val=4
        )
        self.steps = list(self.generator.generate())
        self.step_counter = 0

    def update(self):
        if self.step_counter % 30 == 0:
            self.favored_direction = random.choice(['up', 'down', 'left', 'right'])
        
        step = self.steps[self.step_counter]
        self.step_counter = (self.step_counter + 1) % len(self.steps)
        
        head_x, head_y = self.segments[0]
        if self.favored_direction == 'up' and step <= 2:
            head_y -= self.speed
        elif self.favored_direction == 'down' and step <= 2:
            head_y += self.speed
        elif self.favored_direction == 'left' and step <= 2:
            head_x -= self.speed
        elif self.favored_direction == 'right' and step <= 2:
            head_x += self.speed

        head_x %= self.map_width
        head_y %= self.map_height
        self.segments.insert(0, (head_x, head_y))
        if len(self.segments) > self.length:
            self.segments.pop()

# Simulación
worm = GlowWormModel(pos=(100, 100), length=25, speed=5)
positions = []
for _ in range(200):
    worm.update()
    positions.append(worm.segments[0])

positions = list(zip(*positions))
plt.plot(positions[0], positions[1], color='green', label="Trayectoria del GlowWorm")
plt.title("Simulación con Método de Congruencia Lineal")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid()
plt.show()
