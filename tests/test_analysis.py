"""Check statistical edge cases and independently verify real-data calculations."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from analysis import (mean, median, pearson_correlation, category_values,
                      category_profiles, add_ratios, geographical_units, overall_house_value)
from load_and_inspect import load_housing


class StatisticsTests(unittest.TestCase):
    def test_mean_missing_and_zero(self):
        self.assertEqual(mean([0, 2, None, float('nan'), 4]), 2)

    def test_median_odd_even_unsorted(self):
        self.assertEqual(median([9, 1, 3]), 3)
        self.assertEqual(median([9, 1, 3, 7]), 5)
        self.assertEqual(median([None, 8]), 8)

    def test_undefined_statistics(self):
        for function in [mean, median]:
            for values in [[], [None], [float('inf')]]:
                with self.assertRaises(ValueError):
                    function(values)
        with self.assertRaises(ValueError):
            pearson_correlation([1, 1], [2, 3])
        with self.assertRaises(ValueError):
            pearson_correlation([1], [2, 3])

    def test_correlation_pairwise_missing(self):
        self.assertAlmostEqual(pearson_correlation([1, None, 3], [6, 5, 2]), -1)

    def test_real_dataset_against_pandas(self):
        housing = load_housing()
        self.assertEqual(geographical_units(housing)['districts'], 20640)
        self.assertEqual(geographical_units(housing)['unique_coordinate_pairs'], 12590)
        self.assertAlmostEqual(overall_house_value(housing), housing.median_house_value.mean())
        result = category_values(housing)
        expected = housing.groupby('ocean_proximity').median_house_value.agg(['mean', 'median'])
        for category in expected.index:
            self.assertAlmostEqual(result.loc[category, 'mean_value'], expected.loc[category, 'mean'])
            self.assertAlmostEqual(result.loc[category, 'median_value'], expected.loc[category, 'median'])
        self.assertAlmostEqual(pearson_correlation(housing.median_income, housing.median_house_value),
                               housing.median_income.corr(housing.median_house_value))

    def test_ratios_and_profiles_without_mutation(self):
        housing = load_housing()
        original = housing.copy(deep=True)
        ratios = add_ratios(housing)
        self.assertAlmostEqual(ratios.iloc[0].rooms_per_household, 880 / 126)
        self.assertEqual(ratios.bedrooms_per_household.isna().sum(), 207)
        profiles = category_profiles(housing)
        for category, group in ratios.groupby('ocean_proximity'):
            self.assertAlmostEqual(profiles.loc[category, 'mean_rooms_per_household'], group.rooms_per_household.mean())
            self.assertAlmostEqual(profiles.loc[category, 'median_rooms_per_household'], group.rooms_per_household.median())
            self.assertAlmostEqual(profiles.loc[category, 'mean_bedrooms_per_household'], group.bedrooms_per_household.mean())
        pd.testing.assert_frame_equal(housing, original)


if __name__ == '__main__':
    unittest.main()
