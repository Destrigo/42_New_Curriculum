def artifact_sorter(artifacts: list[dict]) -> list[dict]:
    return sorted(artifacts, key=lambda x: x['power'], reverse=True)


def power_filter(mages: list[dict], min_power: int) -> list[dict]:
    return list(filter(lambda mage: mage['power'] >= min_power, mages))


def spell_transformer(spells: list[str]) -> list[str]:
    return list(map(lambda spell: f"* {spell} *", spells))


def mage_stats(mages: list[dict]) -> dict:
    if not mages:
        return {'max_power': 0, 'min_power': 0, 'avg_power': 0.0}
    powers = list(map(lambda m: m['power'], mages))
    max_power = max(powers)
    min_power = min(powers)
    avg_power = round(sum(powers) / len(powers), 2)
    return {'max_power': max_power,
            'min_power': min_power,
            'avg_power': avg_power}


if __name__ == "__main__":
    """test"""
    artifacts = [
        {'name': 'Amulet of Fire', 'power': 75, 'type': 'amulet'},
        {'name': 'Sword of Shadows', 'power': 90, 'type': 'weapon'},
        {'name': 'Ring of Light', 'power': 60, 'type': 'ring'}
    ]
    sorted_artifacts = artifact_sorter(artifacts)
    print(sorted_artifacts)
    print("")

    mages = [
        {'name': 'Gandalf', 'power': 95, 'element': 'fire'},
        {'name': 'Merlin', 'power': 80, 'element': 'air'},
        {'name': 'Morgana', 'power': 65, 'element': 'dark'}
    ]
    strong_mages = power_filter(mages, 80)
    print(strong_mages)
    print("")

    spells = ['Fireball', 'Ice Lance', 'Lightning Bolt']
    transformed_spells = spell_transformer(spells)
    print(transformed_spells)
    print("")

    stats = mage_stats(mages)
    print(stats)
