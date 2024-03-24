from enum import Enum

class ShipStatus(Enum):
    SAIL = 0
    LOADING = 1
    DISCHARGING = 2
    DOCK = 3
    IDLE = 4
    UNKNOWN = 5

class CargoAction(Enum):
    NONE = 0
    LOADING = 1
    DISCHARGING = 2
    FINISH = 3
    UNKNOWN = 4

