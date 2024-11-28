import numpy as np
from scipy.stats import chi2
from constants import ALPHA


class ChiSquareTest:
    def run_test(self, random_numbers):
        """
        Perform the Chi-Square goodness-of-fit test on the given random numbers.

        Parameters:
            random_numbers (list or numpy array): The sequence of random numbers to test.

        Returns:
            bool: True if the null hypothesis is not rejected (passes the test),
                  False otherwise.
        """
        n = len(random_numbers)

        # Define the number of intervals (k) as the square root of the sample size
        k = int(np.sqrt(n))

        # Expected frequency per interval
        expected_frequency = n / k

        # Create intervals for the random numbers
        intervals = np.linspace(np.min(random_numbers),
                                np.max(random_numbers), k + 1)

        # Calculate observed frequencies
        observed_frequencies, _ = np.histogram(random_numbers, bins=intervals)

        # Calculate Chi-Square statistic for each interval
        chi2_per_interval = (observed_frequencies -
                             expected_frequency) ** 2 / expected_frequency

        # Calculate the total Chi-Square value
        chi2_total = np.sum(chi2_per_interval)

        # Degrees of freedom (k - 1)
        degrees_of_freedom = k - 1

        # Critical Chi-Square value
        chi2_critical = chi2.ppf(1 - ALPHA, df=degrees_of_freedom)

        # Test result
        result = chi2_total <= chi2_critical
        return result
