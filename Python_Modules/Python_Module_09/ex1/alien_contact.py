from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional
from datetime import datetime
from enum import Enum


class ContactType(str, Enum):
    radio = "radio"
    visual = "visual"
    physical = "physical"
    telepathic = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: Optional[str] = Field(None, max_length=500)
    is_verified: bool = False

    @model_validator(mode='after')
    def check_business_rules(cls, values):
        contact_type = values.contact_type
        contact_id = values.contact_id
        witness_count = values.witness_count
        signal_strength = values.signal_strength
        message_received = values.message_received
        is_verified = values.is_verified

        if not contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")
        if contact_type == ContactType.physical and not is_verified:
            raise ValueError("Physical contact "
                             "reports must be verified")
        if contact_type == ContactType.telepathic and witness_count < 3:
            raise ValueError("Telepathic contact "
                             "requires at least 3 witnesses")
        if signal_strength > 7.0 and not message_received:
            raise ValueError("Strong signals (>7.0) must "
                             "include a received message")
        return values

    def print_info(self) -> None:
        print("Valid contact report:")
        print(f"ID: {self.contact_id}")
        print(f"Type: {self.contact_type}")
        print(f"Location: {self.location}")
        print(f"Signal: {self.signal_strength}/10")
        print(f"Duration: {self.duration_minutes} minutes")
        print(f"Witnesses: {self.witness_count}")
        print(f"Message: {self.message_received}")


def main():
    print("Alien Contact Log Validation")
    print("="*40)

    try:
        valid_contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp="2025-12-13T12:00:00",
            location="Area 51, Nevada",
            contact_type="radio",
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli",
            is_verified=True
        )
        valid_contact.print_info()
    except ValidationError as e:
        print(e)

    try:
        invalid_contact = AlienContact(
            contact_id="AC_2024_002",
            timestamp="2025-12-13T12:00:00",
            location="Mars Base",
            contact_type="telepathic",
            signal_strength=5.0,
            duration_minutes=30,
            witness_count=1  # error
        )
        return invalid_contact is None
    except ValidationError as e:
        print("\nExpected validation error:")
        print(e)
