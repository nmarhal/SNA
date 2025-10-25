import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

class CentralityProgressionPlotter:
    def __init__(self, centrality_name: str, section_type: str):
        self.centrality_name = centrality_name
        self.section_type = section_type
        self.data_points = []
        self.all_characters = set()

        self.colors = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
            "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
            "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
        ]

    def add_data_point(self, character_centralities: dict):
        self.data_points.append(character_centralities)
        self.all_characters.update(character_centralities.keys())

    def draw(self, character_filter: list[str] = None, trend_lines: list[str] = None):
        if not self.data_points:
            print("No data to plot")
            return

        figure, axis = plt.subplots(figsize=(12, 6))
        sections = list(range(1, len(self.data_points) + 1))

        character_list = self._filter_characters(character_filter)
        if not character_list:
            print("No matching characters found in the dataset")
            return

        characters_with_trends = set()
        if trend_lines:
            characters_with_trends = {char.lower() for char in trend_lines
                                      if char.lower() in self.all_characters}

        for index, character in enumerate(character_list):
            color = self.colors[index % len(self.colors)]
            scores = self._get_character_scores(character)

            self._plot_character_line(axis, sections, character, color, scores)

            if character.lower() in characters_with_trends:
                self._plot_trend_line(axis, sections, scores, color)

        self._configure_axes(axis)
        plt.tight_layout()
        plt.show()

    def _filter_characters(self, character_filter: list[str] = None) -> list[str]:
        if character_filter:
            filtered = [char for char in character_filter if char.lower() in self.all_characters]
            return sorted(filtered)
        return sorted(self.all_characters)

    def _get_character_scores(self, character: str) -> list[float]:
        scores = []
        for data_point in self.data_points:
            scores.append(data_point.get(character, 0))
        return scores

    @staticmethod
    def _plot_character_line(axis, sections: list[int], character: str,
                             color: str, scores: list[float]):
        axis.plot(sections, scores, marker="o", label=character,
                  color=color, linewidth=2, markersize=6)

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

    def _configure_axes(self, axis):
        axis.set_xlabel(f"{self.section_type}", fontsize=12)
        axis.set_ylabel(f"{self.centrality_name.capitalize()} Score", fontsize=12)
        axis.set_title(f"{self.centrality_name.capitalize()} Progression",
                       fontsize=14, fontweight="bold")
        axis.xaxis.set_major_locator(MaxNLocator(integer=True))
        axis.grid(True, alpha=0.3)
        axis.legend(loc="center left", bbox_to_anchor=(1, 0.5),
                    frameon=True, fontsize=9)
