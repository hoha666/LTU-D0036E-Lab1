"""Q5: generate histograms without needing a graphical desktop."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


def plot_histograms(housing, output_path):
    features = [
        ('households', 'Households per district', 'Number of households'),
        ('median_income', 'District median income', 'Income (dataset units)'),
        ('housing_median_age', 'District median housing age', 'Age (years)'),
        ('median_house_value', 'District median house value', 'House value (dollars)'),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for ax, (column, title, label) in zip(axes.flat, features):
        # One bin per integer year preserves the endpoint spike at age 52.
        bins = [x - 0.5 for x in range(1, 54)] if column == 'housing_median_age' else 50
        ax.hist(housing[column].dropna(), bins=bins, color='#256e91', edgecolor='white', linewidth=0.4)
        ax.set(title=title, xlabel=label, ylabel='Number of districts')
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.grid(axis='y', alpha=0.2)
        if column in {'housing_median_age', 'median_house_value'}:
            maximum = housing[column].max()
            ax.axvline(maximum, color='#b74632', linestyle='--', label=f'Maximum: {maximum:,.0f}')
            ax.legend(fontsize=9)
    fig.suptitle('Housing districts: distributions of four features', fontsize=16)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path
