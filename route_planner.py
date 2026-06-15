"""Routing logic: Dijkstra (plain) and EV-aware Dijkstra (battery-constrained)."""

import heapq
import logging
from typing import Dict, List, Tuple

import networkx as nx

from models import RouteResult, Vehicle, ChargingStation

logger = logging.getLogger(__name__)


class RoutePlanner:
    """Plans routes for an EV across a city graph, considering battery range
    and charging station placement."""

    def __init__(self, graph: nx.Graph, charging_stations: Dict[str, ChargingStation]):
        self.graph = graph
        self.charging_stations = charging_stations

    def validate_nodes(self, *nodes: str) -> bool:
        return all(node in self.graph.nodes for node in nodes)

    def shortest_path(self, start: str, end: str) -> Tuple[float, List[str]]:
        pq = [(0.0, start, [start])]
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)

            if node == end:
                return cost, path

            for neighbor, data in self.graph[node].items():
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + data['weight'], neighbor, path + [neighbor]))

        logger.warning("No path found between %s and %s", start, end)
        return float('inf'), []

    def ev_aware_route(self, start: str, end: str, vehicle: Vehicle) -> RouteResult:
        capacity = vehicle.battery_capacity_km
        pq = [(0.0, capacity, start, [start])]
        visited: Dict[Tuple[str, float], float] = {}

        while pq:
            cost, battery, node, path = heapq.heappop(pq)
            state = (node, battery)

            if state in visited:
                continue
            visited[state] = cost

            if node == end:
                stops = [n for n in path if n in self.charging_stations]
                return RouteResult(
                    start=start, end=end, path=path,
                    distance_km=cost, final_battery_km=battery,
                    charging_stops=stops, is_feasible=True
                )

            for neighbor, data in self.graph[node].items():
                edge_dist = data['weight']
                if edge_dist > battery:
                    continue

                new_battery = battery - edge_dist
                if neighbor in self.charging_stations:
                    new_battery = capacity

                heapq.heappush(pq, (cost + edge_dist, new_battery, neighbor, path + [neighbor]))

        logger.warning("No feasible EV route found between %s and %s within battery range", start, end)
        return RouteResult(start=start, end=end, path=[], distance_km=float('inf'), is_feasible=False)

    def estimate_charging_cost(self, result: RouteResult, vehicle: Vehicle) -> float:
        total = 0.0
        for stop_name in result.charging_stops:
            station = self.charging_stations[stop_name]
            total += station.full_charge_cost(vehicle.battery_capacity_km, vehicle.kwh_per_km)
        return total

    def minimum_spanning_network(self):
        """Prim's Algorithm: Minimum Spanning Tree connecting all cities
        and charging stations with minimum total road length."""
        mst = nx.minimum_spanning_tree(self.graph, algorithm='prim', weight='weight')
        total_cost = sum(data['weight'] for _, _, data in mst.edges(data=True))
        return mst, total_cost