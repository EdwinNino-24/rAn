import numpy as np
from test_nums.chi_square import ChiSquareTest
from test_nums.kolmogorov_smirnov import KolmogorovSmirnovTest
from test_nums.variance import VarianceTest
from test_nums.poker import PokerTest


class RandomTests:

    def run_all_tests(self, random_numbers):
        """
        Runs all tests (mean, variance, and poker) on the random numbers.

        Args:
            random_numbers (list or np.array): List of random numbers to test.

        Returns:
            bool: True if all tests pass, False if any test fails.
        """
        # Run the chi square test
        chi_square_test = ChiSquareTest()
        chi_square_test_result = chi_square_test.run_test(random_numbers)

        # Run the ks test
        ks_test = KolmogorovSmirnovTest()
        ks_test_result = ks_test.run_test(random_numbers)

        # Run the mean test
        mean_test = ChiSquareTest()
        mean_test_result = mean_test.run_test(random_numbers)

        # Run the poker test
        poker_test = PokerTest()
        poker_test_result = poker_test.run_test(random_numbers)

        # Run the variance test
        variance_test = VarianceTest()
        variance_test_result = variance_test.run_test(random_numbers)

        # Return True if all tests pass, False if any fail
        return chi_square_test_result and ks_test_result and mean_test_result and variance_test_result and poker_test_result
