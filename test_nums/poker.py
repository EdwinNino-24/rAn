import numpy as np
from collections import Counter
from scipy.stats import chi2


class PokerTest:
    def __init__(self):
        """
        Initializes the PokerTest class with the theoretical probabilities
        for each poker hand category.
        """
        self.probabilities = {
            'D': 0.3024,  # All different
            'O': 0.504,   # One pair
            'T': 0.108,   # Two pairs
            'K': 0.072,   # Three of a kind
            'F': 0.009,   # Full house
            'P': 0.0045,  # Four of a kind (Poker)
            'Q': 0.0001   # Five of a kind (Quintilla)
        }

    @staticmethod
    def categorize_number(number):
        """
        Categorizes a number based on the frequency of its first 5 decimal digits.

        Args:
            number (float): The random number to categorize.

        Returns:
            str: A single-character category (D, O, T, K, F, P, Q).
        """
        digits = list(str(number).split('.')[1][:5])
        counts = Counter(digits)
        occurrences = sorted(counts.values(), reverse=True)

        if occurrences == [5]:
            return 'Q'  # Quintilla
        elif occurrences == [4, 1]:
            return 'P'  # Four of a kind (Poker)
        elif occurrences == [3, 2]:
            return 'F'  # Full house
        elif occurrences == [3, 1, 1]:
            return 'K'  # Three of a kind
        elif occurrences == [2, 2, 1]:
            return 'T'  # Two pairs
        elif occurrences == [2, 1, 1, 1]:
            return 'O'  # One pair
        else:
            return 'D'  # All different

    def run_test(self, random_numbers):
        """
        Performs the Poker test on a set of random numbers.

        Args:
            random_numbers (array-like): The list of random numbers to test.

        Returns:
            bool: True if the test passes, False otherwise.
        """
        categories = [self.categorize_number(num) for num in random_numbers]

        n = len(random_numbers)
        types = ['D', 'O', 'T', 'K', 'F', 'P', 'Q']
        observed_frequencies = []
        expected_frequencies = []
        chi2_values = []

        for category in types:
            observed = categories.count(category)
            theoretical_probability = self.probabilities[category]
            expected = theoretical_probability * n
            chi2_value = ((expected - observed) ** 2) / \
                expected if expected != 0 else 0

            observed_frequencies.append(observed)
            expected_frequencies.append(expected)
            chi2_values.append(chi2_value)

        total_chi2 = np.sum(chi2_values)
        degrees_of_freedom = len(types) - 1
        critical_value = chi2.ppf(0.95, degrees_of_freedom)

        return total_chi2 < critical_value
