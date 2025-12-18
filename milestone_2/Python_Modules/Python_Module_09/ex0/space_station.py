from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from datetime import datetime


class SpaceStation(BaseModel):
    station_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    crew_size: int = Field(..., ge=1, le=20)
    power_level: float = Field(..., ge=0.0, le=100.0)
    oxygen_level: float = Field(..., ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: Optional[str] = Field(None, max_length=200)


if __name__ == "__main__":
    print("Space Station Data Validation")
    print("="*40)

    try:
        valid_station = SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=6,
            power_level=85.5,
            oxygen_level=92.3,
            last_maintenance="2025-12-13T10:00:00",
            notes="Main research station."
        )
        print("Valid station created:")
        print(f"ID: {valid_station.station_id}")
        print(f"Name: {valid_station.name}")
        print(f"Crew: {valid_station.crew_size} people")
        print(f"Power: {valid_station.power_level}%")
        print(f"Oxygen: {valid_station.oxygen_level}%")
        if valid_station.is_operational:
            print("Status: 'Operational'")
        else:
            print("Status: 'Not operational'")
        print("="*40)
    except ValidationError as e:
        print("Validation error:", e)

    try:
        invalid_station = SpaceStation(
            station_id="BAD001",
            name="Overcrowded Station",
            crew_size=25,  # invalid
            power_level=50.0,
            oxygen_level=50.0,
            last_maintenance=datetime.now()
        )
        invalid_station is None
    except ValidationError as e:
        print("Expected validation error:")
        print(e)
