import numpy as np
from constants import ALPHA


class KolmogorovSmirnovTest:

    CRITICAL_VALUES = {
        1: 0.97500, 2: 0.84189, 3: 0.70760, 4: 0.62394, 5: 0.56328,
        6: 0.51926, 7: 0.48342, 8: 0.45427, 9: 0.43001, 10: 0.40925,
        11: 0.39122, 12: 0.37543, 13: 0.36143, 14: 0.34890, 15: 0.33750,
        16: 0.32733, 17: 0.31796, 18: 0.30936, 19: 0.30143, 20: 0.29408,
        21: 0.28724, 22: 0.28087, 23: 0.2749, 24: 0.26931, 25: 0.26404,
        26: 0.25908, 27: 0.25438, 28: 0.24993, 29: 0.24571, 30: 0.24170,
        31: 0.23788, 32: 0.23424, 33: 0.23076, 34: 0.22743, 35: 0.22425,
        36: 0.22119, 37: 0.21826, 38: 0.21544, 39: 0.21273, 40: 0.21012,
        41: 0.20760, 42: 0.20517, 43: 0.20283, 44: 0.20056, 45: 0.19837,
        46: 0.19625, 47: 0.19420, 48: 0.19221, 49: 0.19028, 50: 0.18841,
    }

    def run_test(self, random_numbers):
        """
        Perform the Kolmogorov-Smirnov goodness-of-fit test on the given random numbers.

        Parameters:
            random_numbers (list or numpy array): The sequence of random numbers to test.

        Returns:
            bool: True if the test is passed, False otherwise.
        """
        n = len(random_numbers)

        # Compute minimum and maximum values
        min_value = np.min(random_numbers)
        max_value = np.max(random_numbers)

        # Define the number of intervals (k) based on the square root of the sample size
        k = int(np.sqrt(n))

        # Create intervals
        intervals = np.linspace(min_value, max_value, k + 1)

        # Count observed frequencies in each interval
        observed_frequencies, _ = np.histogram(random_numbers, bins=intervals)

        # Calculate expected frequency per interval (assuming uniform distribution)
        expected_frequency = n / k

        # Compute cumulative frequencies
        observed_cumulative = np.cumsum(observed_frequencies)
        expected_cumulative = np.arange(1, k + 1) * expected_frequency

        # Compute cumulative probabilities
        observed_prob_cumulative = observed_cumulative / n
        expected_prob_cumulative = expected_cumulative / n

        # Calculate differences between observed and expected cumulative probabilities
        differences = np.abs(observed_prob_cumulative -
                             expected_prob_cumulative)

        # Find the maximum difference
        D_max = np.max(differences)

        # Determine the critical value
        if n > 50:
            D_critical = 1.36 / np.sqrt(n)
        else:
            D_critical = self.CRITICAL_VALUES.get(n, None)

        # Return True if the test is passed, False otherwise
        if D_critical is None:
            return False  # Test cannot be performed for this sample size
        return D_max <= D_critical
