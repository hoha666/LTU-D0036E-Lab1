"""Task 2 functions. Mean, median, and correlation are implemented explicitly."""
import math
import pandas as pd


def clean_numbers(values):
    """Exclude missing observations, not zeros; reject empty or infinite input."""
    numbers = [float(value) for value in values if pd.notna(value)]
    if not numbers or not all(math.isfinite(value) for value in numbers):
        raise ValueError('Statistics require at least one finite, non-missing value.')
    return numbers


def mean(values):
    """Sum the observations and divide by the number of observations."""
    numbers = clean_numbers(values)
    return sum(numbers) / len(numbers)


def median(values):
    """Sort; select the middle or average the two middle observations."""
    numbers = sorted(clean_numbers(values))
    middle = len(numbers) // 2
    if len(numbers) % 2:
        return numbers[middle]
    return (numbers[middle - 1] + numbers[middle]) / 2


def geographical_units(housing):
    """Q1: districts are rows; coordinate pairs need not identify districts."""
    return {'districts': len(housing),
            'unique_coordinate_pairs': len(housing[['longitude', 'latitude']].drop_duplicates()),
            'duplicate_rows': int(housing.duplicated().sum())}


def overall_house_value(housing):
    """Q2: equally weight districts, not the five category means."""
    return mean(housing['median_house_value'])


def category_values(housing):
    """Q3-4: mean and median of district median house values."""
    rows = []
    for category, group in housing.groupby('ocean_proximity', sort=True):
        average = mean(group['median_house_value'])
        middle = median(group['median_house_value'])
        rows.append({'ocean_proximity': category, 'districts': len(group),
                     'mean_value': average, 'median_value': middle,
                     'mean_minus_median': average - middle})
    return pd.DataFrame(rows).set_index('ocean_proximity')


def add_ratios(housing):
    """Derive ratios on a copy so raw data stays unchanged."""
    result = housing.copy()
    for source, target in [('total_rooms', 'rooms_per_household'),
                           ('total_bedrooms', 'bedrooms_per_household'),
                           ('population', 'people_per_household')]:
        result[target] = result[source] / result['households']
    return result


def category_profiles(housing):
    """Q7-9: explicitly named means, medians, totals, and pooled ratios."""
    rows = []
    features = ['housing_median_age', 'total_rooms', 'rooms_per_household',
                'bedrooms_per_household', 'population', 'households',
                'median_income', 'people_per_household']
    for category, group in add_ratios(housing).groupby('ocean_proximity', sort=True):
        row = {'ocean_proximity': category, 'districts': len(group)}
        for feature in features:
            row[f'mean_{feature}'] = mean(group[feature])
            row[f'median_{feature}'] = median(group[feature])
        # A ratio of sums weights districts by household count.
        row['pooled_rooms_per_household'] = sum(group['total_rooms']) / sum(group['households'])
        row['pooled_people_per_household'] = sum(group['population']) / sum(group['households'])
        row['total_population'] = sum(group['population'])
        row['total_households'] = sum(group['households'])
        rows.append(row)
    return pd.DataFrame(rows).set_index('ocean_proximity')


def endpoint_summary(housing):
    """Q6: measure exact maxima as evidence of possible upper censoring."""
    rows = []
    for column in ['housing_median_age', 'median_house_value']:
        maximum = max(housing[column])
        count = int((housing[column] == maximum).sum())
        rows.append({'feature': column, 'maximum': maximum,
                     'count_at_maximum': count, 'percent_at_maximum': 100 * count / len(housing)})
    return pd.DataFrame(rows).set_index('feature')


def pearson_correlation(x, y):
    """Q10: linear association using paired, non-missing observations."""
    if len(x) != len(y):
        raise ValueError('Paired inputs must have equal lengths.')
    pairs = [(a, b) for a, b in zip(x, y) if pd.notna(a) and pd.notna(b)]
    xs, ys = zip(*pairs) if pairs else ([], [])
    mx, my = mean(xs), mean(ys)
    numerator = sum((a - mx) * (b - my) for a, b in pairs)
    denominator = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    if denominator == 0:
        raise ValueError('Correlation is undefined for a constant variable.')
    return numerator / denominator


def additional_observations(housing):
    """Q10: missingness, income association, and ratio outliers."""
    enriched = add_ratios(housing)
    return {'missing_bedrooms': int(housing['total_bedrooms'].isna().sum()),
            'missing_bedrooms_percent': float(100 * housing['total_bedrooms'].isna().sum() / len(housing)),
            'income_value_correlation': pearson_correlation(housing['median_income'], housing['median_house_value']),
            'maximum_rooms_per_household': max(enriched['rooms_per_household']),
            'maximum_people_per_household': max(enriched['people_per_household'])}
