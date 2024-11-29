from constants import NO_POWER, DOUBLE_SHOT, INCREASE_SCORE, INCREASE_LIFE, RAPID_FIRE, DOUBLE, FAST, NORMAL


class PowerManager:
    def __init__(self, random_numbers):
        """
        Inicializa el administrador de poderes con números pseudoaleatorios pre-generados.
        :param random_numbers: Lista de números aleatorios pre-generados.
        """
        self.states = [NO_POWER, DOUBLE_SHOT,
                       INCREASE_SCORE, RAPID_FIRE, INCREASE_LIFE]
        self.current_power = NO_POWER
        self.transition_matrix = {
            NO_POWER: [0.3, 0.2, 0.3, 0.1, 0.1],
            DOUBLE_SHOT: [0.5, 0.0, 0.2, 0.1, 0.2],
            INCREASE_SCORE: [0.6, 0.0, 0.2, 0.1, 0.2],
            RAPID_FIRE: [0.25, 0.2, 0.4, 0.0, 0.15],
            INCREASE_LIFE: [0.3, 0.2, 0.25, 0.05, 0.2]
        }
        self.random_numbers = random_numbers
        self.random_index = 0

    def get_next_power(self):
        """
        Determina el siguiente estado de poder utilizando un número aleatorio entero.
        """
        if not self.random_numbers:
            raise ValueError("La lista de números aleatorios está vacía.")

        # Tomar el siguiente número y ajustar el índice
        random_value = self.random_numbers[self.random_index]
        self.random_index = (self.random_index + 1) % len(self.random_numbers)

        # Obtener las probabilidades del estado actual
        probabilities = self.transition_matrix[self.current_power]
        cumulative_prob = 0

        # Convertir el número aleatorio en un rango manejable
        normalized_value = random_value % 100 / 100  # Normalizar entre 0 y 1

        # Determinar el próximo estado basado en las probabilidades
        for i, prob in enumerate(probabilities):
            cumulative_prob += prob
            if normalized_value <= cumulative_prob:
                self.current_power = self.states[i]
                break

        return self.current_power

    def apply_power(self, player):
        """
        Aplica el poder actual al jugador o al sistema de puntajes.
        """
        if self.current_power == DOUBLE_SHOT:
            player.shoot_mode = DOUBLE
        elif self.current_power == INCREASE_SCORE:
            player.shoot_mode = NORMAL
            player.score += 20
        elif self.current_power == RAPID_FIRE:
            player.shoot_mode = FAST
        elif self.current_power == INCREASE_LIFE:
            player.shoot_mode = NORMAL
            player.health += 20
