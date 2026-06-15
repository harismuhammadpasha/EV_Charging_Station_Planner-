"""Visualization helpers for displaying the route on a map."""

import matplotlib.pyplot as plt
import networkx as nx
from typing import List


class MapVisualizer:
    """Draws the city graph and highlights a given route."""

    def __init__(self, graph: nx.Graph, charging_stations: set, seed: int = 42):
        self.graph = graph
        self.charging_stations = charging_stations
        self.pos = nx.spring_layout(graph, seed=seed)
        self.labels = nx.get_edge_attributes(graph, 'weight')

    def _node_colors(self) -> List[str]:
        return ['green' if n in self.charging_stations else 'skyblue' for n in self.graph.nodes()]

    def show_route(self, start: str, end: str, path: List[str], distance: float):
        path_edges = list(zip(path, path[1:]))

        def is_path_edge(u, v):
            return (u, v) in path_edges or (v, u) in path_edges

        edge_colors = ['red' if is_path_edge(u, v) else 'gray' for u, v in self.graph.edges()]
        edge_widths = [3 if is_path_edge(u, v) else 1 for u, v in self.graph.edges()]

        plt.figure(figsize=(9, 7))
        nx.draw(
            self.graph, self.pos, with_labels=True,
            node_color=self._node_colors(), node_size=800, font_size=11,
            edge_color=edge_colors, width=edge_widths
        )
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=self.labels, font_size=8)
        plt.title(f"{start} -> {end} | EV Path: {' -> '.join(path)} | Distance: {distance} km")
        plt.show()

    def show_mst(self, mst_graph, total_cost: float):
        plt.figure(figsize=(9, 7))
        nx.draw(
            self.graph, self.pos, with_labels=True,
            node_color=self._node_colors(), node_size=800, font_size=11,
            edge_color='lightgray', width=1
        )
        nx.draw_networkx_edges(mst_graph, self.pos, edge_color='blue', width=3)
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=self.labels, font_size=8)
        plt.title(f"Minimum Spanning Network (Prim's Algorithm) | Total Cost: {total_cost} km")
        plt.show()