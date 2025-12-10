def record_spell(spell_name: str, ingredients: str) -> str:
    """Late import"""
    from .validator import validate_ingredients
    validation = validate_ingredients(ingredients)

    if validation.endswith("VALID"):
        return f"Spell recorded: {spell_name} ({validation})"
    return f"Spell rejected: {spell_name} ({validation})"
