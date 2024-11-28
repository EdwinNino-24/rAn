import numpy as np
from scipy.stats import norm
from constants import ALPHA


class MeanTest:
    @staticmethod
    def truncate(numbers, decimals):
        """
        Truncates the numbers to the specified number of decimal places.
        """
        factor = 10.0 ** decimals
        return np.trunc(numbers * factor) / factor

    def test_means(self, random_numbers):
        """
        Performs a means test on a set of random numbers.

        Args:
            random_numbers (array-like): The list of random numbers to test.
            alpha (float): The significance level. Default is 0.05.

        Returns:
            bool: True if the test is passed, False otherwise.
        """
        random_numbers = self.truncate(random_numbers, 5)
        n = len(random_numbers)
        expected_mean = 0.5
        R = np.mean(random_numbers)
        critical_value = 1 - (ALPHA / 2)
        Z = norm.ppf(critical_value)
        standard_error = 1 / (np.sqrt(12 * n))
        lower_limit = expected_mean - Z * standard_error
        upper_limit = expected_mean + Z * standard_error

        return lower_limit <= R <= upper_limit
