from alchemy.elements import create_fire, create_earth


def lead_to_gold():
    fire_result = create_fire()
    return f"Lead transmuted to gold using {fire_result}"


def stone_to_gem():
    earth_result = create_earth()
    return f"Stone transmuted to gem using {earth_result}"
