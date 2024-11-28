import random


class LinearCongruence:
    """
    Genera números pseudoaleatorios utilizando el método de Congruencia Lineal.

    Args:
        xo (int): Valor inicial (semilla).
        n (int): Número de iteraciones (cantidad de números a generar).
        k (int): Parámetro k en la fórmula de congruencia lineal.
        c (int): Parámetro c en la fórmula de congruencia lineal.
        g (int): Parámetro g en la fórmula de congruencia lineal.
        min_val (float): Límite inferior del intervalo de mapeo.
        max_val (float): Límite superior del intervalo de mapeo.

    Methods:
        generate(): Genera una lista de números pseudoaleatorios.
    """

    def __init__(self, n, min_val, max_val):
        """
        Inicializa la clase LinearCongruence.

        Args:
            xo (int): Valor inicial.
            n (int): Número de iteraciones.
            min_val (float): Límite inferior del intervalo.
            max_val (float): Límite superior del intervalo.
        """
        self.xo = 1  # Almacena el valor inicial
        self.n = n  # Almacena el número de iteraciones
        self.k = random.randint(2, 4)  # Almacena el parámetro k
        self.c = random.randint(3, 7)  # Almacena el parámetro c
        self.g = random.randint(5, 10)  # Almacena el parámetro g
        self.min_val = min_val  # Almacena el límite inferior del intervalo
        self.max_val = max_val  # Almacena el límite superior del intervalo

    def generate(self):
        """
        Genera una lista de números pseudoaleatorios utilizando el método de Congruencia Lineal.

        Returns:
            list: Una lista de listas, donde cada sublista contiene el valor de xi, el número aleatorio generado (Ri) y el valor mapeado al intervalo [min_val, max_val] (Ni).
        """
        a = 1 + 2 * self.k  # Calcula el valor de 'a'
        m = 2 ** self.g  # Calcula el valor de 'm'
        Ri_list = []  # Lista de \( R_i \)
        Ni_list = []  # Lista de \( N_i \)
        xi = self.xo  # Inicializa xi con el valor inicial

        for _ in range(self.n):  # Itera el número de veces especificado
            # Aplica la fórmula de congruencia lineal para calcular el siguiente xi
            xi = (a * xi + self.c) % m
            Ri = xi / (m - 1)  # Normaliza xi al intervalo [0, 1)
            # Mapea Ri al intervalo [min_val, max_val]
            Ni = self.min_val + Ri * (self.max_val - self.min_val)
            Ri_list.append(round(Ri, 5))  # Agrega Ri
            Ni_list.append(round(Ni, 5))  # Agrega Ni

        return Ri_list, Ni_list  # Devuelve la lista de resultados
