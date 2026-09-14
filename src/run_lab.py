"""Run from any directory: python path/to/src/run_lab.py."""
import argparse
import json
from pathlib import Path
from analysis import (additional_observations, category_profiles, category_values,
                      endpoint_summary, geographical_units, overall_house_value)
from load_and_inspect import DEFAULT_DATA, ROOT, inspect_housing, load_housing
from plots import plot_histograms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs')
    args = parser.parse_args()
    housing = load_housing(args.data)
    inspect_housing(housing)
    args.output.mkdir(parents=True, exist_ok=True)
    summary = {'question_1': geographical_units(housing),
               'question_2_mean_value': overall_house_value(housing),
               'question_10': additional_observations(housing)}
    print('\nQ1, Q2, Q10:\n', json.dumps(summary, indent=2))
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    for name, table in [('category_values', category_values(housing)),
                        ('category_profiles', category_profiles(housing)),
                        ('endpoints', endpoint_summary(housing))]:
        table.to_csv(args.output / f'{name}.csv', float_format='%.6f')
        print(f'\n{name}:\n{table.to_string(float_format=lambda x: f"{x:,.3f}")}')
    plot_histograms(housing, args.output / 'histograms.png')
    print(f'\nResults saved in {args.output.resolve()}')


if __name__ == '__main__':
    main()
