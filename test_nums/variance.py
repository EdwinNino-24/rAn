import numpy as np
from scipy.stats import chi2
from constants import ALPHA


class VarianceTest:

    def run_test(self, random_numbers):
        """
        Performs the variance test on a set of random numbers.

        Args:
            random_numbers (array-like): The list of random numbers to test.

        Returns:
            bool: True if the variance is within the expected range, False otherwise.
        """
        n = len(random_numbers)
        sample_variance = np.var(random_numbers, ddof=1)  # Sample variance
        chi2_lower = chi2.ppf(ALPHA / 2, n - 1)
        chi2_upper = chi2.ppf(1 - ALPHA / 2, n - 1)
        lower_limit = chi2_lower / (12 * (n - 1))
        upper_limit = chi2_upper / (12 * (n - 1))

        return lower_limit <= sample_variance <= upper_limit
