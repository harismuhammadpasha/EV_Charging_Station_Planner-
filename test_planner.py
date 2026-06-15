"""Unit tests for the EV Charging Station Planner."""

import networkx as nx
import pytest

from models import Vehicle, ChargingStation
from route_planner import RoutePlanner


@pytest.fixture
def simple_graph():
    g = nx.Graph()
    edges = [
        ('A', 'B', 50),
        ('B', 'C', 50),
        ('A', 'C', 150),
    ]
    for u, v, w in edges:
        g.add_edge(u, v, weight=w)
    return g


@pytest.fixture
def planner(simple_graph):
    stations = {'B': ChargingStation(name='B', cost_per_kwh=30)}
    return RoutePlanner(simple_graph, stations)


def test_shortest_path_basic(planner):
    dist, path = planner.shortest_path('A', 'C')
    assert dist == 100
    assert path == ['A', 'B', 'C']


def test_ev_aware_route_within_battery(planner):
    vehicle = Vehicle(name="EV", battery_capacity_km=60, kwh_per_km=0.2)
    result = planner.ev_aware_route('A', 'C', vehicle)
    assert result.is_feasible
    assert result.path == ['A', 'B', 'C']
    assert 'B' in result.charging_stops


def test_ev_aware_route_infeasible(planner):
    vehicle = Vehicle(name="EV", battery_capacity_km=40, kwh_per_km=0.2)
    result = planner.ev_aware_route('A', 'C', vehicle)
    assert not result.is_feasible


def test_vehicle_battery_consumption():
    vehicle = Vehicle(name="EV", battery_capacity_km=100, kwh_per_km=0.2)
    assert vehicle.consume(30) is True
    assert vehicle.current_battery_km == 70
    assert vehicle.consume(80) is False


def test_charging_cost_calculation():
    station = ChargingStation(name='B', cost_per_kwh=30)
    cost = station.full_charge_cost(battery_capacity_km=100, kwh_per_km=0.2)
    assert cost == 600


def test_validate_nodes(planner):
    assert planner.validate_nodes('A', 'B', 'C') is True
    assert planner.validate_nodes('A', 'X') is False