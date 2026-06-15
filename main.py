"""EV Charging Station Planner - CLI entry point."""

import logging
import networkx as nx

from config import (
    CITY_EDGES, CHARGING_STATIONS, BATTERY_CAPACITY_KM,
    KWH_PER_KM, CHARGING_COST_PER_KWH, LOW_BATTERY_THRESHOLD_PCT
)
from models import Vehicle, ChargingStation
from route_planner import RoutePlanner
from visualizer import MapVisualizer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def build_graph() -> nx.Graph:
    graph = nx.Graph()
    for u, v, w in CITY_EDGES:
        graph.add_edge(u, v, weight=w)
    return graph


def build_charging_stations() -> dict:
    return {name: ChargingStation(name=name, cost_per_kwh=CHARGING_COST_PER_KWH)
            for name in CHARGING_STATIONS}


def get_battery_range() -> float:
    raw = input(f"Enter your EV's battery range in km (default {BATTERY_CAPACITY_KM}): ").strip()
    if not raw:
        return BATTERY_CAPACITY_KM
    try:
        value = float(raw)
        if value <= 0:
            print("Battery range must be positive. Using default.")
            return BATTERY_CAPACITY_KM
        return value
    except ValueError:
        print("Invalid number. Using default.")
        return BATTERY_CAPACITY_KM


def print_result(result, plain_distance, plain_path, vehicle, planner):
    print("\n" + "=" * 50)
    print(f"  Route: {result.start} -> {result.end}")
    print("=" * 50)

    print("\n  -- Normal Dijkstra (no battery limit) --")
    print(f"  Path     : {' -> '.join(plain_path) if plain_path else 'N/A'}")
    print(f"  Distance : {plain_distance} km")

    print("\n  -- EV-Aware Route (battery + charging) --")
    if not result.is_feasible:
        print("  No feasible path found within battery range!")
        print("=" * 50)
        return

    print(f"  Path     : {' -> '.join(result.path)}")
    print(f"  Distance : {result.distance_km} km")

    battery_pct = (result.final_battery_km / vehicle.battery_capacity_km) * 100
    print(f"  Battery Remaining at Destination : {result.final_battery_km} km ({battery_pct:.1f}%)")

    if battery_pct < LOW_BATTERY_THRESHOLD_PCT:
        print("  WARNING: Battery low at arrival! Consider an extra charging stop.")

    if result.charging_stops:
        cost = planner.estimate_charging_cost(result, vehicle)
        print(f"  Charging Stops : {', '.join(result.charging_stops)}")
        print(f"  Number of Stops : {len(result.charging_stops)}")
        print(f"  Estimated Charging Cost : Rs. {cost:.0f}")
    else:
        print("  Charging Stops : None needed")
        print("  Number of Stops : 0")
        print("  Estimated Charging Cost : Rs. 0")

    if result.distance_km > plain_distance:
        diff = result.distance_km - plain_distance
        print(f"\n  Note: EV path is {diff} km longer than the absolute shortest route,")
        print("  because the direct route exceeds battery range.")
    else:
        print("\n  Note: EV path matches the absolute shortest route - no detour needed.")

    print("=" * 50)


def get_valid_node(prompt: str, graph: nx.Graph) -> str:
    while True:
        value = input(prompt).strip().upper()
        if value in graph.nodes:
            return value
        print(f"Invalid city! Choose from: {', '.join(sorted(graph.nodes))}")


def run_route_query(planner: RoutePlanner, graph: nx.Graph, visualizer: MapVisualizer):
    start = get_valid_node("Enter Start City: ", graph)
    end = get_valid_node("Enter Destination City: ", graph)
    battery_range = get_battery_range()

    vehicle = Vehicle(name="My EV", battery_capacity_km=battery_range, kwh_per_km=KWH_PER_KM)

    plain_distance, plain_path = planner.shortest_path(start, end)
    result = planner.ev_aware_route(start, end, vehicle)

    print_result(result, plain_distance, plain_path, vehicle, planner)

    if result.is_feasible:
        visualizer.show_route(start, end, result.path, result.distance_km)


def run_mst_view(planner: RoutePlanner, visualizer: MapVisualizer):
    mst, total_cost = planner.minimum_spanning_network()

    print("\n" + "=" * 50)
    print("  Minimum Spanning Network (Prim's Algorithm)")
    print("=" * 50)
    print(f"  Total Network Cost : {total_cost} km")
    print("  Connections:")
    for u, v, data in mst.edges(data=True):
        print(f"    {u} -- {v}  ({data['weight']} km)")
    print("=" * 50)

    visualizer.show_mst(mst, total_cost)


def list_cities(graph: nx.Graph, charging_stations: set):
    print("\nAvailable Cities:")
    for city in sorted(graph.nodes):
        marker = " (Charging Station)" if city in charging_stations else ""
        print(f"  - {city}{marker}")


def main():
    graph = build_graph()
    charging_stations = build_charging_stations()
    planner = RoutePlanner(graph, charging_stations)
    visualizer = MapVisualizer(graph, set(charging_stations.keys()))

    print("=" * 50)
    print("  EV Charging Station Planner")
    print("=" * 50)
    print(f"Default Battery Capacity : {BATTERY_CAPACITY_KM} km")
    print(f"Charging Stations        : {', '.join(charging_stations.keys())}")

    while True:
        print("\nMenu:")
        print("  1. Plan a route (Dijkstra + Battery-Aware)")
        print("  2. View Minimum Spanning Network (Prim's Algorithm)")
        print("  3. List all cities")
        print("  4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            run_route_query(planner, graph, visualizer)
        elif choice == "2":
            run_mst_view(planner, visualizer)
        elif choice == "3":
            list_cities(graph, set(charging_stations.keys()))
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()