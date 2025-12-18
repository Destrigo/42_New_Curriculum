from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import List
from datetime import datetime
from enum import Enum


class Rank(str, Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: List[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def validate_mission(self):
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        if not any(member.rank in {"commander", "captain"}
                   for member in self.crew):
            raise ValueError("Mission must have at "
                             "least one Commander or Captain")

        if self.duration_days > 365:
            experienced_count = sum(1 for member
                                    in self.crew
                                    if member.years_experience >= 5)
            if experienced_count < len(self.crew)/2:
                raise ValueError("Long missions (>365 days)"
                                 "require 50% experienced crew (5+ years)")

        if not all(member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")
        return self


if __name__ == "__main__":
    print("Space Mission Crew Validation")
    print("="*40)

    try:
        crew_list = [
            CrewMember(member_id="CM01", name="Sarah Connor",
                       rank="commander", age=40,
                       specialization="Mission Command", years_experience=15),
            CrewMember(member_id="CM02", name="John Smith",
                       rank="lieutenant", age=35,
                       specialization="Navigation", years_experience=6),
            CrewMember(member_id="CM03", name="Alice Johnson",
                       rank="officer", age=30,
                       specialization="Engineering", years_experience=7),
        ]
        valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date="2025-12-13T08:00:00",
            duration_days=900,
            crew=crew_list,
            budget_millions=2500.0
        )

        print("Valid mission created:")
        print(f"Mission: {valid_mission.mission_name}")
        print(f"ID: {valid_mission.mission_id}")
        print(f"Destination: {valid_mission.destination}")
        print(f"Duration: {valid_mission.duration_days} days")
        print(f"Budget: ${valid_mission.budget_millions}M")
        print(f"Crew size: {len(valid_mission.crew)}")
        print("Crew members:")
        for member in valid_mission.crew:
            print(f"- {member.name} ({member.rank}) - {member.specialization}")
        print("="*40)

    except ValidationError as e:
        print(e)

    try:
        crew_list_invalid = [
            CrewMember(member_id="CM04", name="Tom Hanks", rank="officer",
                       age=38, specialization="Engineering",
                       years_experience=4),
            CrewMember(member_id="CM05", name="Jane Doe", rank="lieutenant",
                       age=32, specialization="Navigation", years_experience=2)
        ]
        invalid_mission = SpaceMission(
            mission_id="M2024_TEST",
            mission_name="Test Mission",
            destination="Moon",
            launch_date="2025-12-13T08:00:00",
            duration_days=100,
            crew=crew_list_invalid,
            budget_millions=500.0
        )
        invalid_mission is None
    except ValidationError as e:
        print("Expected validation error:")
        print(e)
