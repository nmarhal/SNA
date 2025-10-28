import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

class MetricsProgressionPlotter:
    def __init__(self, metrics_name: str, section_type: str, folder_name: str, top_n: int = 5, ):
        self.metrics_name = metrics_name
        self.section_type = section_type
        self.top_n = top_n
        self.data_points = []
        self.keys_in_top_n = set()
        self.folder_name = folder_name
        self.colors = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
            "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
            "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
        ]

    def add_data_point(self, key_value_items: dict):
        self.data_points.append(key_value_items)

        top_keys = self._get_top_n_keys(key_value_items, self.top_n)
        self.keys_in_top_n.update(top_keys)

    def add_data_point_with_kwargs(self, **key_value_items):
        self.data_points.append(key_value_items)

        top_keys = self._get_top_n_keys(key_value_items, self.top_n)
        self.keys_in_top_n.update(top_keys)

    def draw(self, key_filter: list[str] = None, trend_lines: list[str] = None, save_plot: bool = True):
        if not self.data_points:
            return

        figure, axis = plt.subplots(figsize=(12, 6))
        sections = list(range(1, len(self.data_points) + 1))

        key_list = self._filter_keys(key_filter)
        if not key_list:
            return

        keys_with_trends = set()
        if trend_lines:
            keys_with_trends = {char.lower() for char in trend_lines
                                if char.lower() in self.keys_in_top_n}

        for index, key in enumerate(key_list):
            color = self.colors[index % len(self.colors)]
            scores = self._get_key_scores(key)

            self._plot_key_line(axis, sections, key, color, scores)

            if key.lower() in keys_with_trends:
                self._plot_trend_line(axis, sections, scores, color)

        self._configure_axes(axis)
        plt.tight_layout()

        if save_plot:
            self._save_plot(figure, key_filter=key_filter)
        else:
            plt.show()

    def _filter_keys(self, key_filter: list[str] = None) -> list[str]:
        if key_filter:
            filtered = [key for key in key_filter if key.lower() in self.keys_in_top_n]
            return sorted(filtered)
        return sorted(self.keys_in_top_n)

    def _get_top_n_keys(self, key_centralities: dict, top_n: int) -> list[str]:
        sorted_keys = sorted(key_centralities.items(), 
                                  key=lambda item: item[1], 
                                  reverse=True)
        return [key for key, score in sorted_keys[:top_n]]

    def _get_key_scores(self, key: str) -> list[float]:
        scores = []
        for data_point in self.data_points:
            scores.append(data_point.get(key, 0))
        return scores

    def _save_plot(self, figure, key_filter: list[str] = None):
        save_dir = f"results/{self.folder_name}"
        os.makedirs(save_dir, exist_ok=True)
        filename = self._make_plot_filename(key_filter)

        filepath = os.path.join(save_dir, filename)
        figure.savefig(filepath, dpi=500, bbox_inches='tight')

    def _make_plot_filename(self, key_filter: list[str] = None):
        plot_title = self._get_plot_title()
        plot_title = plot_title.replace(":", "").replace(" ", "_").replace("/", "_").lower()
        if key_filter:
            plot_title += f"_{'_'.join(map(lambda x: x.lower(), key_filter))}"
        return f"{plot_title}.png"

    def _configure_axes(self, axis):
        axis.set_xlabel(f"{self.section_type}", fontsize=12)
        axis.set_ylabel(f"{self.metrics_name.capitalize()}", fontsize=12)
        axis.set_title(self._get_plot_title(), fontsize=12, fontweight="bold")
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))
        axis.grid(True, alpha=0.3)
        axis.legend(loc="center left", bbox_to_anchor=(1, 0.5),
                    frameon=True, fontsize=9)

    def _get_plot_title(self):
        return f"{self.metrics_name.capitalize()} per {self.section_type.capitalize()}"

    @staticmethod
    def _plot_key_line(axis, sections: list[int], key: str,
                             color: str, scores: list[float]):
        axis.plot(sections, scores, marker="o", label=key,
                  color=color, linewidth=1, markersize=6)

    @staticmethod
    def _plot_trend_line(axis, sections: list[int], scores: list[float], color: str):
        if len(sections) <= 2:
            return

        polynomial_coefficients = np.polyfit(sections, scores, 2)
        polynomial_function = np.poly1d(polynomial_coefficients)

        smooth_x_values = np.linspace(sections[0], sections[-1], 100)
        smooth_y_values = polynomial_function(smooth_x_values)

        axis.plot(smooth_x_values, smooth_y_values, linestyle="--",
                  color=color, linewidth=1.5, alpha=0.7)
