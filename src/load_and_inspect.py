"""Task 1: load data using a path relative to this file, not the terminal."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / 'data' / 'raw' / 'housing.csv'
NUMERIC_COLUMNS = ['longitude', 'latitude', 'housing_median_age', 'total_rooms',
                   'total_bedrooms', 'population', 'households', 'median_income',
                   'median_house_value']


def load_housing(path=DEFAULT_DATA):
    """Load district records; preserve missing bedrooms rather than invent values."""
    housing = pd.read_csv(path)
    required = NUMERIC_COLUMNS + ['ocean_proximity']
    missing = set(required) - set(housing.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    if housing.empty:
        raise ValueError('The housing dataset is empty.')
    for column in NUMERIC_COLUMNS:
        housing[column] = pd.to_numeric(housing[column], errors='raise')
    if housing[required].drop(columns='total_bedrooms').isna().any().any():
        raise ValueError('Unexpected missing data outside total_bedrooms.')
    if (housing['households'] <= 0).any():
        raise ValueError('Households must be positive for per-household ratios.')
    return housing


def inspect_housing(housing):
    """Display the first 11 rows as in the lab, schema, and missing counts."""
    print(housing.head(11).to_string(index=False))
    print(f'\nShape: {housing.shape}')
    housing.info()
    print('\nMissing values:\n', housing.isna().sum().to_string())


if __name__ == '__main__':
    inspect_housing(load_housing())
