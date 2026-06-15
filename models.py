"""Domain models for the EV Charging Station Planner."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ChargingStation:
    """Represents an EV charging station located at a city."""
    name: str
    cost_per_kwh: float

    def full_charge_cost(self, battery_capacity_km: float, kwh_per_km: float) -> float:
        energy_needed = battery_capacity_km * kwh_per_km
        return energy_needed * self.cost_per_kwh


@dataclass
class Vehicle:
    """Represents an Electric Vehicle with battery constraints."""
    name: str
    battery_capacity_km: float
    kwh_per_km: float
    current_battery_km: float = field(init=False)

    def __post_init__(self):
        self.current_battery_km = self.battery_capacity_km

    def battery_percent(self) -> float:
        return (self.current_battery_km / self.battery_capacity_km) * 100

    def is_low_battery(self, threshold_pct: float) -> bool:
        return self.battery_percent() < threshold_pct

    def consume(self, distance_km: float) -> bool:
        if distance_km > self.current_battery_km:
            return False
        self.current_battery_km -= distance_km
        return True

    def recharge_full(self):
        self.current_battery_km = self.battery_capacity_km


@dataclass
class RouteResult:
    """Holds the result of a route calculation."""
    start: str
    end: str
    path: List[str]
    distance_km: float
    final_battery_km: float = 0.0
    charging_stops: List[str] = field(default_factory=list)
    is_feasible: bool = True